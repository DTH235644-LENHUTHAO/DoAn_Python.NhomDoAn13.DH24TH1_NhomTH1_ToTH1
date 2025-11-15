from tkinter import*
from tkinter import messagebox
from pyodbc import*
from PIL import Image, ImageTk
import Connect as db
import formHocSinh as hs
import formMeNu as mn



def center_window(win, w=500, h=350):
    ws = win.winfo_screenwidth()
    hs = win.winfo_screenheight()
    x = (ws // 2) - (w // 2)
    y = (hs // 2) - (h // 2)
    win.geometry(f'{w}x{h}+{x}+{y}')

def login_system():
    # Lấy dữ liệu từ ô nhập liệu
    user_id = stringUserID.get()
    password = stringMK.get()

    
    # 1. Kiểm tra kết nối CSDL
    if db.conn is None or db.cursor is None:
        db.connect_db() # Thử kết nối lại
        if db.conn is None:
            messagebox.showerror("Lỗi", "Không thể kết nối CSDL. Vui lòng kiểm tra lại.")
            return

    # 2. Kiểm tra dữ liệu nhập vào
    if not user_id or not password:
        messagebox.showwarning("Cảnh báo", "Vui lòng nhập đầy đủ UserID và Mật khẩu.")
        return

    try:
        # 3. Thực hiện truy vấn kiểm tra tài khoản
        # Sử dụng tham số (?) để ngăn chặn lỗi SQL Injection
        sql = "SELECT VaiTro FROM NGUOIDUNG WHERE UserID = ? AND MatKhau = ?"
        db.cursor.execute(sql, (user_id, password))
        
        # Lấy kết quả (chỉ cần lấy 1 dòng)
        result = db.cursor.fetchone()

        #count=result[0] if result else 0

        if result:
            vaitro = result[0]  # Lưu vai trò người dùng vào biến toàn cục trong formMeNu
            # ĐĂNG NHẬP THÀNH CÔNG
            messagebox.showinfo("Thành công", f"Đăng nhập thành công! Chào mừng {user_id} với vai trò {vaitro}.")
            
            # --- CHUYỂN ĐẾN FORM KHÁC TẠI ĐÂY ---
            root.withdraw()  # Ẩn form đăng nhập
            # Ví dụ: đóng form đăng nhập và mở form chính
            mn.create_main_menu_manual(root, vaitro)
            #hs.start_HS()
            stringUserID.set("")  # Xóa dữ liệu sau khi đăng nhập thành công
            stringMK.set("")  # Xóa mật khẩu
            # open_main_form(vaitro) # Gọi hàm mở cửa sổ chính
        
        else:
            # ĐĂNG NHẬP THẤT BẠI
            messagebox.showerror("Lỗi", "UserID hoặc Mật khẩu không chính xác.")

    except Exception as e:
        messagebox.showerror("Lỗi CSDL", f"Lỗi truy vấn CSDL:\n{e}")

root = Tk()

stringUserID = StringVar()
stringMK = StringVar()

root.title("ĐĂNG NHẬP HỆ THỐNG")
root.minsize(500, 350)
root.resizable(height=True, width=True) 
center_window(root, 500, 350)
# --- Tạo Frame chính cho nội dung để dễ dàng căn giữa ---
main_frame = Frame(root, padx=20, pady=20)
main_frame.pack(expand=True, fill='both') # Căn giữa và lấp đầy root

# Tạo hình nền
    # THAY ĐỔI ĐƯỜNG DẪN NÀY
# --- Tiêu đề ---
Label(main_frame,
      text="ĐĂNG NHẬP HỆ THỐNG",
      fg="#0A6847", # Màu xanh lá đậm hoặc màu bạn thích
      font=("Times New Roman", 24, "bold"),
      pady=15
      ).grid(row=0, column=0, columnspan=2, sticky="nsew")

# --- Form Đăng nhập ---
# Cột 0 là Label (căn phải) | Cột 1 là Entry (căn trái/lấp đầy)
# Cấu hình grid column để Entry có thể giãn rộng hơn
main_frame.grid_columnconfigure(0, weight=1)
main_frame.grid_columnconfigure(1, weight=3)


# Label UserID
Label(main_frame,
      text="👤 UserID:",
      font=("Arial", 14),
      padx=10,
      pady=10
      ).grid(row=1, column=0, sticky="e") # Căn phải

# Entry UserID
Entry(main_frame,
      width=30, # Tăng chiều rộng để trông đẹp hơn
      textvariable=stringUserID,
      font=("Arial", 14),
      bd=2, # Độ dày viền
      relief="groove" # Kiểu viền
      ).grid(row=1, column=1, padx=(0, 10), pady=10, sticky="ew") # Căn trái, lấp đầy theo chiều ngang, thêm padx bên phải

# Label Mật khẩu
Label(main_frame,
      text="🔒 Mật khẩu:",
      font=("Arial", 14),
      padx=10,
      pady=10
      ).grid(row=2, column=0, sticky="e") # Căn phải

# Entry Mật khẩu
Entry(main_frame,
      width=30,
      textvariable=stringMK,
      font=("Arial", 14),
      show="*", # Ẩn ký tự mật khẩu
      bd=2,
      relief="groove"
      ).grid(row=2, column=1, padx=(0, 10), pady=10, sticky="ew") # Căn trái, lấp đầy theo chiều ngang

# --- Khung chứa Button ---
frameButton = Frame(main_frame, pady=20)
frameButton.grid(row=3, column=0, columnspan=2) # Đặt Frame button bên dưới, chiếm 2 cột

# Button Đăng nhập
Button(frameButton,
       text="Đăng nhập",
       command=login_system,
       font=("Arial", 14, "bold"),
       bg="#3CB371", # Màu nền xanh
       fg="white", # Màu chữ trắng
       activebackground="#2E8B57",
       width=12,
       cursor="hand2"
       ).pack(side=LEFT, padx=15)

# Button Thoát
Button(frameButton,
       text="Thoát",
       command=root.quit,
       font=("Arial", 14),
       bg="#DC3545", # Màu nền đỏ
       fg="white",
       activebackground="#C82333",
       width=12,
       cursor="hand2"
       ).pack(side=LEFT, padx=15)

db.close_db()
root.mainloop()
# Đóng kết nối CSDL khi thoát chương trình
