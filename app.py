import sys
sys.stdout.reconfigure(encoding='utf-8')
import datetime
from flask import request, redirect, url_for, Flask, render_template, session, flash
from config import config
import mysql.connector
import os
from werkzeug.utils import secure_filename
from flask import Flask, session, redirect, url_for, request, flash

app = Flask(__name__)
app.secret_key = config.SECRET_KEY

# Kết nối database
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:@localhost/bookstore1'

UPLOAD_FOLDER = 'static/images/uploads' # Thư mục lưu trữ ảnh
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'} # Các định dạng ảnh được phép
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024 # Giới hạn kích thước file upload là 16MB
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def connect():
    return mysql.connector.connect(database=config.SQL_DB, user=config.SQL_USER, password=config.SQL_PASSWORD, host=config.SQL_HOST)
# Hàm kiểm tra định dạng tệp ảnh
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
# Trang Admin
@app.route('/admin')
def admin():
    if 'user' not in session:
        return redirect(url_for('login'))
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM categories")
    categories = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('admin.html', categories=categories)   
# Xóa chuyên mục
@app.route('/delete_category/<int:id>', methods=['GET', 'POST'])
def delete_category(id):
    if request.method == 'POST':
        name = request.form.get('catename')
        conn = connect()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM categories WHERE cateid=%s", (id,))
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('admin'))
    else:
        conn = connect()
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM categories WHERE cateid={id}")
        category = cursor.fetchone()
        cursor.close()
        conn.close()
        return render_template('delete_category.html', category=category)
# Sửa chuyên mục
@app.route('/edit_category/<int:id>', methods=['GET', 'POST'])
def edit_category(id):
    if request.method == 'POST':
        name = request.form.get('catename')
        conn = connect()
        cursor = conn.cursor()
        cursor.execute(f"UPDATE categories SET catename='{name}' WHERE cateid={id}")
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('admin'))
    else:
        conn = connect()
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM categories WHERE cateid={id}")
        category = cursor.fetchone()
        cursor.close()
        conn.close()
        return render_template('edit_category.html', category=category)
# Thêm chuyên mục
@app.route('/add_category', methods=['GET', 'POST'])
def add_category():
    if request.method == 'POST':
        name = request.form.get('catename')
        conn = connect()
        cursor = conn.cursor()
        cursor.execute(f"INSERT INTO categories (catename) VALUES ('{name}')")
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('admin'))
    else:
        return render_template('add_category.html')
# quản lý sách
@app.route('/booksmanage')
def booksmanage():
    if 'user' not in session:
        return redirect(url_for('login'))
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("select b.bid, b.title,b.author,b.description, b.price FROM books b, categories c WHERE b.cateid=c.cateid;")
    books = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('booksmanage.html', b=books)
# Xóa sách
@app.route('/delete_book/<int:id>', methods=['GET', 'POST'])
def delete_book(id):
    conn = connect()
    cursor = conn.cursor()

    if request.method == 'POST':
        try:
            cursor.execute("DELETE FROM books WHERE bid = %s", (id,))
            conn.commit()
        except mysql.connector.Error as err:
            print(f"Lỗi: {err}")
            conn.rollback()
        finally:
            cursor.close()
            conn.close()
        return redirect(url_for('booksmanage'))

    else:
        # Lấy thông tin sách để hiển thị xác nhận
        cursor.execute("SELECT * FROM books WHERE bid = %s", (id,))
        book = cursor.fetchone()
        cursor.close()
        conn.close()
        return render_template('delete_book.html', book=book)
