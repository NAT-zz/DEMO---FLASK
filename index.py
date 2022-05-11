import re
from flask import render_template, request, redirect, session, jsonify
from __init__ import app, my_login, CART_KEY
from admin import*
from models import User
from flask_login import login_user, logout_user
import utils
import hashlib
import math
import cloudinary
import cloudinary.uploader

#Xu li url / nhan request va tra respond
@app.route("/") 
def home():
    #Gởi dữ liệu từ server ra
    #Cách chuyển dữ liệu từ server sang client
    
    #Lấy tham số category_id, không có thì trả ra None
    products = utils.get_product(kw = request.args.get("kw"), category_id=request.args.get("category_id"), page = int(request.args.get("page", 1)))

    count = utils.count_product()
    size = app.config["PAGE_SIZE"]

    return render_template('home.html',
     product = products, pagenum = math.ceil(count/size))  

#Gửi tham số từ client lên server = path params (Cách 1)
@app.route("/hello/<name>/<int:year>") #Có thể ràng buộc kiểu dữ liệu
def hello(name, year):
    return render_template('home.html', message = "WELCOME %s %d" % (name, year), name = name)

#Request params = gởi dữ liệu từ client lên server (Cách 2)
@app.route("/hello2/")
def hello2():
    fn = request.args.get('first_name', "A") #Nếu không truyền thì lấy mặc định là A
    ln = request.args.get('last_name', "B")
    return render_template('hello.html', message = "WELCOME %s %s" % (fn,ln))

#Gởi dữ liệu từ client lên server theo phương thức put, patch cũng tương tự
#Gởi file lên server phải dùng post
@app.route("/upload", methods=["POST"])
def upload():
    #Tập tin phải .file
    avatar = request.files.get("Avatar")
    if avatar:
        avatar.save("%s/static/images/%s" % (app.root_path, avatar.filename))
        return "SUCCESSFUL"
    return "FAILED"

#Thử trang kế thừa
@app.route("/extend")
def inherit():
    return render_template('extend.html')

@app.route("/loginadmin", methods = ["POST"])
def user_login_execute():
    username = request.form.get("username")
    pwd = request.form.get("password")
    #Trước khi lưu vào Database
    #user.password = str(hashlib.md5(user.password.encode("utf-8")).digest())
    pwd = str(hashlib.md5(pwd.encode("utf-8")).digest())
    user = User.query.filter(User.username == username, User.password == pwd).first()

    if user:
        login_user(user)
    return redirect('/admin')

@my_login.user_loader
#Bỏ vào biến current user
def user_load(user_id):
    return User.query.get(user_id)

@app.route("/api/add-item-cart", methods = ["POST"]) 
def add_to_cart():
    cart = session.get(CART_KEY) #<- key là "cart"
    # Nếu chưa bỏ j vào giở
    if not cart:
        cart = {}
    
    # lấy dữ liệu dạng json từ body, kiểu POST
    data = request.json
    product_id = str(data["product_id"])

    if product_id in cart: #sản phẩm đã từng bỏ vào giỏ
        p = cart[product_id]
        p['quantity'] = p['quantity'] + 1
    else:
        cart[product_id] = { 
            "product_id" : data["product_id"],
            "product_name" : data["product_name"],
            "product_price" : data["product_price"],
            "quantity" : 1
        }

    # debug đặt breakpoint
    # import pdb 
    # pdb.set_trace()

    session[CART_KEY] = cart
    return jsonify(utils.cart_stats(cart))

@app.route("/api/update-cart-item", methods=["put"])
def update_cart_item():
    cart = session.get(CART_KEY)
    if cart:
        data = request.json
        try:
            product_id = str(data["product_id"])
            quantity = data['quantity']
        except IndexError | KeyError as ex:
            print(ex)
        else:
            if product_id in cart:
                p = cart[product_id]
                p['quantity'] = quantity
                session[CART_KEY] = cart
            return jsonify({
                "error_code": 200,
                "cart_stats": utils.cart_stats(cart)
            })

    return jsonify({
        "error_code": 404
    })

@app.route("/api/delete-cart-item/<product_id>", methods=["delete"])
def delete_cart_item(product_id):
    cart = session.get(CART_KEY)
    if cart:
        if product_id in cart:
            del cart[product_id]
            session[CART_KEY] = cart
            return jsonify({
                "error_code": 200,
                "cart_stats": utils.cart_stats(cart)
            })
    
    return jsonify({
        "error_code": 404
    })

@app.route("/cart")
def cart():
    return render_template('cart.html')

#gắn vô context của request
@app.context_processor
def common_context():
    cart_stats = utils.cart_stats(session.get("cart"))
    categories = utils.get_category()
    return {
        "category": categories,
        "cart_stats": cart_stats
    }

@app.route("/api/pay", methods = ["POST"])
def pay():
    cart = session.get(CART_KEY)
    if cart:
        if utils.add_receipt(cart):
            del session[CART_KEY]
            return jsonify({
                "error_code": 200
            })
    return jsonify({
        "error_code": 404
    })

@app.route("/user-logout")
def normaluser_logout():
    logout_user()
    return redirect("/user-login")

@app.route("/user-login", methods = ["POST", "GET"])
def normaluser_login():
    err_msg = ""
    if request.method == "POST":
        username = request.form.get("username")
        pwd = request.form.get("password")
        #Trước khi lưu vào Database
        #user.password = str(hashlib.md5(user.password.encode("utf-8")).digest())
        pwd = str(hashlib.md5(pwd.encode("utf-8")).digest())
        user = User.query.filter(User.username == username, User.password == pwd).first()

        if user:
            login_user(user)
            return redirect(request.args.get("next", "/"))
        else:
            err_msg = "Username hoac password khong chinh xac"

    return render_template("login_user.html", err_msg=err_msg)
    
@app.route("/register", methods=["POST", "GET"])
def register():
    err_msg = ""
    if request.method == 'POST':
        try:
            password = request.form.get("password")    
            confirm_password = request.form.get("confirm-password")
            if password.strip() == confirm_password.strip():
                avatar = request.files['avatar']
                data = request.form.copy()
                del data['confirm-password']

                if utils.add_user(**data):
                    return redirect("/user-login")
                else:
                    err_msg = "Dữ liệu đầu vào không hợp lệ"
            else:
                err_msg = "Mật khẩu không khớp"
        except:
            err_msg = "Hệ thống lỗi"

    return render_template("register.html", err_msg = err_msg)

if __name__ == '__main__':
    app.run(debug=True)

# virtualenv --python=/usr/bin/python3.9 venv
# source venv/bin/activate

# pip install -r requirements.txt

# pip install flask
# pip install sqlalchemy
# pip install cloudinary
# pip install flask_login
# pip install flask_admin
# pip install flask_sqlalchemy


# show databases;
# use natzz$demodb;
# show tables;
# source demoapp/demodb.sql

# "mysql+pymysql://natzz:tuan@1310@natzz.mysql.pythonanywhere-services.com/natzz$demodb?charset=utf8mb4"
