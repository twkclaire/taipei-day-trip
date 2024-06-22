from fastapi import *
from fastapi.responses import FileResponse, JSONResponse
import mysql.connector
from fastapi.staticfiles import StaticFiles
from mysql.connector.pooling import MySQLConnectionPool
from passlib.context import CryptContext 
import time
from typing import Dict
import jwt
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware 


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



# class CreateBooking(BaseModel):
# 	attractionId:int
# 	date:str
# 	time:str
# 	price:int

# @app.post("api/booking")
# async def booking(booking:CreateBooking):
# 	if booking:
# 		try:
# 			db =cnxpool.get_connection()
# 			mycursor = db.cursor()
# 			sql = "INSERT INTO booking (attractionId, date, time, price) VALUES (%s, %s, %s,%s)"
# 			val = (CreateBooking.attractionId, CreateBooking.date, CreateBooking.time, CreateBooking.price)
# 			mycursor.execute(sql, val)
# 			db.commit()
# 			return {"ok":True}
# 		except Exception:
# 			return JSONResponse(
# 				status_code=500, 
# 				content={"error":True, "message":"伺服器內部錯誤"}
# 				)
# 		finally:
# 			db.close()		

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
			
#用戶資訊運回傳
@app.get("/api/user/auth")
async def getUser(request:Request):
	token = request.headers.get('Authorization')
	# print(token)
	if token:
		try:
			token = token.replace('Bearer ', '')
			# print("inside the if", token)
			decoded_jwt=jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
			# print(decoded_jwt)
			return { "data": dict(list(decoded_jwt.items())[0: 3]) } #Using slicing on dictionary item list so expiry date isn't included
		except jwt.ExpiredSignatureError:
			return JSONResponse(
				status_code=400,
				content={"error":True, "message":"Token has expired"}
			)
		except jwt.InvalidTokenError:
			return JSONResponse(
				status_code=400,
				content={"error":True, "message": "Invalid token"}
			)
	else:
		return{"Please:":"Sign in"}





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

