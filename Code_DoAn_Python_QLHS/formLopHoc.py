from tkinter import *
from tkinter import messagebox, ttk
import pyodbc
import Connect as db  # file Connect.py chứa connect_db()
import formMeNu as mn
import formThemGVCN as gvcn 


# Biến toàn cục cho widgets và data maps
tree = None
cbKhoi = None  # Combobox cho Khối (10, 11, 12)
cbGVCN = None  # Combobox cho Tên GVCN


# ====== Hàm canh giữa cửa sổ ======
def center_window(win, w=1000, h=500):
    ws = win.winfo_screenwidth()
    hs = win.winfo_screenheight()
    x = (ws // 2) - (w // 2)
    y = (hs // 2) - (h // 2)
    win.geometry(f'{w}x{h}+{x}+{y}')


def start_Lop(menu_window, user_role):
    global tree, cbKhoi, cbGVCN

    root = Toplevel(menu_window)
    root.title("Quản Lý Lớp Học")
    root.minsize(1000, 500)
    root.resizable(width=True, height=True)

    center_window(root, 1000, 500)
    menu_window.withdraw()

    # ======= Biến giao diện & Khóa chính cũ =======
    stringMaLop = StringVar()
    stringTenLop = StringVar()
    stringKhoi = StringVar()
    stringTenGVCN = StringVar()  # Lưu TÊN GVCN (Chọn trên Combobox)

    # Biến tạm giữ Khóa chính cũ khi sửa/xóa
    old_MaLop = StringVar()

    # Danh sách các lựa chọn Khối
    khoi_options = ["10", "11", "12"]

    # ======= HÀM HỖ TRỢ CSDL VÀ RESET =======

    def get_ma_from_ten(ten, ten_col, ma_col, table):
        """Hàm tra cứu Mã từ Tên (Ví dụ: TenGiaoVien -> MaGVCN)."""
        try:
            sql = f"SELECT {ma_col} FROM {table} WHERE {ten_col}=?"
            db.cursor.execute(sql, (ten,))
            row = db.cursor.fetchone()
            if not row:
                messagebox.showerror("Lỗi", f"Không tìm thấy {ten_col} '{ten}'.")
                return None
            return row[0]
        except Exception as e:
            messagebox.showerror("Lỗi CSDL", f"Lỗi tra cứu Mã: {e}")
            return None


    def load_combobox_data():
        """Tải danh sách Khối và Tên GVCN vào Combobox."""
        try:
            # 1. Tải Tên Giáo Viên Chủ Nhiệm (GVCN)
            # Giả định bảng GVCN có MaGVCN và TenGiaoVien
            db.cursor.execute("SELECT TenGiaoVien FROM GVCN ORDER BY TenGiaoVien")
            cbGVCN['values'] = [row[0] for row in db.cursor.fetchall()]

            # 2. Khối (Đã được định nghĩa cứng trong khoi_options)
            cbKhoi['values'] = khoi_options
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi tải combobox: {e}")


    def load_classes():
        """Tải dữ liệu lớp học lên Treeview (Truy vấn để lấy Tên GVCN, Điện thoại, Email)."""
        try:
            sql = """
            SELECT
                lh.MaLop, lh.TenLop, lh.Khoi, lh.MaGVCN, gv.TenGiaoVien, gv.DienThoai, gv.Email
            FROM LOPHOC lh
            JOIN GVCN gv ON lh.MaGVCN = gv.MaGVCN
            ORDER BY lh.Khoi, lh.TenLop
            """
            db.cursor.execute(sql)
            rows = db.cursor.fetchall()

            tree.delete(*tree.get_children())
            for r in rows:
                # values = (MaLop, TenLop, Khoi, MaGVCN, TenGiaoVien, DienThoai, Email)
                tree.insert('', 'end', values=(r[0], r[1], r[2], r[3], r[4], r[5], r[6]))
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi tải dữ liệu:\n{e}")


    def _clear_entries():
        """Chỉ xóa trắng các trường nhập liệu và đặt lại giá trị mặc định."""
        stringMaLop.set("")
        stringTenLop.set("")
        stringKhoi.set(khoi_options[0])  # Khối mặc định 10
        stringTenGVCN.set("")

        old_MaLop.set("")  # Reset khóa chính cũ


    def clear_form_after_crud():
        """Tải lại data, xóa chọn và reset form (Sử dụng cho Thêm/Sửa/Xóa)."""
        load_classes()

        tree.unbind('<<TreeviewSelect>>')
        if tree.selection():
            tree.selection_remove(tree.selection())
        _clear_entries()
        tree.bind('<<TreeviewSelect>>', item_selected)


    def NhapMoi_Click():
        """Xóa chọn trên Treeview và reset form an toàn (Sử dụng cho nút Nhập mới)."""
        load_combobox_data()  # Tải lại nếu có GVCN mới được thêm
        tree.unbind('<<TreeviewSelect>>')
        if tree.selection():
            tree.selection_remove(tree.selection())
        _clear_entries()
        tree.bind('<<TreeviewSelect>>', item_selected)


    def item_selected(event):
        """Lấy dữ liệu từ Treeview khi người dùng click."""
        selected = tree.focus()
        if not selected:
            return
        values = tree.item(selected, 'values')
        if not values:
            return

        # values = (MaLop, TenLop, Khoi, MaGVCN, TenGiaoVien, DienThoai, Email)
        ma_lop = values[0]
        ten_lop = values[1]
        khoi = str(values[2])
        ten_gvcn = values[4]  # Lấy Tên GVCN để hiển thị

        # Gán giá trị vào form
        stringMaLop.set(ma_lop)
        stringTenLop.set(ten_lop)
        stringKhoi.set(khoi)
        stringTenGVCN.set(ten_gvcn)

        # Lưu lại Khóa chính cũ
        old_MaLop.set(ma_lop)


    def addLop():
        """Thêm lớp học mới vào CSDL."""
        ma_lop = stringMaLop.get().strip()
        ten_lop = stringTenLop.get().strip()
        khoi = stringKhoi.get().strip()
        ten_gvcn = stringTenGVCN.get().strip()

        if not all([ma_lop, ten_lop, khoi, ten_gvcn]):
            messagebox.showwarning("Thiếu dữ liệu", "Vui lòng nhập đủ Mã Lớp, Tên Lớp, Khối và Tên GVCN.")
            return

        # 1. Tra cứu Mã GVCN từ Tên
        ma_gvcn = get_ma_from_ten(ten_gvcn, 'TenGiaoVien', 'MaGVCN', 'GVCN')

        if ma_gvcn is None:
            return

        try:
            sql = "INSERT INTO LOPHOC (MaLop, TenLop, Khoi, MaGVCN) VALUES (?, ?, ?, ?)"
            db.cursor.execute(sql, (ma_lop, ten_lop, khoi, ma_gvcn))
            db.conn.commit()
            messagebox.showinfo("Thành công", f"Đã thêm lớp: {ten_lop}")
            clear_form_after_crud()
        except pyodbc.IntegrityError:
            # Bắt lỗi khi Mã Lớp (MaLop) bị trùng Khóa chính
            messagebox.showerror("Lỗi", f"Mã Lớp '{ma_lop}' đã tồn tại!")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi thêm lớp:\n{e}")


    def updateLop():
        """Cập nhật thông tin lớp học trong CSDL."""

        ma_lop = stringMaLop.get().strip()  # Mã Lớp mới (không đổi)
        old_ma_lop = old_MaLop.get()  # Mã Lớp cũ (đã chọn)

        if not old_ma_lop:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn một dòng để Sửa.")
            return

        ten_lop = stringTenLop.get().strip()
        khoi = stringKhoi.get().strip()
        ten_gvcn = stringTenGVCN.get().strip()

        if ma_lop != old_ma_lop:
            messagebox.showerror("Lỗi", "Không được phép thay đổi Mã Lớp.")
            return

        # 1. Tra cứu Mã GVCN mới
        ma_gvcn = get_ma_from_ten(ten_gvcn, 'TenGiaoVien', 'MaGVCN', 'GVCN')

        if ma_gvcn is None:
            return

        try:
            sql = """
            UPDATE LOPHOC
            SET TenLop = ?, Khoi = ?, MaGVCN = ?
            WHERE MaLop = ?
            """
            db.cursor.execute(sql, (ten_lop, khoi, ma_gvcn, old_ma_lop))
            db.conn.commit()
            messagebox.showinfo("Thành công", f"Đã cập nhật lớp: {ten_lop}")
            clear_form_after_crud()
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi cập nhật lớp:\n{e}")


    def deleteLop():
        """Xóa lớp học trong CSDL."""
        ma_lop = old_MaLop.get()
        ten_lop = stringTenLop.get().strip()

        if not ma_lop:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn một dòng để Xóa.")
            return

        if not messagebox.askyesno("Xác nhận",
                                    f"Bạn có chắc chắn muốn xóa lớp {ten_lop} (Mã: {ma_lop})?\nLưu ý: Thao tác này có thể bị chặn nếu có dữ liệu liên quan (Học sinh)!"):
            return

        try:
            sql = "DELETE FROM LOPHOC WHERE MaLop = ?"
            db.cursor.execute(sql, (ma_lop,))
            db.conn.commit()
            messagebox.showinfo("Thành công", f"Đã xóa lớp {ten_lop}.")
            clear_form_after_crud()
        except pyodbc.IntegrityError:
            messagebox.showerror("Lỗi", "Không thể xóa lớp này vì có học sinh thuộc lớp này.")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi xóa lớp:\n{e}")


    def close_Lop_form():
        """Đóng form Lớp Học và hiển thị lại Menu."""
        root.destroy()
        menu_window.deiconify()


    def Them_GVCN():
        """Mở form Thêm GVCN và ẩn form hiện tại."""
        root.withdraw()
        gvcn.start_GiaoVien(menu_window)


    # ======= GIAO DIỆN =======

    Label(root, text="QUẢN LÝ LỚP HỌC", fg="red", font=("Times New Roman", 
                                        20, "bold")).grid(row=0, column=0, columnspan=7, pady=20) # Thay đổi columnspan

    root.grid_columnconfigure((0, 6), weight=1)  # Căn giữa nội dung, cột 6 là cột cuối cùng của nội dung

    # Row 1: Mã Lớp
    Label(root, text="Mã lớp:", font=("Times New Roman", 13)).grid(row=1, column=1, sticky='e', padx=10, pady=5)
    Entry(root, width=25, textvariable=stringMaLop).grid(row=1, column=2, sticky='w')

    # Row 2: Tên Lớp
    Label(root, text="Tên lớp:", font=("Times New Roman", 13)).grid(row=2, column=1, sticky='e', padx=10, pady=5)
    Entry(root, width=25, textvariable=stringTenLop).grid(row=2, column=2, sticky='w')

    # Row 3: Khối
    Label(root, text="Khối:", font=("Times New Roman", 13)).grid(row=3, column=1, sticky='e', padx=10, pady=5)
    cbKhoi = ttk.Combobox(root, width=22, textvariable=stringKhoi, values=khoi_options, state="readonly")
    cbKhoi.grid(row=3, column=2, sticky='w')
    cbKhoi.set(khoi_options[0])

    # Row 4: Tên GVCN (Sử dụng Frame để nhóm Combobox và Button)
    Label(root, text="Tên GVCN:", font=("Times New Roman", 13)).grid(row=4, column=1, sticky='e', padx=10, pady=5)

    frame_gvcn = Frame(root)
    frame_gvcn.grid(row=4, column=2, sticky='w', pady=5)

    cbGVCN = ttk.Combobox(frame_gvcn, width=22, textvariable=stringTenGVCN, state="readonly")
    cbGVCN.grid(row=0, column=0, sticky='w')

    # Nút Thêm GVCN
    btn_them_gvcn = Button(frame_gvcn, text="Thêm GVCN", command=Them_GVCN, font=("Times New Roman", 9), bg="#4CAF50",
                            fg="white", width=11)
    btn_them_gvcn.grid(row=0, column=1, padx=(5, 0), sticky='w')

    # ======= Nút chức năng (Phân quyền) =======
    frameButton = Frame(root)
    frameButton.grid(row=6, column=0, columnspan=7, pady=15) # Thay đổi columnspan

    Button(frameButton, text="Reset", command=NhapMoi_Click, bg="#2196F3", fg="white", width=10).pack(side=LEFT, padx=10)

    btn_them = Button(frameButton, text="Thêm", command=addLop, bg="#4CAF50", fg="white", width=10)
    btn_sua = Button(frameButton, text="Sửa", command=updateLop, bg="#FFC107", fg="black", width=10)
    btn_xoa = Button(frameButton, text="Xóa", command=deleteLop, bg="#F44336", fg="white", width=10)

    btn_them.pack(side=LEFT, padx=10)
    btn_sua.pack(side=LEFT, padx=10)
    btn_xoa.pack(side=LEFT, padx=10)

    Button(frameButton, text="Thoát", command=close_Lop_form, bg="#9E9E9E", fg="white", width=10).pack(side=LEFT, padx=10)

    # ÁP DỤNG PHÂN QUYỀN GIAO DIỆN
    if user_role != 'Admin':
        btn_them.config(state=DISABLED, relief=SUNKEN, bg="#ccc", fg="#666")
        btn_sua.config(state=DISABLED, relief=SUNKEN, bg="#ccc", fg="#666")
        btn_xoa.config(state=DISABLED, relief=SUNKEN, bg="#ccc", fg="#666")
        btn_them_gvcn.config(state=DISABLED, relief=SUNKEN, bg="#ccc", fg="#666")

    # ======= Bảng dữ liệu (Treeview) =======

    # Cập nhật danh sách 7 cột
    columns = ("MaLop", "TenLop", "Khoi", "MaGVCN", "TenGiaoVien", "DienThoai", "Email")
    tree = ttk.Treeview(root, columns=columns, show="headings", height=10)

    # Cấu hình cột hiển thị (điều chỉnh width để chứa thêm thông tin)
    tree.heading("MaLop", text="Mã Lớp")
    tree.column("MaLop", width=80, anchor=CENTER)
    tree.heading("TenLop", text="Tên Lớp")
    tree.column("TenLop", width=150, anchor='w')
    tree.heading("Khoi", text="Khối")
    tree.column("Khoi", width=60, anchor=CENTER)
    tree.heading("MaGVCN", text="Mã GVCN")
    tree.column("MaGVCN", width=80, anchor=CENTER)
    tree.heading("TenGiaoVien", text="Tên GVCN")
    tree.column("TenGiaoVien", width=150, anchor='w')
    
    # Cột mới 1: Điện Thoại
    tree.heading("DienThoai", text="Điện Thoại GVCN")
    tree.column("DienThoai", width=120, anchor=CENTER) 
    
    # Cột mới 2: Email
    tree.heading("Email", text="Email GVCN")
    tree.column("Email", width=200, anchor='w') 

    tree.grid(row=7, column=0, columnspan=7, padx=10, pady=10, sticky='nsew') # Thay đổi columnspan

    # Thanh cuộn
    scroll_y = ttk.Scrollbar(root, orient=VERTICAL, command=tree.yview)
    scroll_x = ttk.Scrollbar(root, orient=HORIZONTAL, command=tree.xview)
    tree.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)
    scroll_y.grid(row=7, column=7, sticky='ns') # Thay đổi column
    scroll_x.grid(row=8, column=0, columnspan=7, sticky='ew') # Thay đổi columnspan

    # Liên kết sự kiện click chuột
    tree.bind('<<TreeviewSelect>>', item_selected)

    root.protocol("WM_DELETE_WINDOW", close_Lop_form)

    # Cấu hình cho Treeview giãn nở
    root.grid_rowconfigure(7, weight=1)
    root.grid_columnconfigure(2, weight=1)  # Cột 2 chứa inputs và treeview cần giãn nở

    # ======= KẾT NỐI & TẢI DỮ LIỆU =======
    db.connect_db()
    load_combobox_data()
    load_classes()