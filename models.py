from datetime import datetime

from flask_login import UserMixin
from sqlalchemy import (Boolean, Column, DateTime, Float, ForeignKey, Integer,
                        String, Enum, func, or_)
from sqlalchemy.orm import relationship
import enum
class MyRole(enum.Enum):
    USER = 1
    ADMIN = 0

from __init__ import db


class Category(db.Model):
    __tablename__ = 'Test_Table'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(30), nullable=False)
    #truy vấn ngược phải đi kèm với khóa ngoại bên dưới
    products = relationship('Product', backref = "category", lazy = True)

    def __str__(self):
        return self.name

class Product(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    price = Column(Float, default = 0.0, nullable=False)
    image = Column(String(100), nullable=True)
    #Khóa ngoai
    category_id = Column(Integer, ForeignKey(Category.id), nullable=False)

    receipt_details = relationship("ReceiptDetail", backref = "product", lazy = True)
    def __str__(self):
        return self.name
    
class User(db.Model, UserMixin):
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    is_active = Column(Boolean, default=True)
    join_date = Column(DateTime, default = datetime.now())
    username = Column(String(50), nullable=False, unique=True)
    #Lưu xuống database dưới dạng băm
    password = Column(String(100), nullable=False)
    avatar = Column(String(100), nullable=True)
    role = Column(Enum(MyRole), default = MyRole.USER) 

    #Lazy = false thi khi lay User se lay luon Receipt
    #Lazy = true thi khi lay User khi se khong truy van, luc can thi moi lay
    receipts = relationship("Receipt", backref="user", lazy = True)
    def __str__(self):
        return self.name

class Receipt(db.Model):
    id = Column(Integer, primary_key=True, autoincrement= True)
    created_date = Column(DateTime, default = datetime.now())
    user_id = Column(Integer, ForeignKey(User.id), nullable=False)

    details = relationship("ReceiptDetail", backref = "receipt", lazy = True)

class ReceiptDetail(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    receipt_id = Column(Integer, ForeignKey(Receipt.id), nullable=False)
    product_id = Column(Integer, ForeignKey(Product.id), nullable=False)
    quantity = Column(Integer, default = 0)
    unit_price = Column(Float, default = 0)
    

#Thêm dữ liệu
# c = Category('Mobile') 
# db.session.add(c)
# db.session.commit()


# Lấy từ CSDL theo khóa chính (id)
# c = Category.query.get(1) 
# = select* from Category where id = 1
# Thêm vào b với khóa ngoại
# p = Product(name = 'iphone', price=30, category = c) 
# db.session.add(p)
# db.session.commit()

# p = Product.query.get(2)
# p.__dict__ : xem hết thông tin
# p.category : xem thông tin p thuộc category nào
# p.category.__dict__ : xem thông tin category đó
# => tác dụng của backref

#Cập nhật 
# c.name = 'tuan'
# db.session.add(c)
# db.session.commit()
#Xóa
# db.session.delete(c)
# db.session.commit()

#Loc
#c = Category.query.filter(Category.name.contains("t"))
#Product.query.filter(Product.name.contains('iphone')).all()
#Product.query.filter(Product.name.startswith('g')).all()
#Product.query.filter(Product.name.endswith('y')).all()

#Lấy sản phẩm có giá lớn hơn 15
#Product.query.filter(Product.price.__gt__(15)).all() 
#Lấy sản phẩm có giá nhở hơn 35
#Product.query.filter(Product.price.__lt__(35)).all() 

#Lấy all sản phẩm sort tăng dần theo id
#Product.query.order_by(Product.id).all()
#Lấy all sản phẩm sort giảm dần theo 
#Product.query.order_by(-Product.id).all()  

#Lấy all sản phẩm với các điều kiện nối = and
#Product.query.filter(Product.price.__lt__(35), Product.name.contains('iphone')).order_by(Product.id).all()
#Lấy al sản phẩm với các điều kiện nối = or
#Product.query.filter(or_(Product.price.__lt__(35), Product.name.contains('iphone'))).order_by(Product.id).all()
#join 2 bảng
#Product.query.join(Category, Product.category_id==Category.id).filter(Category.name.contains('t')).add_column(Category.name).all()
#Tìm giá trị lớn nhất
#db.session.query(func.max(Product.price)).first()

if __name__ == '__main__':
    db.create_all()

