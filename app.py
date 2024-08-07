from fastapi import *
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from mysql.connector.pooling import MySQLConnectionPool
from passlib.context import CryptContext 
import time
from typing import Dict, Annotated
import jwt
from pydantic import BaseModel, Field, EmailStr
from fastapi.middleware.cors import CORSMiddleware
import httpx 
import uuid


dbconfig = {
    "host": "localhost",
    "user": "root",
    "password": "jmhg42thSQL!",
    "database": "daytrip"
}

cnxpool = MySQLConnectionPool(pool_name="mypool", pool_size=20, **dbconfig)


app=FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"],   
)

bcrypt_context =CryptContext(schemes =["bcrypt"], deprecated="auto")
JWT_SECRET = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
JWT_ALGORITHM = "HS256"	

# Static Pages (Never Modify Code in this Block)
@app.get("/", include_in_schema=False)
async def index(request: Request):
	return FileResponse("./static/index.html", media_type="text/html")
@app.get("/attraction/{id}", include_in_schema=False)
async def attraction(request: Request, id: int):
	return FileResponse("./static/attraction.html", media_type="text/html")
@app.get("/booking", include_in_schema=False)
async def booking(request: Request):
	return FileResponse("./static/booking.html", media_type="text/html")
@app.get("/thankyou", include_in_schema=False)
async def thankyou(request: Request):
	return FileResponse("./static/thankyou.html", media_type="text/html")


class UserLogIn(BaseModel):
	email:str
	password:str

class UserSignup(BaseModel):
	name:str
	email:str
	password:str

def token_response(token: str):
    return {
        "token": token
    }