# Sửa sách
@app.route('/edit_book/<int:id>', methods=['GET', 'POST'])
def edit_book(id):
    conn = connect()
    cursor = conn.cursor()

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        author = request.form.get('author', '').strip()
        price = request.form.get('price', '').strip()
        description = request.form.get('description', '').strip()
        cateid = request.form.get('cateid', '').strip()
        current_image = request.form.get('current_image', '')
        image_file = request.files.get('image')

        image_name = current_image

        if image_file and allowed_file(image_file.filename):
            filename = secure_filename(image_file.filename)
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            image_file.save(image_path)
            image_name = filename

        try:
            cursor.execute("""
                UPDATE books 
                SET title = %s, author = %s, price = %s, description = %s, image = %s, cateid = %s 
                WHERE bid = %s
            """, (title, author, price, description, image_name, cateid, id))
            conn.commit()
        except mysql.connector.Error as err:
            print(f"[Edit Book] Lỗi SQL: {err}")
            conn.rollback()
        finally:
            cursor.close()
            conn.close()

        return redirect(url_for('booksmanage'))

    # GET: lấy dữ liệu để hiển thị lên form
    try:
        cursor.execute("SELECT * FROM books WHERE bid = %s", (id,))
        book = cursor.fetchone()

        cursor.execute("SELECT * FROM categories")
        categories = cursor.fetchall()
    except mysql.connector.Error as err:
        print(f"[Edit Book] Lỗi DB: {err}")
        book = None
        categories = []
    finally:
        cursor.close()
        conn.close()

    if book:
        return render_template('edit_book.html', book=book, categories=categories)
    else:
        return "Không tìm thấy sách để chỉnh sửa", 404

# Thêm sách
@app.route('/add_book', methods=['GET', 'POST'])
def add_book():
    conn = connect()
    cursor = conn.cursor()

    if request.method == 'POST':
        try:
            title = request.form['title']
            author = request.form['author']
            price = request.form['price']
            description = request.form['description']
            cateid = request.form['cateid']
            image_file = request.files.get('image')

            image_name = 'noimage.jpg'

            if image_file and allowed_file(image_file.filename):
                filename = secure_filename(image_file.filename)
                image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                image_file.save(image_path)
                image_name = filename

            cursor.execute("""
                INSERT INTO books (title, author, price, description, cateid, image)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (title, author, price, description, cateid, image_name))
            conn.commit()

            flash("Thêm sách thành công!", "success")
            return redirect(url_for('booksmanage'))

        except Exception as err:
            conn.rollback()
            flash(f"Lỗi khi thêm sách: {err}", "danger")
            return redirect(url_for('add_book'))

        finally:
            cursor.close()
            conn.close()

    # GET method: hiển thị form
    try:
        cursor.execute("SELECT * FROM categories")
        categories = cursor.fetchall()
        return render_template('add_book.html', categories=categories)
    except Exception as e:
        flash(f"Lỗi khi tải danh mục: {e}", "danger")
        return render_template('add_book.html', categories=[])
    finally:
        cursor.close()
        conn.close()

# Đăng xuất
@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))
# Trang chủ
@app.route('/')
def index():
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("SELECT bid, title, author, price, description, image FROM books")
    books = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('index.html', books=books)   

# Đăng nhập
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form.get('user')
        password = request.form.get('password')

        conn = connect()
        cursor = conn.cursor(dictionary=True)  # để lấy dict thay vì tuple
        cursor.execute("SELECT * FROM users WHERE username=%s AND password=%s", (username, password))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user:
            session['user'] = user  # lưu user vào session

            # ✅ Điều hướng theo role
            if user['role'] == 1:
                return redirect(url_for('admin'))  # admin
            else:
                return redirect(url_for('index'))  # user thường
        else:
            error = "Tên đăng nhập hoặc mật khẩu không đúng"
    return render_template('login.html', error=error)
# mua hang
@app.route('/orders')
def orders():
    conn = connect()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT o.oid, u.username, o.total, o.created
            FROM orders o
            JOIN users u ON o.uid = u.uid
            ORDER BY o.created DESC
        """)
        orders = cursor.fetchall()
    finally:
        cursor.close()
        conn.close()

    return render_template('orders.html', orders=orders)
# Chi tiết đơn hàng
@app.route('/order/<int:id>')
def order_detail(id):
        conn = connect()
        cursor = conn.cursor()

    # Truy vấn thông tin hóa đơn (thêm name, phone, address)
        cursor.execute("""
        SELECT oid, fullname, total, created, phone, address 
        FROM orders 
        WHERE oid = %s
    """, (id,))
        order = cursor.fetchone()

    # Truy vấn chi tiết sản phẩm trong hóa đơn
        cursor.execute("""
        SELECT b.title, b.price, od.quanity 
        FROM orderdetail od
        JOIN books b ON od.bid = b.bid 
        WHERE od.oid = %s
    """, (id,))
        items = cursor.fetchall()

        conn.close()

        return render_template("order_detail.html", order=order, items=items)
