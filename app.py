from fastapi import *
from fastapi.responses import FileResponse, JSONResponse
import mysql.connector
from fastapi.staticfiles import StaticFiles
from mysql.connector.pooling import MySQLConnectionPool


dbconfig = {
    "host": "localhost",
    "user": "root",
    "password": "jmhg42thSQL!",
    "database": "daytrip"
}

cnxpool = MySQLConnectionPool(pool_name="mypool", pool_size=20, **dbconfig)


app=FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

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



# def get_connection():
#     connection = pooling.MySQLConnectionPool(
#         pool_name = "python_pool",
#         pool_size = 20,
#         pool_reset_session = True,
#         host = 'localhost',
#         user = mysql_user,
#         password = mysql_pwd,
#         database = mysql_db
#         )
#     conn = connection.get_connection()
#     return conn

# from mysql.connector import pooling

# dbconfig = {
#     "host": "localhost",
#     "user": "root",
#     "password": "jmhg42thSQL!",
#     "database": "daytrip"
# }

# mydb_pool = pooling.MySQLConnectionPool(pool_name="mypool", pool_size=5, **dbconfig)
