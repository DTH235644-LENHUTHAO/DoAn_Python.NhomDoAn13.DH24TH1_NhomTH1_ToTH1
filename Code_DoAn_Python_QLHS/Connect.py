from tkinter import*
from tkinter import messagebox
import pyodbc
from tkinter import ttk

#Thiet lâp ket nối
SERVER_NAME = 'LAPTOP-GHON1NSC\MSSQLSERVER01' 
DATABASE_NAME = 'QuanLyHocSinh' 

CONNECTION_STRING = (
    f'Driver={{ODBC Driver 17 for SQL Server}};'
    f'Server={SERVER_NAME};'
    f'Database={DATABASE_NAME};'
    f'Trusted_Connection=yes;' 
)

conn = None
cursor = None

def connect_db():
    """Kết nối tới SQL Server sử dụng CONNECTION_STRING."""
    global conn, cursor
    try:
        conn = pyodbc.connect(CONNECTION_STRING,unicode_results=True)
        cursor = conn.cursor()
        print("Kết nối CSDL thành công!")
    except Exception as e:
        conn = None
        cursor = None
        messagebox.showerror("Lỗi Kết Nối", f"Không thể kết nối CSDL.\n{e}")
        
def close_db():
    """Đóng con trỏ và kết nối CSDL nếu chúng đang mở."""
    global conn, cursor
    
    if cursor is not None:
        try:
            cursor.close()
            cursor = None # Đặt lại biến
            print("Đã đóng Cursor CSDL.")
        except Exception as e:
            print(f"Lỗi khi đóng Cursor: {e}")
            
    # Đóng kết nối
    if conn is not None:
        try:
            conn.close()
            conn = None # Đặt lại biến
            print("Đã đóng Kết nối CSDL.")
        except Exception as e:
            print(f"Lỗi khi đóng Kết nối: {e}")