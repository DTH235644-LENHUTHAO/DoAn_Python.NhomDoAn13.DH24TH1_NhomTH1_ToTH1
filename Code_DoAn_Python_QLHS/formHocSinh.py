from tkinter import *
from tkinter import messagebox, ttk
from tkcalendar import DateEntry
from datetime import date
import pyodbc
import Connect as db  
import formMeNu as mn  
import formThemDiaChi as dc  

# ====== Hàm canh giữa cửa sổ ======
def center_window(win, w=1200, h=600):
    ws = win.winfo_screenwidth()
    hs = win.winfo_screenheight()
    x = (ws // 2) - (w // 2)
    y = (hs // 2) - (h // 2)
    win.geometry(f'{w}x{h}+{x}+{y}')

def start_HS(menu_window, vaitro):
    root = Toplevel(menu_window)
    root.title("Quản Lý Học Sinh")
    root.minsize(1200, 600)

    center_window(root, 1200, 600)
    menu_window.withdraw()
    # ======= Biến giao diện =======
    stringMaHS = StringVar()
    stringHoTen = StringVar()
    stringGioiTinh = StringVar()
    stringMail = StringVar()
    stringTenLop = StringVar()
    stringDiaChi = StringVar()

    # ======= HÀM CHỨC NĂNG =======
    def load_combobox_data():
        try:
            db.cursor.execute("SELECT DISTINCT TenLop FROM LOPHOC")
            cbLop['values'] = [row[0] for row in db.cursor.fetchall()]

            db.cursor.execute("SELECT DISTINCT DiaChi FROM DIACHI")
            cbDiaChi['values'] = [row[0] for row in db.cursor.fetchall()]
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi tải combobox: {e}")

    def load_students():
        try:
            sql = """
            SELECT 
                hs.MaHS, hs.HoTenHS, hs.NgaySinh, hs.GioiTinh, hs.Email,
                lh.TenLop, lh.Khoi, gv.TenGiaoVien, dc.DiaChi
            FROM HOCSINH hs
            JOIN LOPHOC lh ON hs.MaLop = lh.MaLop
            JOIN GVCN gv ON lh.MaGVCN = gv.MaGVCN
            JOIN DIACHI dc ON hs.MaDiaChi = dc.MaDiaChi
            """
            db.cursor.execute(sql)
            rows = db.cursor.fetchall()
            tree.delete(*tree.get_children())
            for r in rows:
                tree.insert('', 'end', values=(
                    r[0],
                    r[1],
                    r[2].strftime('%Y-%m-%d') if r[2] else '',
                    r[3],
                    r[4],
                    r[5],
                    r[6],
                    r[7],
                    r[8]
                ))
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi tải dữ liệu: {e}")

    def clear_form():
        load_students()
        tree.unbind('<<TreeviewSelect>>')
        tree.selection_remove(tree.selection())
        stringMaHS.set(value="")
        stringHoTen.set(value="")
        stringGioiTinh.set(value="")
        stringMail.set(value="")
        stringTenLop.set(value="")
        stringDiaChi.set(value="")
        date_ngaysinh.set_date(date.today())
        tree.bind('<<TreeviewSelect>>', item_selected)

        

    def item_selected(event):
        selected = tree.focus()
        if not selected:
            return
        values = tree.item(selected, 'values')
        if not values:
            return
        stringMaHS.set(values[0])
        stringHoTen.set(values[1])
        date_ngaysinh.set_date(values[2])
        stringGioiTinh.set(values[3])
        stringMail.set(values[4])
        stringTenLop.set(values[5])
        stringDiaChi.set(values[8])

    def addStudent():
        mahs = stringMaHS.get().strip()
        hoten = stringHoTen.get().strip()
        ngaysinh = date_ngaysinh.get_date()
        gioitinh = stringGioiTinh.get().strip()
        email = stringMail.get().strip()
        tenlop = stringTenLop.get().strip()
        diachi = stringDiaChi.get().strip()

        if not mahs or not hoten or not tenlop or not diachi:
            messagebox.showwarning("Thiếu dữ liệu", "Vui lòng nhập đủ thông tin bắt buộc.")
            return

        try:
            db.cursor.execute("SELECT MaLop FROM LOPHOC WHERE TenLop=?", (tenlop,))
            row = db.cursor.fetchone()
            if not row:
                messagebox.showerror("Lỗi", "Tên lớp không tồn tại.")
                return
            maLop = row[0]

            db.cursor.execute("SELECT MaDiaChi FROM DIACHI WHERE DiaChi=?", (diachi,))
            row = db.cursor.fetchone()
            if not row:
                messagebox.showerror("Lỗi", "Địa chỉ không tồn tại.")
                return
            maDC = row[0]

            sql = """INSERT INTO HOCSINH (MaHS, HoTenHS, NgaySinh, GioiTinh, Email, MaLop, MaDiaChi)
                     VALUES (?, ?, ?, ?, ?, ?, ?)"""
            db.cursor.execute(sql, (mahs, hoten, ngaysinh, gioitinh, email, maLop, maDC))
            db.conn.commit()
            messagebox.showinfo("Thành công", f"Đã thêm học sinh: {hoten}")
            load_students()
            clear_form()
        except pyodbc.IntegrityError:
            messagebox.showerror("Lỗi", f"Mã học sinh '{mahs}' đã tồn tại!")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi thêm học sinh:\n{e}")

    def updateStudent():
        mahs = stringMaHS.get().strip()
        if not mahs:
            messagebox.showwarning("Thiếu dữ liệu", "Vui lòng chọn học sinh cần sửa.")
            return
        hoten = stringHoTen.get().strip()
        ngaysinh = date_ngaysinh.get_date()
        gioitinh = stringGioiTinh.get().strip()
        email = stringMail.get().strip()
        tenlop = stringTenLop.get().strip()
        diachi = stringDiaChi.get().strip()
        try:
            db.cursor.execute("SELECT MaLop FROM LOPHOC WHERE TenLop=?", (tenlop,))
            maLop = db.cursor.fetchone()[0]
            db.cursor.execute("SELECT MaDiaChi FROM DIACHI WHERE DiaChi=?", (diachi,))
            maDC = db.cursor.fetchone()[0]
            sql = """UPDATE HOCSINH 
                     SET HoTenHS=?, NgaySinh=?, GioiTinh=?, Email=?, MaLop=?, MaDiaChi=? 
                     WHERE MaHS=?"""
            db.cursor.execute(sql, (hoten, ngaysinh, gioitinh, email, maLop, maDC, mahs))
            db.conn.commit()
            messagebox.showinfo("Thành công", f"Đã cập nhật học sinh: {hoten}")
            load_students()
            clear_form()
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi cập nhật:\n{e}")

    def deleteStudent():
        mahs = stringMaHS.get().strip()
        if not mahs:
            messagebox.showwarning("Thiếu dữ liệu", "Vui lòng chọn học sinh cần xóa.")
            return
        if not messagebox.askyesno("Xác nhận", f"Bạn có chắc muốn xóa học sinh {mahs}?"):
            return
        try:
            db.cursor.execute("DELETE FROM HOCSINH WHERE MaHS=?", (mahs,))
            db.conn.commit()
            messagebox.showinfo("Thành công", f"Đã xóa học sinh {mahs}")
            load_students()
            clear_form()
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi xóa học sinh:\n{e}")

    def close_HS_form():
        root.destroy()
        menu_window.deiconify()

    def Them_Dia_Chi():
        root.withdraw()
        dc.start_DiaChi(menu_window)

    # ======= GIAO DIỆN =======
    Label(root, text="THÔNG TIN HỌC SINH", fg="red", font=("Times New Roman", 20, "bold")).grid(row=0, column=0, columnspan=4, pady=10)

    Label(root, text="Mã học sinh:", font=("Times New Roman", 13)).grid(row=1, column=0, sticky='e', padx=10, pady=5)
    Entry(root, width=25, textvariable=stringMaHS).grid(row=1, column=1, sticky='w')

    Label(root, text="Họ tên:", font=("Times New Roman", 13)).grid(row=2, column=0, sticky='e', padx=10, pady=5)
    Entry(root, width=25, textvariable=stringHoTen).grid(row=2, column=1, sticky='w')

    Label(root, text="Ngày sinh:", font=("Times New Roman", 13)).grid(row=3, column=0, sticky='e', padx=10, pady=5)
    date_ngaysinh = DateEntry(root, width=22, background="darkblue", foreground="white", date_pattern="yyyy-mm-dd")
    date_ngaysinh.grid(row=3, column=1, sticky='w')

    Label(root, text="Giới tính:", font=("Times New Roman", 13)).grid(row=4, column=0, sticky='e', padx=10, pady=5)
    cbGT = ttk.Combobox(root, width=22, textvariable=stringGioiTinh, values=["Nam", "Nữ"], state="readonly")
    cbGT.grid(row=4, column=1, sticky='w')
    cbGT.set("Nam")

    Label(root, text="Email:", font=("Times New Roman", 13)).grid(row=5, column=0, sticky='e', padx=10, pady=5)
    Entry(root, width=25, textvariable=stringMail).grid(row=5, column=1, sticky='w')

    Label(root, text="Tên lớp:", font=("Times New Roman", 13)).grid(row=1, column=2, sticky='e', padx=10, pady=5)
    cbLop = ttk.Combobox(root, width=22, textvariable=stringTenLop, state="readonly")
    cbLop.grid(row=1, column=3, sticky='w')

    Label(root, text="Địa chỉ:", font=("Times New Roman", 13)).grid(row=2, column=2, sticky='e', padx=10, pady=5)
    cbDiaChi = ttk.Combobox(root, width=22, textvariable=stringDiaChi, state="readonly")
    cbDiaChi.grid(row=2, column=3, sticky='w')

    #Button(root, text="Thêm địa chỉ", command=lambda:Them_Dia_Chi(), font=("Arial", 12), bg="#4CAF50", 0fg="white", width=10,height=1).grid(row=3, column=2, padx=5, pady=5,sticky='w')
   
    """# ======= Nút chức năng =======
    frame_btn = Frame(root)
    frame_btn.grid(row=6, column=0, columnspan=4, pady=15)
    Button(frame_btn, text="Nhập mới", command=clear_form, bg="#2196F3", fg="white", width=10).grid(row=0, column=0, padx=5)
    Button(frame_btn, text="Thêm", command=addStudent, bg="#4CAF50", fg="white", width=10).grid(row=0, column=1, padx=5)
    Button(frame_btn, text="Sửa", command=updateStudent, bg="#FFC107", fg="black", width=10).grid(row=0, column=2, padx=5)
    Button(frame_btn, text="Xóa", command=deleteStudent, bg="#F44336", fg="white", width=10).grid(row=0, column=3, padx=5)
    Button(frame_btn, text="Thoát", command=close_HS_form, bg="#9E9E9E", fg="white", width=10).grid(row=0, column=4, padx=5)"""
    
    btn_them_dc = Button(root, text="Thêm địa chỉ", command=lambda:Them_Dia_Chi(),
                          font=("Times New Roman", 8), bg="#4CAF50", fg="white", width=11)
    btn_them_dc.grid(row=3, column=3, padx=10, pady=5,sticky='w')
    # ======= Nút chức năng =======
    frame_btn = Frame(root)
    frame_btn.grid(row=6, column=0, columnspan=4, pady=15)
    
    # Nút Nhập mới (Reset form)
    btn_nhapmoi=Button(frame_btn, text="Reset", command=clear_form, bg="#2196F3", fg="white", width=10)
    btn_nhapmoi.grid(row=0, column=0, padx=5)
    
    # Lưu tham chiếu các nút cần phân quyền
    btn_them = Button(frame_btn, text="Thêm", command=addStudent, bg="#4CAF50", fg="white", width=10)
    btn_sua = Button(frame_btn, text="Sửa", command=updateStudent, bg="#FFC107", fg="black", width=10)
    btn_xoa = Button(frame_btn, text="Xóa", command=deleteStudent, bg="#F44336", fg="white", width=10)

    # Hiển thị các nút
    btn_them.grid(row=0, column=1, padx=5)
    btn_sua.grid(row=0, column=2, padx=5)
    btn_xoa.grid(row=0, column=3, padx=5)

    btn_thoat = Button(frame_btn, text="Thoát", command=close_HS_form, bg="#9E9E9E", fg="white", width=10)
    btn_thoat.grid(row=0, column=4, padx=5)

    # 3. ÁP DỤNG PHÂN QUYỀN: Vô hiệu hóa nếu không phải Admin
    if vaitro != 'Admin':
        btn_them.config(state=DISABLED, relief=SUNKEN, bg="#ccc", fg="#666")
        btn_sua.config(state=DISABLED, relief=SUNKEN, bg="#ccc", fg="#666")
        btn_xoa.config(state=DISABLED, relief=SUNKEN, bg="#ccc", fg="#666")
        btn_them_dc.config(state=DISABLED, relief=SUNKEN, bg="#ccc", fg="#666")

    # ======= Bảng dữ liệu =======

    cols = ('MaHS', 'HoTenHS', 'NgaySinh', 'GioiTinh', 'Email', 'TenLop', 'Khoi', 'TenGVCN', 'DiaChi')
    tree = ttk.Treeview(root, columns=cols, show='headings')

    tree.heading('MaHS', text='Mã Học Sinh')
    tree.column('MaHS', width=80)

    tree.heading('HoTenHS', text='Họ Tên')
    tree.column('HoTenHS', width=130)

    tree.heading('NgaySinh', text='Ngày Sinh')
    tree.column('NgaySinh', width=80)

    tree.heading('GioiTinh', text='Giới Tính')
    tree.column('GioiTinh', width=80)

    tree.heading('Email', text='Email')
    tree.column('Email', width=150)

    tree.heading('TenLop', text='Tên Lớp')
    tree.column('TenLop', width=90)

    tree.heading('Khoi', text='Khối')
    tree.column('Khoi', width=80)

    tree.heading('TenGVCN', text='Tên GVCN')
    tree.column('TenGVCN', width=130)

    tree.heading('DiaChi', text='Địa Chỉ')
    tree.column('DiaChi', width=330)

    tree.grid(row=7, column=0, columnspan=4, padx=10, pady=10, sticky='nsew')

    scroll_y = ttk.Scrollbar(root, orient=VERTICAL, command=tree.yview)
    scroll_x = ttk.Scrollbar(root, orient=HORIZONTAL, command=tree.xview)
    tree.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)
    scroll_y.grid(row=7, column=4, sticky='ns')
    scroll_x.grid(row=8, column=0, columnspan=4, sticky='ew')
    #tree.pack(side=LEFT, fill=BOTH, expand=True)
    """vsb = ttk.Scrollbar(tree_frame, orient='vertical', command=tree.yview)
    hsb = ttk.Scrollbar(tree_frame, orient='horizontal', command=tree.xview)
    tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
    vsb.pack(side=RIGHT, fill=Y)
    hsb.pack(side=BOTTOM, fill=X)
    tree.pack(side=LEFT, fill=BOTH, expand=True)"""
    # Cho phép frame chứa tree mở rộng
    tree.grid_rowconfigure(0, weight=1)
    tree.grid_columnconfigure(0, weight=1)


    tree.bind('<<TreeviewSelect>>', item_selected)
    root.protocol("WM_DELETE_WINDOW", close_HS_form)

    # ======= KẾT NỐI & TẢI DỮ LIỆU =======
    db.connect_db()
    load_combobox_data()
    load_students()