# Thêm sản phẩm vào giỏ hàng
@app.route('/add_to_cart/<int:bid>', methods=['POST'])
def add_to_cart(bid):
    cart = session.get('cart', {})

    # Nếu sản phẩm đã tồn tại trong giỏ -> tăng số lượng
    if str(bid) in cart:
        cart[str(bid)] += 1
    else:
        cart[str(bid)] = 1

    session['cart'] = cart
    flash('Đã thêm sản phẩm vào giỏ hàng!')
    return redirect(request.referrer or url_for('index'))
# Xem giỏ hàng
@app.route('/cart')
def cart():
    cart = session.get('cart', {})  # Lấy giỏ hàng từ session (hoặc {} nếu chưa có)
    books = []
    total = 0
    if cart:
        conn = connect()  # Kết nối tới cơ sở dữ liệu
        cursor = conn.cursor()
        for bid, quantity in cart.items():  # Duyệt qua các sản phẩm trong giỏ hàng
            cursor.execute("SELECT bid, title, price FROM books WHERE bid=%s", (bid,))
            book = cursor.fetchone()
            if book:
                item_total = book[2] * quantity  # Tính thành tiền cho từng sản phẩm
                total += item_total  # Cộng dồn vào tổng tiền
                books.append({
                    'bid': book[0],
                    'title': book[1],
                    'price': book[2],
                    'quantity': quantity,  # Đảm bảo số lượng được lấy đúng từ giỏ hàng
                    'total': item_total  # Thành tiền cho sản phẩm
                })
        cursor.close()
        conn.close()

    # In ra giỏ hàng (debugging)
    print("Cart session:", cart)

    return render_template('cart.html', books=books, total=total)
# Đếm số lượng sản phẩm trong giỏ hàng
@app.context_processor
def inject_cart_count():
    cart = session.get('cart', {})
    count = sum(cart.values()) if cart else 0
    return dict(cart_count=count)
# Xóa sản phẩm khỏi giỏ hàng
@app.route('/remove_from_cart/<int:bid>')
def remove_from_cart(bid):
    cart = session.get('cart', {})
    if str(bid) in cart:
        cart.pop(str(bid))
        session['cart'] = cart
        Flask('Đã xóa khỏi giỏ hàng!')
    return redirect(url_for('cart'))
