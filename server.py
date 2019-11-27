from flask_api import FlaskAPI
from flask import request, jsonify
from flask_cors import CORS
import json
import pymysql
import time

app = FlaskAPI(__name__)
CORS(app)


def connect_mysql():
    db = pymysql.connect(host='localhost', user="root", db='blog', password="")
    return db

@app.route('/post/mostread', methods=['GET'])
def mostread():
    try:
        db = connect_mysql()
        cursor = db.cursor()
        cursor.execute("""SELECT posts.create_at,posts.post_title,CONCAT('http://localhost:8001/',image.src) as image_src,posts.post_ID,category.category  FROM posts 
                            INNER JOIN image on image.img_ID = posts.post_image_ID 
                            INNER JOIN category on category.category_ID = posts.post_category_ID
                            ORDER BY post_view desc limit 4 
                            """)
        db.commit()
        result = cursor.fetchall()
        return json.dumps([{"create_at": str(r[0]), "title":r[1], "img_src": r[2], "post_ID":r[3], "category":r[4]} for r in result])
    except:
        return "Lỗi rùi nè"
    finally:
        cursor.close()

@app.route('/post/newspost', methods=['GET'])
def newspost():    
    try:        
        db = connect_mysql()
        cursor  = db.cursor()
        cursor.execute("""SELECT posts.post_ID,posts.create_at,posts.post_title,CONCAT('http://localhost:8001/',image.src) as image_src,category.category FROM posts
                                INNER JOIN image ON image.img_ID = posts.post_image_ID
                                INNER JOIN  category ON category.category_ID = posts.post_category_ID 
                                WHERE posts.post_status = 'published' ORDER BY posts.post_ID DESC LIMIT 9
        """)
        db.commit()        
        result = cursor.fetchall()        
        return json.dumps([{"post_ID" : r[0],"create_at":str(r[1]),"post_title" : r[2],"img_src" : r[3],"category" : r[4]} for r in result])
    finally:
        cursor.close()


if __name__ == '__main__':
    app.run(debug=True)