def signJWT(id: str, name:str, email:str) -> Dict[str, str]:
    payload = {
		"id":id,
        "name": name,
		"email":email,
        "exp": time.time() + 604800 #expire in 7 days
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

    return token_response(token)


def get_password_hash(password):
	return bcrypt_context.hash(password)

def verify_password(plain_password, hash_password):
	return bcrypt_context.verify(plain_password,hash_password)


 #("CREATE TABLE booking (id BIGINT PRIMARY KEY AUTO_INCREMENT, attractionId BIGINT NOT NULL, date DATE NOT NULL, time VARCHAR(255) NOT NULL, price BIGINT NOT NULL)")
class CreateBooking(BaseModel):
	attractionId:int
	date:str
	time:str
	price:int



def decodeJWT(request: Request):
    token = request.headers.get('Authorization')

    if token:
        try:
            token = token.replace('Bearer ', '')
            decoded_jwt = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            return decoded_jwt
        except jwt.ExpiredSignatureError:
            return JSONResponse(status_code=400, content={"error": True, "message": "Token expired"})
        except jwt.InvalidTokenError:
            return JSONResponse(status_code=400, content={"error": True, "message": "Invalid Token"})
    else:
        return JSONResponse(status_code=403, content={"error": True, "message": "未登入系統，拒絕存取"})
	
class Attraction(BaseModel):
	id: int
	name: str
	address: str
	image: str

class Contact(BaseModel):
	name:Annotated[str, Field(min_length=1)]
	email:EmailStr
	phone:Annotated[str, Field(min_length=1)]

class Trip(BaseModel):
	attraction:Attraction 
	date: str
	time: str

class Order(BaseModel):
	price:int
	trip:Trip
	contact:Contact

class CreateOrder(BaseModel):
	prime:str
	order:Order 

partner_key = "partner_oezzdurEpgu3bm5xrrUOYCExjsUHWQqb9nfhK7Yt5t1gIsdh38sk62sX"
merchant_id = "tppf_twkclaire_GP_POS_2"

@app.post("/api/orders")
async def create_order(order: CreateOrder, token=Depends(decodeJWT)):
    if isinstance(token, JSONResponse):
        return token
    userID = token["id"]

    if order:
        userId = userID
        order_number = str(uuid.uuid4())
        prime = order.prime
        price = order.order.price
        attractionId = order.order.trip.attraction.id
        attractionName = order.order.trip.attraction.name
        attractionAddress = order.order.trip.attraction.address
        attractionImage = order.order.trip.attraction.image
        date = order.order.trip.date
        time = order.order.trip.time
        name = order.order.contact.name
        email = order.order.contact.email
        phone = order.order.contact.phone
        status = 1  # 1 means unpaid

        try:
            # Add order record to database before payment is executed
            db = cnxpool.get_connection()
            mycursor = db.cursor()
            sql = """
            INSERT INTO orderlist 
            (userId, orderNumber, price, attractionId, attractionName, attractionAddress, attractionImage, date, time, name, email, phone, status) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            val = (
                userId, order_number, price, attractionId, attractionName,
                attractionAddress, attractionImage, date, time, name, email, phone, status
            )
            mycursor.execute(sql, val)
            db.commit()

            # Construct data sent to tappay
            payment_data = {
                "prime": prime,
                "partner_key": partner_key,
                "merchant_id": merchant_id,
                "amount": price,
                "currency": "TWD",
                "order_number": order_number,
                "details": "test",
                "cardholder": {
                    "phone_number": phone,
                    "name": name,
                    "email": email
                },
            }

            # Paid by prime
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://sandbox.tappaysdk.com/tpc/payment/pay-by-prime",
                    json=payment_data,
                    headers={
                        "Content-Type": "application/json",
                        "x-api-key": partner_key
                    }
                )
                # trying to get the status so I can log success/failed message
                if response:
                    data = response.json()
                    status = data.get("status")
                    msg = data.get("msg")

                    # print(status, msg)
                    if status == 0:  # update payment status to 0, meaning paid
                        sql = "UPDATE orderlist SET status=0 WHERE orderNumber=%s"
                        val = (order_number,)
                        mycursor.execute(sql, val)
                        db.commit()

                        sql = "DELETE FROM booking WHERE userId=%s"  # delete the booking history in boooking table by unique id userId
                        sql_data = (userId,)
                        mycursor.execute(sql, sql_data)
                        db.commit()

                        return {
                            "data": {
                                "number": order_number,
                                "payment": {
                                    "status": 0,
                                    "message": "付款成功"
                                }
                            }
                        }
                    else: #order is created but payment is not through, this is a 200 respond.
                        return {
                            "data": {
                                "number": order_number,
                                "payment": {
                                    "status": 1,
                                    "message": "付款失敗"
                                }
                            }
                        }


        except Exception:
         return JSONResponse(
				status_code=500, 
				content={"error":True, "message":"伺服器內部錯誤"}
				)
        finally:
            mycursor.close()
            db.close()





@app.get("/api/orders/{orderNumber}")
async def getOrderNumber(orderNumber: str, token=Depends(decodeJWT)):
    if isinstance(token, JSONResponse):
        return token
    userID = token["id"]

    if orderNumber:
        try:
            print(orderNumber)
            db = cnxpool.get_connection()
            mycursor = db.cursor()
            sql = "SELECT * FROM orderlist WHERE orderNumber=%s and userId= %s"
            val = (orderNumber.strip(), userID)
            mycursor.execute(sql, val)
            result = mycursor.fetchone()
            if result:
                # print(result)
                return {
                    "data": {
                        "number": result[2],
                        "price": result[3],
                        "trip": {
                            "attraction": {
                                "id": result[4],
                                "name": result[5],
                                "address": result[6],
                                "image": result[7],
                            },
                            "date": result[8],
                            "time": result[9],
                        },
                        "contact": {
                            "name": result[10],
                            "email": result[11],
                            "phone": result[12],
                        },
                        "status": result[13],
                    }
                }
        except Exception as e:
            # Handle the exception, e.g., logging or returning an error response
            return {"ok": False, "error": str(e)}
        finally:
            mycursor.close()
            db.close()




            



@app.post("/api/booking")
async def booking(booking:CreateBooking, token =Depends(decodeJWT)): #make sure one account can only have one booking. if booking existed, use alter syntax for sql
	if isinstance(token, JSONResponse):
		return token
	# print(token)
	if booking:
		try:
			db =cnxpool.get_connection()
			mycursor = db.cursor()
			sql=("SELECT * FROM booking WHERE userId = %s")
			val=(token["id"],)
			mycursor.execute(sql,val)
			result=mycursor.fetchone()
			if result:
				sql = "UPDATE booking SET attractionId=%s, date=%s, time=%s, price=%s WHERE userId=%s"
				val = (booking.attractionId, booking.date, booking.time, booking.price,token["id"])
			else: 
				sql = "INSERT INTO booking (userId, attractionId, date, time, price) VALUES (%s, %s, %s, %s,%s)"
				val = (token["id"],booking.attractionId, booking.date, booking.time, booking.price)
			mycursor.execute(sql, val)
			db.commit()
			return {"ok":True}
		except Exception:
			return JSONResponse(
				status_code=500, 
				content={"error":True, "message":"伺服器內部錯誤"}
				)
		finally:
			db.close()
	else:
		raise HTTPException(status_code=400, detail="Invalid booking details")	


				


@app.delete("/api/booking")
async def deletebooking(token =Depends(decodeJWT)):
	if isinstance(token, JSONResponse):
		return token
	userId=token["id"]
	try:
		db =cnxpool.get_connection()
		mycursor = db.cursor()
		sql="DELETE FROM booking WHERE userId=%s"
		sql_data=(userId,)
		mycursor.execute(sql,sql_data)
		db.commit()
		return {"ok":True}
	except Exception:
		return JSONResponse(
			status_code=500, 
			content={"error":True, "message":"伺服器內部錯誤"}
			)	
	finally:
		db.close()

@app.get("/api/booking")
async def getbooking(token =Depends(decodeJWT)):
	if isinstance(token, JSONResponse):
		return token
	userId=token["id"]
	# print(token) 
	try:
		db =cnxpool.get_connection()
		mycursor = db.cursor()
		sql="SELECT * FROM attractions INNER JOIN booking on attractions.id = booking.attractionId WHERE userId=%s"
		sql_data=(userId,)
		mycursor.execute(sql,sql_data)
		result=mycursor.fetchone()
		if result is None:
			return{"data":None}
		else:
			return {
				"data": {
					"attraction": {
					"id": result[0],
					"name": result[1],
					"address": result[4],
					"image": result[9].split(",")[0],
					},
					"date": result[13],
					"time": result[14],
					"price": result[15]
				}
				}
	except Exception:
		return JSONResponse(
			status_code=500, 
			content={"error":True, "message":"伺服器內部錯誤"}
			)	
	finally:
		db.close()

			

@app.get("/api/user/auth")
async def getUser(token:dict =Depends(decodeJWT)):
	if isinstance(token, JSONResponse):
		return token
	return { "data": dict(list(token.items())[0: 3]) } #Using slicing on dictionary item list so expiry date isn't included

			
#用戶註冊
@app.post("/api/user")
async def registerUser(user:UserSignup ):

	try: 
		db =cnxpool.get_connection()
		mycursor = db.cursor()
		mycursor.execute("SELECT * FROM member WHERE email = %s", (user.email,))
		existing_user = mycursor.fetchone()
		if existing_user:    
				return JSONResponse(
					status_code=400, 
					content={"error":True, "message":"Email已註冊"}
					)
		
		else:
			hash_password = get_password_hash(user.password)           
			sql = "INSERT INTO member (name, email, password) VALUES (%s, %s, %s)"
			val = (user.name, user.email, hash_password)
			mycursor.execute(sql, val)
			db.commit()
			return {"ok": True}
	except Exception:
		return JSONResponse(
			status_code=500, 
			content={"error":True, "message":"伺服器內部錯誤"}
			)
	finally:
		db.close()		




#用戶登入
@app.put("/api/user/auth")
async def login(user:UserLogIn):
		try: 
			db =cnxpool.get_connection()
			mycursor = db.cursor()
			sql="SELECT * FROM member WHERE email=%s"
			val=(user.email,)
			mycursor.execute(sql, val)
			existing_user = mycursor.fetchone()
			# print(existing_user)
			if existing_user:
					hash_password=existing_user[3]
					# print(hash_password)
					if verify_password(user.password, hash_password):
						id=existing_user[0]
						name=existing_user[1]
						email=existing_user[2]
						# print(verify_password)
						return signJWT(id,name,email)
					else:
						return JSONResponse(
							status_code=400, 
							content={"error":True, "message":"Email或密碼有誤"}
							) 
			else:
				return JSONResponse(
					status_code=400, 
					content={"error":True, "message":"Email或密碼有誤"}
					) 
		except Exception:
			return JSONResponse(
				status_code=500, 
				content={"error":True, "message":"伺服器內部錯誤"}
				)
		finally:
			db.close()		




@app.get("/api/attraction/{attractionId}")
async def get＿attractionId(attractionId:int):
	try:
		db = cnxpool.get_connection()
		mycursor = db.cursor()
		sql=("SELECT * FROM attractions WHERE id=%s")
		sql_data=(attractionId,)
		mycursor.execute(sql,sql_data)
		attraction=mycursor.fetchone()
		if attraction:
			info={
				"data":{
					"id": attraction[0],
					"name": attraction[1],
					"category": attraction[2],
					"description": attraction[3],
					"address": attraction[4],
					"transport": attraction[5],
					"mrt": attraction[6],
					"lat": attraction[7],
					"lng": attraction[8],
					"images":attraction[9].split(",")				

				}
			}
			return info
		else:  #if attractionId is wrong
			return JSONResponse(
				status_code=400,
				content={"error":True, "message":"景點編號不正確"}
			)		

	except Exception:
		return JSONResponse(

			status_code=500, 
			content={"error":True, "message":"伺服器內部錯誤"}
			)
	finally:
		db.close()





@app.get("/api/mrts")
async def get＿mrts():
	try:
		db = cnxpool.get_connection()
		mycursor = db.cursor()
		mycursor.execute("SELECT mrt FROM attractions GROUP BY mrt ORDER BY COUNT(id) DESC;")
		mrt_result=mycursor.fetchall()
		mrt_list=[]
		for mrt in mrt_result:
			if mrt[0]!= None:
				mrt_list.append(mrt[0])
		return {"data": mrt_list}
	except Exception:
		return JSONResponse(
			status_code=500, 
			content={"error":True, "message":"伺服器內部錯誤"}
			)
	finally:
		db.close()


@app.get("/api/attractions")
async def get＿attractions(page: int= Query(...,gt=-1), keyword:str | None = None):

	if page==0:
		start=0
	else:
		start =(page -1)* 12 +12

	try:
		db = cnxpool.get_connection()
		mycursor = db.cursor()
		if keyword is None:

			sql=("SELECT * FROM attractions ORDER BY id LIMIT 13 OFFSET %s")
			sql_data=(start,)
			mycursor.execute(sql,sql_data)
			all_attractions = mycursor.fetchall()
			num_result=len(all_attractions)

		else: 
			sql=("SELECT * FROM attractions WHERE name LIKE %s OR mrt = %s ORDER BY id LIMIT 13 OFFSET %s")
			sql_data=["%"+keyword+"%",keyword,start]
			mycursor.execute(sql,sql_data)
			all_attractions=mycursor.fetchall()
			num_result=len(all_attractions)

		result=[]
		for attraction in all_attractions:
				data={

					"id": attraction[0],
					"name": attraction[1],
					"category": attraction[2],
					"description": attraction[3],
					"address": attraction[4],
					"transport": attraction[5],
					"mrt": attraction[6],
					"lat": attraction[7],
					"lng": attraction[8],
					"images":attraction[9].split(",")				
				}

				result.append(data)
		if num_result == 13:	
			nextPage=page+1	
		else:
			nextPage=None
		return{"nextPage": nextPage, "data": result}
		
	except Exception:
		return JSONResponse(
			status_code=500, 
			content={"error":True, "message":"伺服器內部錯誤"}
			)
	finally:
		db.close()

#mycursor.execute("CREATE TABLE member (id BIGINT PRIMARY KEY AUTO_INCREMENT, name VARCHAR(255) NOT NULL, email VARCHAR(255) NOT NULL, password VARCHAR(255) NOT NULL)")
