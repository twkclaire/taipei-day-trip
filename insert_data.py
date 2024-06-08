import json
import mysql.connector

#connect to sql use daytrip db
mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="jmhg42thSQL!",
  database="daytrip"
)

#create table assign id as primary key
mycursor = mydb.cursor()
mycursor.execute("""
    CREATE TABLE attractions (
        id BIGINT NOT NULL AUTO_INCREMENT,
        name VARCHAR(255) NOT NULL, 
        category VARCHAR(255), 
        description TEXT NOT NULL,
        address VARCHAR(255) NOT NULL,
        transport TEXT,
        mrt VARCHAR(255),
        lat DECIMAL(8,6) NOT NULL,
        lng DECIMAL(9,6) NOT NULL,
        images TEXT NOT NULL,
        PRIMARY KEY (id)
    )
""")

#connect to json file
src1 = "data/taipei-attractions.json"
with open(src1, "r", encoding="utf-8") as file:
    data = json.load(file)
    list = data["result"]["results"]

#selecting information to insert in sql
for item in list:
    imagelinks=item["file"].split("http")
    all_images =[]
    for image in imagelinks: # only select file names that contains jpg or png
        if image.lower().endswith('.jpg') or image.lower().endswith('.png') :
            url="http"+image
            all_images.append(url)
    images= ",".join(all_images) #convert list to string and seperate with a comma

    sql="INSERT INTO attractions (name, category, description, address, transport, mrt, lat, lng, images) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
    val= ( 
        item["name"], 
        item["CAT"], 
        item["description"], 
        item["address"],
        item["direction"], 
        item["MRT"], 
        item["latitude"], 
        item["longitude"],
        images
        )

    mycursor.execute(sql, val)
    mydb.commit()
