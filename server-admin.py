from flask_api import FlaskAPI
from flask import request, jsonify
from flask_cors import CORS, cross_origin
import json
import pymysql
import os
import uuid
import cloudinary

import time


cloudinary.config(
    cloud_name="green-life",
    api_key="348926172629471",
    api_secret="XEKkZ4VoA9IklXjpJeuNHqgWR3A"

)

app = FlaskAPI(__name__)
UPLOAD_FOLDER = 'static/upload'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
CORS(app)

# kết nối mysql
def connect_mysql():
    db = pymysql.connect(host='localhost', user="root", db='blog', password="")
    return db

@app.route('/post/getall')
def hello():
    if request.method == "GET":
        try:
            with db.cursor() as cursor:
                cursor.execute("SELECT * FROM posts")                
                result = cursor.fetchall()
        finally:
            return json.dumps([{"ip": data[0], "date_time": str(data[1]), "post_content": data[2], "post_status":data[3], "post_type": data[4], "post_like_count":data[5], "post_title": data[6]} for data in result])

@app.route('/post/insert',methods = ['POST'])
def insert():
    if request.method == 'POST':
        try:                   
            db = connect_mysql()
            cursor = db.cursor()
            cursor.execute("INSERT INTO posts(post_content,author_ID,post_title,post_image_ID,post_category_ID) VALUES(%s,%s,%s,%s,%s)",(request.get_json()["content"],request.get_json()["author_ID"],request.get_json()["title"],request.get_json()["img_ID"],request.get_json()["category_ID"]))
            db.commit()
        except Exception as e:                     
            print(e)
            return e
        finally:
            return json.dumps({"status" : 200 , "content" : "Thêm bài viết thành công"})

@app.route('/category/getall', methods = ['GET'])
def getall():
    try:
        db = connect_mysql()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM blog.category;")
        db.commit()
        result = cursor.fetchall()           
        return json.dumps([{"category_ID" : r[0], "category" : r[1]} for r in result])
    finally:
        cursor.close()
@app.route('/file/upload', methods=['POST', 'GET'])
def upload():
    if request.method == 'POST':
        try:
            files = request.files.getlist("file")
            for file in files:
                extension = os.path.splitext(file.filename)[1]
                path = os.path.join(app.config['UPLOAD_FOLDER'], str(uuid.uuid4()) + extension)                
                file.save(path)
                size = os.stat('./'+path).st_size
                db = connect_mysql()
                cursor = db.cursor()
                cursor.execute("insert into blog.image(size, src, type) value( %s, %s, %s)",(size,path,extension))                               
                db.commit()                    
                result = cursor.lastrowid
                return {"img_ID" : result}        

        except Exception as e:
            return e
        finally:
            cursor.close()


if __name__ == '__main__':
    app.run(debug=True, port=8001)
