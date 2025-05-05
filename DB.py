# from flask_sqlalchemy import SQLAlchemy

# db = SQLAlchemy()

# class User(db.Model):
#     uid = db.Column(db.Integer, primary_key=True)
#     username = db.Column(db.String(50), nullable=False)
#     email = db.Column(db.String(50), nullable=False, unique=True)
#     password = db.Column(db.String(50), nullable=False)
#     role = db.Column(db.Boolean, default=False)

# class Book(db.Model):
#     bid = db.Column(db.Integer, primary_key=True)
#     title = db.Column(db.String(100), nullable=False)
#     author = db.Column(db.String(50), nullable=False)
#     price = db.Column(db.Float, nullable=False)
#     description = db.Column(db.String(255))
#     image = db.Column(db.String(255))
#     cateid = db.Column(db.Integer, db.ForeignKey('categories.cateid'), nullable=False)

# class Categories(db.Model):
#     cateid = db.Column(db.Integer, primary_key=True)
#     catename = db.Column(db.String(100), nullable=False)

# class Order(db.Model):
#     oid = db.Column(db.Integer, primary_key=True)
#     uid = db.Column(db.Integer, db.ForeignKey('user.uid'), nullable=False)
#     total = db.Column(db.Float, nullable=False)
#     created = db.Column(db.DateTime, default=datetime.datetime.utcnow)

# class OrderDetail(db.Model):
#     did = db.Column(db.Integer, primary_key=True)
#     oid = db.Column(db.Integer, db.ForeignKey('order.oid'), nullable=False)
#     bid = db.Column(db.Integer, db.ForeignKey('book.bid'), nullable=False)
#     quantity = db.Column(db.Integer, nullable=False)



from flask_sqlalchemy import SQLAlchemy # type: ignore
db = SQLAlchemy()
class user(db.Model):
    uid = db.Column("uid" ,db.Integer, primary_key=True)
    username = db.Column("username" ,db.String(50))
    email = db.Column("email" ,db.String(50))
    password = db.Column("password" ,db.String(50))
    role = db.Column("role" ,db.Bollean)
class book(db.Model):
    bid = db.Column("bid" ,db.Integer, primary_key=True)
    title = db.Column("title" ,db.String(100))
    author = db.Column("author" ,db.String(50))
    price = db.Column("price" ,db.Float)
    description = db.Column("description" ,db.String(50))
    image = db.Column("image" ,db.String(255))
    cateid = db.Column("cateid" ,db.Integer)
class categories(db.Model):
    cateid = db.Column("cateid" ,db.Integer, primary_key=True)
    catename = db.Column("catename" ,db.String(100))
class oder(db.Model):
    oid = db.Column("oid" ,db.Integer, primary_key=True)
    uid = db.Column("uid" ,db.Integer)
    total = db.Column("total" ,db.Float)
    created = db.Column("created" ,db.DateTime)
class oderdeltal(db.Model):
    did = db.Column("odid" ,db.Integer, primary_key=True)
    oid = db.Column("oid" ,db.Integer)
    bid = db.Column("bid" ,db.Integer)
    quantity = db.Column("quantity" ,db.Integer)
