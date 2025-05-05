import mysql.connector  #import thư viện mysql.connector
class config:
    SQL_DB = 'bookstore1' #tên csdl trong mysql
    SQL_USER = 'root' #tên user trong mysql
    SQL_PASSWORD = ''#mật khẩu của user trong mysql
    SQL_HOST = 'localhost'#địa host chỉ của mysql
    SECRET_KEY = '123456' #khóa bí mật
def conect(self):
    return mysql.connector.connect(database=self.SQL_DB, user=self.SQL_USER, password=self.SQL_PASSWORD, host=self.SQL_HOST)
    