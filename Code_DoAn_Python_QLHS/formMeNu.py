from tkinter import *
from tkinter import messagebox, ttk
from tkcalendar import DateEntry
from datetime import date
import pyodbc
import Connect as db  # file Connect.py chứa connect_db()
import formHocSinh as hs  
import formDiem as diem
import formHocPhi as hp
import formLopHoc as lh
import formTimKiemHS as timkiem


menu_vaitro = ""  # Biến toàn cục lưu vai trò người dùng
# Hàm tạo cửa sổ Menu chính

def center_window(win, w=1200, h=550):
    ws = win.winfo_screenwidth()
    hs = win.winfo_screenheight()
    x = (ws // 2) - (w // 2)
    y = (hs // 2) - (h // 2)
    win.geometry(f'{w}x{h}+{x}+{y}')

def create_main_menu_manual(master_root,vaitro):
    global menu_vaitro
    menu_vaitro = vaitro
    menu_root = Toplevel(master_root)
    menu_root.title("HỆ THỐNG QUẢN LÝ HỌC SINH")
    menu_root.minsize(1200, 550) 
    center_window(menu_root, 1200, 550)
    menu_root.resizable(height=False, width=False) 

    def DangXuat(menu_root):
        """Đăng xuất khỏi hệ thống và đóng kết nối CSDL."""
        if messagebox.askyesno("Xác nhận", "Bạn có chắc muốn đăng xuất không?"):
            db.close_db()  # Đóng kết nối CSDL
            menu_root.destroy()  # Đóng cửa sổ Menu chính
            master_root.deiconify()
              # Hiện lại cửa sổ đăng nhập


    def open_hoc_sinh_form(menu_root):
        """Mở form Quản lý Học Sinh."""
        
        # Giả sử bạn có hàm start_HS() trong formHocSinh.py
        # hs.start_HS() 
        menu_root.withdraw() 
        hs.start_HS(menu_root, menu_vaitro)
        #menu_root.destroy()
        
    # Hàm sẽ được gọi khi bạn nhấn nút "Điểm"
    def open_diem_form(menu_root):
        """Mở form Quản lý Điểm."""
        menu_root.withdraw()
        diem.start_Diem(menu_root,menu_vaitro)

    # Hàm sẽ được gọi khi bạn nhấn nút "Học Phí"
    def open_hoc_phi_form(menu_root):
        """Mở form Quản lý Học Phí."""
        menu_root.withdraw()
        hp.start_HP(menu_root, menu_vaitro)
        # Thêm code để mở form Học Phí tại đây

    # Hàm sẽ được gọi khi bạn nhấn nút "Lớp Học"
    def open_lop_hoc_form(menu_root):
        """Mở form Quản lý Lớp Học."""
        menu_root.withdraw()
        lh.start_Lop(menu_root, menu_vaitro)

    def open_tim_kiem_form(menu_root):
        """Mở form Tìm Kiếm Học Sinh."""
        menu_root.withdraw()
        timkiem.start_TimKiem(menu_root, menu_vaitro)

    
    # Thiết lập màu nền
    menu_root.config(bg="#F0F8FF") # Màu nền nhẹ nhàng
    
    # --- Tiêu đề Chính ---
    Label(menu_root,
          text="TRANG CHỦ",
          fg="#0A6847",
          bg="#F0F8FF",
          font=("Times New Roman", 26, "bold"),
          pady=30
          ).pack(pady=(20, 10))

    # --- Frame chứa các Button Chức năng ---
    button_frame = Frame(menu_root, bg="#F0F8FF")
    button_frame.pack(pady=20, padx=20)
    
    # Cấu hình grid column để các nút giãn đều
    button_frame.grid_columnconfigure(0, weight=1)
    button_frame.grid_columnconfigure(1, weight=1)
    button_frame.grid_columnconfigure(2, weight=1)

    # --- Button Học Sinh ---
    Button(button_frame,
           text="👨‍🎓\nQuản Lý Học Sinh",
           command=lambda: open_hoc_sinh_form(menu_root), # Truyền menu_root vào hàm nếu muốn đóng sau đó
           font=("Arial", 16, "bold"),
           bg="#3CB371", # Màu xanh lá
           fg="white",
           width=18,
           height=4,
           bd=5,
           relief=RAISED,
           cursor="hand2"
           ).grid(row=0, column=0, padx=15, pady=15)

    # --- Button Điểm ---
    Button(button_frame,
           text="💯\nQuản Lý Điểm",
           command=lambda: open_diem_form(menu_root),
           font=("Arial", 16, "bold"),
           bg="#1E90FF", # Màu xanh dương
           fg="white",
           width=18,
           height=4,
           bd=5,
           relief=RAISED,
           cursor="hand2"
           ).grid(row=0, column=1, padx=15, pady=15)

    # --- Button Học Phí ---
    Button(button_frame,
           text="💲\nQuản Lý Học Phí",
           command=lambda: open_hoc_phi_form(menu_root),
           font=("Arial", 16, "bold"),
           bg="#FFD700", # Màu vàng/gold
           fg="black", # Đổi màu chữ cho dễ nhìn
           width=18,
           height=4,
           bd=5,
           relief=RAISED,
           cursor="hand2"
           ).grid(row=0, column=2, padx=15, pady=15)

    #--- Button Lớp Học ---
    Button(button_frame,
           text="🏫\nQuản Lý Lớp Học",
           command=lambda: open_lop_hoc_form(menu_root),
           font=("Arial", 16, "bold"),
           bg="#FF8C00", # Màu cam đậm
           fg="white",
           width=18,
           height=4,
           bd=5,
           relief=RAISED,
           cursor="hand2"
           ).grid(row=0, column=3, padx=15, pady=15)
    

    Button(menu_root,
           text="🔍🔍 Tìm Kiếm",
           command=lambda: open_tim_kiem_form(menu_root),
           font=("Arial", 12),
           bg="#DC3545", # Màu đỏ
           fg="white",
           width=14,
           height=2,
           cursor="hand2"
           ).pack(pady=20)
    
    # --- Button Đăng Xuất ---
    Button(menu_root,
           text="🚪 Đăng Xuất",
           command=lambda: DangXuat(menu_root), # Đóng cửa sổ Menu
           font=("Arial", 12),
           bg="#DC3545", # Màu đỏ
           fg="white",
           width=15,
           cursor="hand2"
           ).pack(pady=20)
    

    menu_root.protocol("WM_DELETE_WINDOW", menu_root.destroy) # Xử lý khi nhấn nút X
    menu_root.mainloop()

# Nếu bạn chạy file này độc lập để test
if __name__ == '__main__':
    
    create_main_menu_manual()
    