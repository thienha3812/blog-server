from flask_api import FlaskAPI
from flask import request, jsonify
from flask_cors import CORS
import json
import pymysql
import time
import os
from dotenv import load_dotenv
from hashids import Hashids
load_dotenv()
app = FlaskAPI(__name__)
CORS(app)


def connect_mysql():
    db = pymysql.connect(host='localhost', user="root", db='blog', password="")
    return db

@app.route('/post/mostread', methods=['GET'])
def mostread():
    try:
        hashids = Hashids(min_length=12)
        db = connect_mysql()
        cursor = db.cursor()
        base_url = os.getenv("BASE_URL")
        cursor.execute("""SELECT posts.create_at,posts.post_title,CONCAT(%s,image.src) as image_src,posts.post_ID,category.category FROM posts 
                            INNER JOIN image on image.img_ID = posts.post_image_ID 
                            INNER JOIN category on category.category_ID = posts.post_category_ID
                            ORDER BY post_view desc limit 4 
                            """,(base_url))
        db.commit()        
        result = cursor.fetchall()
        return json.dumps([{"create_at": str(r[0]), "title":r[1], "img_src": r[2], "post_ID":hashids.encode(r[3]), "category":r[4]} for r in result])
    except:
        return "Lỗi rùi nè"
    finally:
        cursor.close()

@app.route('/post/newspost', methods=['GET'])
def newspost():    
    try:        
        hashids = Hashids(min_length=12)
        db = connect_mysql()
        cursor  = db.cursor()
        base_url = os.getenv("BASE_URL")
        cursor.execute("""SELECT posts.post_ID,posts.create_at,posts.post_title,CONCAT(%s,image.src) as image_src,category.category FROM posts
                                INNER JOIN image ON image.img_ID = posts.post_image_ID
                                INNER JOIN  category ON category.category_ID = posts.post_category_ID 
                                WHERE posts.post_status = 'published' ORDER BY posts.post_ID DESC LIMIT 9
        """,(base_url))
        db.commit()                                
        result = cursor.fetchall()        
        return json.dumps([{"post_ID" : hashids.encode(r[0]),"create_at":str(r[1]),"post_title" : r[2],"img_src" : r[3],"category" : r[4]} for r in result])
    finally:
        cursor.close()

@app.route('/post/mostreadinday', methods = ['GET'])
def get():
    try:
        db = connect_mysql()
        hashids = Hashids(min_length=12)        
        cursor  = db.cursor()
        base_url = os.getenv("BASE_URL")
        cursor.execute("""
            SELECT posts.post_ID,posts.create_at,posts.post_title,CONCAT(%s,image.src) as image_src,category.category FROM blog.posts 
            INNER JOIN category on posts.post_category_ID = category.category_ID
            INNER JOIN image on image.img_ID = posts.post_image_ID
            WHERE Date(posts.create_at) = Date(now()) AND posts.post_status = "pulished"
            ORDER BY post_view DESC LIMIT 3
        """,(base_url))
        db.commit()
        result = cursor.fetchall()        
        return json.dumps([{"post_ID" : hashids.encode(r[0]),"create_at" : str(r[1]), "post_title" : r[2],"img_src" : r[3],"category":r[4]} for r in result])
    finally:
        cursor.close()
@app.route('/post/loadpostbyid', methods = ['POST'])
def post():
    try:
        db = connect_mysql()
        idRequest = request.get_json()['id']
        hashID = Hashids(min_length=12).decode(idRequest)[0]
        base_url = os.getenv("BASE_URL")
        cursor = db.cursor()
        cursor.execute("""
        UPDATE posts
        SET posts.post_view = posts.post_view + 1
        WHERE posts.post_ID = %s;
        """,(hashID))
        cursor.execute("""
            SELECT posts.post_ID,posts.create_at,posts.post_title,CONCAT(%s,image.src) as image_src,category.category,posts.post_content FROM posts
            INNER JOIN category on posts.post_category_ID = category.category_ID
            INNER JOIN image on image.img_ID = posts.post_image_ID
            WHERE posts.post_ID = %s
        """,(base_url,hashID))
        db.commit()
        result = cursor.fetchall()                
    
        return json.dumps([{"post_ID" : Hashids(min_length=12).encode(r[0]),"create_at" : str(r[1]), "post_title" : r[2],"img_src" : r[3],"category":r[4],"post_content" : r[5]} for r in result])
    finally:
        cursor.close()
@app.route('/post/allpost', methods= ['POST'])
def getAllPost():    
    try:
        # request data
        startAt = request.get_json()['start']                   
        # database
        db = connect_mysql()
        # cursor
        cursor = db.cursor()
        # hash
        hashids = Hashids(min_length=12)        
        # base_url
        base_url = os.getenv("BASE_URL")
        cursor.execute("""
            SELECT posts.post_ID,posts.create_at,posts.post_title,CONCAT(%s,image.src) as image_src,category.category,posts.post_content FROM posts
            INNER JOIN image ON image.img_ID = posts.post_image_ID
            INNER JOIN  category ON category.category_ID = posts.post_category_ID 
            WHERE posts.post_status='published'
            ORDER BY posts.post_ID DESC
            LIMIT 10
            OFFSET %s
        """,(base_url,startAt))
        db.commit()
        result = cursor.fetchall()        
        return json.dumps([{"post_ID" : hashids.encode(r[0]),"create_at" : str(r[1]), "post_title" : r[2],"img_src" : r[3],"category":r[4]} for r in result])
    finally:
        cursor.close()
@app.route('/post/codingpost',methods= ['POST'])
def getCodingPost():
    try:
        db = connect_mysql()
        cursor = db.cursor()
        startAt = request.get_json()['start']
        hashids = Hashids(min_length=12)     
        base_url = os.getenv("BASE_URL")
        cursor.execute("""
            SELECT posts.post_ID,posts.create_at,posts.post_title,CONCAT(%s,image.src) as image_src,category.category,posts.post_content FROM posts
            INNER JOIN image ON image.img_ID = posts.post_image_ID
            INNER JOIN  category ON category.category_ID = posts.post_category_ID 
            WHERE posts.post_status='published' AND category.category = 'LẬP TRÌNH'
            ORDER BY posts.post_ID DESC
            LIMIT 10
            OFFSET %s            
        """,(base_url,startAt))
        db.commit()
        result = cursor.fetchall()
        return json.dumps([{"post_ID" : hashids.encode(r[0]),"create_at" : str(r[1]), "post_title" : r[2],"img_src" : r[3],"category":r[4]} for r in result])
    finally:
        cursor.close()        


if __name__ == '__main__':
    app.run(debug=True)