from flask import request, redirect, render_template, session, url_for, flash
from datetime import datetime
# Đặt hàng
@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    if 'user' not in session:
        flash('Vui lòng đăng nhập để đặt hàng.', 'warning')
        return redirect(url_for('login'))

    cart = session.get('cart', {})
    if not cart:
        flash('Giỏ hàng của bạn đang trống.', 'info')
        return redirect(url_for('cart'))

    if request.method == 'POST':
        fullname = request.form.get('fullname')
        phone = request.form.get('phone')
        address = request.form.get('address')

        if not fullname or not phone or not address:
            flash('Vui lòng nhập đầy đủ thông tin giao hàng.', 'danger')
            return redirect(url_for('checkout'))
        conn = connect()
        cursor = conn.cursor()

        # Tính tổng đơn hàng
        total = 0
        for bid, quanity in cart.items():
            cursor.execute("SELECT price FROM books WHERE bid = %s", (bid,))
            price = cursor.fetchone()
            if price:
                total += price[0] * quanity	

        # Thêm đơn hàng
        created = datetime.now()
        uid = session['user']['uid']
        cursor.execute("""
            INSERT INTO orders (uid, total, created, fullname, phone, address)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (uid, total, created, fullname, phone, address))
        oid = cursor.lastrowid

        # Thêm chi tiết đơn hàng
        for bid, quanity in cart.items():
            cursor.execute("INSERT INTO orderdetail (oid, bid, quanity) VALUES (%s, %s, %s)",
                           (oid, bid, quanity))

        conn.commit()
        cursor.close()
        conn.close()

        session['cart'] = {}  # Xóa giỏ hàng sau khi đặt hàng
        flash('Đặt hàng thành công!', 'success')
        return redirect(url_for('index'))

    return render_template('checkout.html')
# tim kiếm sách
@app.route('/search')
def search():
    keyword = request.args.get('q', '')
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("SELECT bid, title, author, price, description, image FROM books WHERE title LIKE %s OR author LIKE %s", 
                   ('%' + keyword + '%', '%' + keyword + '%'))
    books = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('index.html', books=books, search=True)
@app.route('/update_cart/<int:bid>', methods=['POST'])
def update_cart(bid):
    action = request.form.get('action')
    cart = session.get('cart', {})

    if action == 'increase':
        cart[str(bid)] = cart.get(str(bid), 0) + 1
    elif action == 'decrease':
        if cart.get(str(bid), 0) > 1:
            cart[str(bid)] -= 1
        else:
            cart.pop(str(bid))  # xóa khỏi giỏ nếu nhỏ hơn 1

    session['cart'] = cart
    return redirect(url_for('cart'))
# Đăng ký
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm = request.form.get('confirm_password')


        if password != confirm:
            return "Mật khẩu xác nhận không khớp!"

        conn = connect()
        cursor = conn.cursor(dictionary=True)

        # Kiểm tra xem có tài khoản nào trong bảng users chưa
        cursor.execute("SELECT COUNT(*) AS total FROM users")
        user_count = cursor.fetchone()['total']

        # Gán role
        role = 1 if user_count == 0 else 0  # Tài khoản đầu tiên là admin

        cursor.execute("INSERT INTO users (username, email, password, role) VALUES (%s, %s, %s, %s)",
                       (username, email, password, role))
        conn.commit()
        cursor.close()
        conn.close()

        return redirect(url_for('login'))

    return render_template('register.html')
# Xóa danh sách hóa đơn
@app.route('/delete_order/<int:id>')
def delete_order(id):
    conn = connect()
    cursor = conn.cursor()

    # Xóa chi tiết đơn hàng trước
    cursor.execute('DELETE FROM orderdetail WHERE oid = %s', (id,))
    
    # Sau đó xóa hóa đơn
    cursor.execute('DELETE FROM orders WHERE oid = %s', (id,))

    conn.commit()
    conn.close()

    return redirect(url_for('orders'))  # Quay lại danh sách hóa đơn
from flask import Flask, render_template, request, session, redirect, url_for
@app.route('/users')
def users():
    if 'user' not in session or session['user']['role'] != 1:
        return redirect(url_for('login'))
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("SELECT uid, username, email, role FROM users")
    users = cursor.fetchall()
    return render_template('admin_users.html', users=users)

@app.route('/edit_user/<int:uid>', methods=['GET', 'POST'])
def edit_user(uid):
    conn = connect()
    cursor = conn.cursor()
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        role = int(request.form['role'])

        # Dùng %s cho MySQL và thêm dấu phẩy bị thiếu
        cursor.execute(
            "UPDATE users SET username=%s, email=%s, password=%s, role=%s WHERE uid=%s",
            (username, email, password, role, uid)
        )
        conn.commit()
        flash('Đã cập nhật người dùng')
        return redirect(url_for('users'))

    cursor.execute("SELECT uid, username, email, password, role FROM users WHERE uid=%s", (uid,))
    user = cursor.fetchone()
    return render_template('edit_user.html', user=user)
@app.route('/delete_user/<int:uid>')
def delete_user(uid):
    # Kiểm tra đăng nhập và quyền admin
    if 'user' not in session or session['user']['role'] != 1:
        flash('Bạn không có quyền thực hiện thao tác này.')
        return redirect(url_for('login'))

    conn = connect()
    cursor = conn.cursor()

    # Kiểm tra role của người dùng cần xoá
    cursor.execute("SELECT role FROM users WHERE uid = %s", (uid,))
    result = cursor.fetchone()

    if not result:
        flash('Người dùng không tồn tại.')
    elif result[0] == 1:
        flash('Không thể xóa tài khoản Admin.')
    else:
        cursor.execute("DELETE FROM users WHERE uid = %s", (uid,))
        conn.commit()
        flash('Đã xóa người dùng')

    return redirect(url_for('users'))

# Mua ngay
@app.route('/buy_now/<int:bid>', methods=['POST'])
def buy_now(bid):
    cart = session.get('cart', {})
    cart[str(bid)] = cart.get(str(bid), 0) + 1
    session['cart'] = cart
    return redirect(url_for('cart'))  # điều hướng sang trang giỏ hàng

@app.route('/book/<int:bid>')
def book_detail(bid):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM books WHERE bid = %s", (bid,))
    book = cursor.fetchone()

    if not book:
        flash('Không tìm thấy sách.')
        return redirect(url_for('index'))

    return render_template('book_detail.html', book=book)


if __name__ == '__main__':
    app.run(port=5001, debug=True)
