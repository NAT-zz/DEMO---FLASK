from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import cloudinary

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:tuan@1310@localhost/cnpm-demo?charset=utf8mb4"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
# Cần có key để thao tác với session
app.secret_key = "(A*FA(GAGASDA*&"
# Cấu hình Cloudinary
app.config["CLOUDINARY_INFO"] = {
    "cloud_name" : "natscloud",
    "api_key" : "669999992192735",
    "api_secret": "7-zbW0Pat43_axsYVZ2ULRTe5zY"
}


#đặt tên j cx dc: PAGE_SIZE
app.config["PAGE_SIZE"] = 3

db = SQLAlchemy(app=app)
my_login = LoginManager(app=app)

cloudinary.config(cloud_name = app.config["CLOUDINARY_INFO"]['cloud_name'],
                api_key = app.config["CLOUDINARY_INFO"]['api_key'],
                api_secret = app.config["CLOUDINARY_INFO"]['api_secret'])

CART_KEY = "cart"