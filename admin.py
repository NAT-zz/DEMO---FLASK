from flask import redirect
from flask_admin import BaseView, expose, Admin, AdminIndexView
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user, logout_user
from flask import request

from __init__ import db, app
import utils
#Cần quản lý bảng nào thì thêm vào
from models import Category, Product

class MyAdminIndex(AdminIndexView):
    @expose("/")
    def index(self):
        stats = utils.product_stats_by_cate()
        return self.render('admin/index.html', stats = stats)

admin = Admin(app=app, name = "UTE SHOP", template_mode = 'bootstrap4', index_view=MyAdminIndex())

#view chứng thực, quyền cho phép đăng nhập vào view
class AuthenticatedView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated

class CategoryModelView(AuthenticatedView):
    #Cu override 
    can_export = True
    can_view_details = True
    
class ProductModelView(AuthenticatedView):
    can_export = True

class StatsBaseView(BaseView):
    @expose('/')
    def index(self):
        from_date = request.args.get("from_date")
        to_date = request.args.get("to_date")

        stats = utils.product_stats(from_date=from_date, to_date=to_date)
        return self.render("admin/stats.html", stats= stats) 

    def is_accessible(self):
        return current_user.is_authenticated

class LogoutView(BaseView):
    @expose('/')
    def index(self):
        logout_user()
        return redirect("/admin")

    def is_accessible(self):
        return current_user.is_authenticated
    

#Thêm session để thêm, xóa, sửa
admin.add_view(CategoryModelView(Category, db.session, name = "Danh Muc"))
admin.add_view(ProductModelView(Product, db.session, name = "San Pham"))
admin.add_view(StatsBaseView(name = "Revenue stats"))
admin.add_view(LogoutView(name = "Dang xuat"))
