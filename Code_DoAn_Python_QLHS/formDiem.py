from tkinter import *
from tkinter import messagebox, ttk
import pyodbc
import Connect as db
import formHocSinh as hs 
import formMeNu as mn 
import formThemMonHoc as mh
import csv 
from tkinter import filedialog 

# Biến toàn cục cho widgets và data maps
tree = None
cbHS = None # Combobox cho Tên HS
cbMH = None # Combobox cho Tên MH
# Không cần dictionary vì sẽ tra cứu Mã khi CRUD


# ====== Hàm canh giữa cửa sổ ======
def center_window(win, w=100, h=500):
    ws = win.winfo_screenwidth()
    hs = win.winfo_screenheight()
    x = (ws // 2) - (w // 2)
    y = (hs // 2) - (h // 2)
    win.geometry(f'{w}x{h}+{x}+{y}')

# Xuất file form Điểm
def export_to_csv():
    """Xuất dữ liệu Treeview hiện tại sang file CSV.
    Nếu có dòng được chọn, chỉ xuất dòng đó. Ngược lại, xuất tất cả.
    """
    global tree

    # 1. Kiểm tra và lấy dữ liệu theo lựa chọn
    selected_items = tree.selection()
    data = []
    
    if selected_items:
        # Xuất chỉ học sinh được chọn
        for item in selected_items:
            data.append(tree.item(item, 'values'))
        export_mode = "các dòng đã chọn"
    else:
        # Xuất toàn bộ dữ liệu
        data = [tree.item(child, 'values') for child in tree.get_children()]
        export_mode = "toàn bộ"

    if not data:
        messagebox.showinfo("Thông báo", "Không có dữ liệu để xuất.")
        return

    # 2. Mở hộp thoại lưu file (chuyển lên sau khi biết có dữ liệu)
    filepath = filedialog.asksaveasfilename(
        defaultextension=".csv",
        filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
        title=f"Lưu file điểm ({export_mode.capitalize()}) Dưới Dạng CSV",
        initialfile="BaoCaoDiem.csv"
    )
    
    if not filepath:
        # Người dùng nhấn Cancel
        return

    try:
        # Tiêu đề cột (Phải khớp thứ tự trong Treeview)
        headers = ["Mã HS", "Tên Học Sinh", "Mã MH", "Tên Môn Học", "Thường Xuyên", "Giữa Kì", "Cuối Kì", "TBM"]
        
        # Ghi dữ liệu vào file CSV
        with open(filepath, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)

            # Ghi tiêu đề
            writer.writerow(headers)
            
            # Ghi dữ liệu
            writer.writerows(data)

        messagebox.showinfo("Thành công", f"Đã xuất {export_mode} dữ liệu học phí thành công ra:\n{filepath}")

    except Exception as e:
        messagebox.showerror("Lỗi", f"Lỗi khi xuất file CSV:\n{e}")

def start_Diem(menu_window, user_role):
    global tree, cbHS, cbMH

    root = Toplevel(menu_window)
    root.title("Quản Lý Điểm Học Sinh")
    root.minsize(1200, 500) # Tăng kích thước min để chứa nhiều cột điểm
    root.resizable(width=True, height=True)

    center_window(root, 1200, 500)

    menu_window.withdraw()

    # ======= Biến giao diện & Khóa chính cũ (MaHS, MaMH) =======
    stringTenHS = StringVar()  # Lưu TÊN Học Sinh (Chọn trên Combobox)
    stringTenMH = StringVar()  # Lưu TÊN Môn Học (Chọn trên Combobox)
    
    # Các biến mới cho từng loại điểm
    stringDiemTX = StringVar()
    stringDiemGK = StringVar()
    stringDiemCK = StringVar()
    stringTBM = StringVar() # TBM sẽ là read-only
    
    # Biến tạm giữ Khóa chính cũ khi sửa/xóa (Chỉ cần MaHS và MaMH)
    old_MaHS = StringVar()
    old_MaMH = StringVar()

    # ====== HÀM TÍNH TOÁN (Dựa trên dữ liệu SQL mẫu của bạn) ======
    def calculate_tbm(tx, gk, ck):
        """Tính TBM theo công thức có trọng số: (TX*1 + GK*2 + CK*3) / 6"""
        try:
            tx_val = float(tx)
            gk_val = float(gk)
            ck_val = float(ck)
            
            # Kiểm tra giá trị hợp lệ
            if not all(0 <= score <= 10 for score in [tx_val, gk_val, ck_val]):
                messagebox.showwarning("Lỗi tính toán", "Điểm phải nằm trong khoảng từ 0 đến 10.")
                return None
            
            # Tính TBM
            tbm = (tx_val * 1 + gk_val * 2 + ck_val * 3) / 6
            return round(tbm, 2)
        except ValueError:
            messagebox.showwarning("Lỗi nhập liệu", "Điểm phải là số hợp lệ.")
            return None


    # ======= HÀM CHỨC NĂNG CSDL VÀ RESET =======

    def load_combobox_data():
        """Tải danh sách Tên Học Sinh và Tên Môn Học vào Combobox."""
        try:
            # 1. Tải Tên Học Sinh
            db.cursor.execute("SELECT HoTenHS FROM HOCSINH ORDER BY HoTenHS")
            cbHS['values'] = [row[0] for row in db.cursor.fetchall()]
            
            # 2. Tải Tên Môn Học
            db.cursor.execute("SELECT TenMH FROM MONHOC ORDER BY TenMH")
            cbMH['values'] = [row[0] for row in db.cursor.fetchall()]
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi tải combobox: {e}")

    def load_scores():
        """Tải dữ liệu điểm lên Treeview (Truy vấn để lấy Tên HS/MH kèm theo Mã)."""
        try:
            # Truy vấn mới để lấy 4 cột điểm: ThuongXuyen, Giuaki, Cuoiki, TBM
            sql = """
            SELECT 
                d.MaHS, hs.HoTenHS, 
                d.MaMH, mh.TenMH, 
                d.ThuongXuyen, d.Giuaki, d.Cuoiki, d.TBM
            FROM DIEM d
            JOIN HOCSINH hs ON d.MaHS = hs.MaHS
            JOIN MONHOC mh ON d.MaMH = mh.MaMH
            ORDER BY d.MaHS, d.MaMH
            """
            db.cursor.execute(sql)
            rows = db.cursor.fetchall()
            
            tree.delete(*tree.get_children())
            for r in rows:
                # Hiển thị Tên trong Treeview (Vẫn cần giữ Mã trong Treeview cho item_selected)
                # Dữ liệu: MãHS, TênHS, MãMH, TênMH, TX, GK, CK, TBM
                tree.insert('', 'end', values=(r[0], r[1], r[2], r[3], r[4], r[5], r[6], r[7]))
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi tải dữ liệu:\n{e}")

    def _clear_entries():
        """Xóa trắng các trường nhập liệu và đặt lại giá trị mặc định."""
        stringTenHS.set("")
        stringTenMH.set("")
        stringDiemTX.set("")
        stringDiemGK.set("")
        stringDiemCK.set("")
        stringTBM.set("")
        
        old_MaHS.set("")
        old_MaMH.set("")
        
    def clear_form_after_crud():
        """Tải lại data, xóa chọn và reset form (Sử dụng cho Thêm/Sửa/Xóa)."""
        load_scores() 
        
        tree.unbind('<<TreeviewSelect>>')
        if tree.selection():
            tree.selection_remove(tree.selection())
        _clear_entries()
        tree.bind('<<TreeviewSelect>>', item_selected)

    def NhapMoi_Click():
        """Xóa chọn trên Treeview và reset form an toàn."""
        load_scores()
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
            
        # Dữ liệu: MãHS(0), TênHS(1), MãMH(2), TênMH(3), TX(4), GK(5), CK(6), TBM(7)
        mhs = values[0]
        ten_hs = values[1]
        mmh = values[2]
        ten_mh = values[3]
        diem_tx = values[4]
        diem_gk = values[5]
        diem_ck = values[6]
        tbm = values[7]
            
        # Gán Tên vào Combobox
        stringTenHS.set(ten_hs)
        stringTenMH.set(ten_mh)
        
        # Gán giá trị điểm
        stringDiemTX.set(diem_tx)
        stringDiemGK.set(diem_gk)
        stringDiemCK.set(diem_ck)
        stringTBM.set(tbm)
        
        # Lưu lại Khóa chính cũ (MaHS, MaMH)
        old_MaHS.set(mhs)
        old_MaMH.set(mmh)

    def get_ma_from_ten(ten, table, ten_col, ma_col):
        """Hàm tra cứu Mã từ Tên."""
        sql = f"SELECT {ma_col} FROM {table} WHERE {ten_col}=?"
        db.cursor.execute(sql, (ten,))
        row = db.cursor.fetchone()
        if not row:
            messagebox.showerror("Lỗi", f"Không tìm thấy {ten_col} '{ten}'.")
            return None
        return row[0]
    
    def addScore():
        """Thêm điểm mới vào CSDL."""
        ten_hs = stringTenHS.get().strip()
        ten_mh = stringTenMH.get().strip()
        tx = stringDiemTX.get().strip()
        gk = stringDiemGK.get().strip()
        ck = stringDiemCK.get().strip()

        if not all([ten_hs, ten_mh, tx, gk, ck]):
            messagebox.showwarning("Thiếu dữ liệu", "Vui lòng nhập đủ Tên HS, Tên MH và 3 loại điểm.")
            return

        # 1. Tính TBM
        tbm = calculate_tbm(tx, gk, ck)
        if tbm is None:
            return

        # 2. Tra cứu Mã
        mhs = get_ma_from_ten(ten_hs, 'HOCSINH', 'HoTenHS', 'MaHS')
        mmh = get_ma_from_ten(ten_mh, 'MONHOC', 'TenMH', 'MaMH')

        if mhs is None or mmh is None:
            return

        try:
            # SQL INSERT mới: (MaHS, MaMH) là Khóa chính, thêm 4 cột điểm
            sql = "INSERT INTO DIEM (MaHS, MaMH, ThuongXuyen, Giuaki, Cuoiki, TBM) VALUES (?, ?, ?, ?, ?, ?)"
            db.cursor.execute(sql, (mhs, mmh, tx, gk, ck, tbm))
            db.conn.commit()
            messagebox.showinfo("Thành công", f"Đã thêm điểm cho HS {ten_hs} - MH {ten_mh}. TBM: {tbm}")
            clear_form_after_crud() 
        except pyodbc.IntegrityError:
            messagebox.showerror("Lỗi", f"Điểm đã tồn tại cho HS {ten_hs}, MH {ten_mh}. Vui lòng SỬA.")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi thêm điểm:\n{e}")

    def updateScore():
        """Cập nhật điểm trong CSDL dựa trên khóa chính cũ (MaHS, MaMH)."""
        
        ten_hs = stringTenHS.get().strip()
        ten_mh = stringTenMH.get().strip()
        tx = stringDiemTX.get().strip()
        gk = stringDiemGK.get().strip()
        ck = stringDiemCK.get().strip()

        old_mhs = old_MaHS.get()
        old_mmh = old_MaMH.get()

        if not old_mhs:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn một dòng để Sửa.")
            return

        # 1. Tính TBM
        tbm = calculate_tbm(tx, gk, ck)
        if tbm is None:
            return
            
        # 2. Tra cứu Mã (cho giá trị mới)
        mhs = get_ma_from_ten(ten_hs, 'HOCSINH', 'HoTenHS', 'MaHS')
        mmh = get_ma_from_ten(ten_mh, 'MONHOC', 'TenMH', 'MaMH')

        if mhs is None or mmh is None:
            return

        # Kiểm tra nếu người dùng thay đổi MaHS/MaMH (thay đổi khóa chính)
        if (mhs, mmh) != (old_mhs, old_mmh):
            db.cursor.execute("SELECT 1 FROM DIEM WHERE MaHS=? AND MaMH=?", (mhs, mmh))
            if db.cursor.fetchone():
                messagebox.showerror("Lỗi Trùng Lặp", "Tổ hợp Mã HS và Mã MH mới này đã tồn tại trong hệ thống." \
                " Vui lòng chọn tổ hợp khác hoặc Sửa trực tiếp dòng đó.")
                return

        try:
            # SQL UPDATE mới: Cập nhật 4 cột điểm và có thể cập nhật MaHS/MaMH nếu khóa chính thay đổi
            sql = """
            UPDATE DIEM 
            SET MaHS = ?, MaMH = ?, ThuongXuyen = ?, Giuaki = ?, Cuoiki = ?, TBM = ?
            WHERE MaHS = ? AND MaMH = ?
            """
            db.cursor.execute(sql, (mhs, mmh, tx, gk, ck, tbm, old_mhs, old_mmh))
            db.conn.commit()
            messagebox.showinfo("Thành công", f"Đã cập nhật điểm cho HS {ten_hs}. TBM mới: {tbm}")
            clear_form_after_crud() 
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi cập nhật điểm:\n{e}")

    def deleteScore():
        """Xóa điểm trong CSDL dựa trên khóa chính kết hợp (MaHS, MaMH)."""
        mhs = old_MaHS.get()
        mmh = old_MaMH.get()
        ten_hs = stringTenHS.get().strip() # Lấy tên HS để hiển thị trong thông báo

        if not mhs:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn một dòng để Xóa.")
            return

        if not messagebox.askyesno("Xác nhận", f"Bạn có chắc chắn muốn xóa tất cả điểm của HS {ten_hs} trong môn {stringTenMH.get()}?"):
            return

        try:
            # SQL DELETE mới: Xóa dựa trên MaHS và MaMH
            sql = "DELETE FROM DIEM WHERE MaHS = ? AND MaMH = ?"
            db.cursor.execute(sql, (mhs, mmh))
            db.conn.commit()
            messagebox.showinfo("Thành công", "Đã xóa điểm.")
            clear_form_after_crud()
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi xóa điểm:\n{e}")

    def close_Diem_form():
        """Đóng form Điểm và hiển thị lại Menu."""
        root.destroy()
        menu_window.deiconify()
        
    def Them_Mon_Hoc():
        """Mở form Thêm Môn Học."""
        root.withdraw()
        mh.start_MonHoc(menu_window)

    # ======= GIAO DIỆN =======
    
    Label(root, text="QUẢN LÝ ĐIỂM HỌC SINH", fg="red", font=("Times New Roman", 20, "bold")).grid(row=0, column=0, columnspan=10, pady=20)
    
    root.grid_columnconfigure((0, 9), weight=1) 
    
    # Khu vực Combobox
    frame_cb = Frame(root)
    frame_cb.grid(row=1, column=1, columnspan=2, sticky='w', padx=10)
    
    Label(frame_cb, text="Tên học sinh:", font=("Times New Roman", 13)).pack(side=LEFT, padx=5, pady=5)
    cbHS = ttk.Combobox(frame_cb, width=22, textvariable=stringTenHS, state="readonly")
    cbHS.pack(side=LEFT)
    
    frame_cb2 = Frame(root)
    frame_cb2.grid(row=2, column=1, columnspan=2, sticky='w', padx=10)
    
    Label(frame_cb2, text="Tên môn học:", font=("Times New Roman", 13)).pack(side=LEFT, padx=5, pady=5)
    cbMH = ttk.Combobox(frame_cb2, width=22, textvariable=stringTenMH, state="readonly")
    cbMH.pack(side=LEFT)

    # Thêm môn học
    btn_them_mh = Button(frame_cb2, text="Thêm môn học", command=Them_Mon_Hoc, font=("Times New Roman", 8), bg="#4CAF50", 
                         fg="white", width=11)
    btn_them_mh.pack(side=LEFT, padx=10)
    
    # Khu vực Điểm (Row 3 & 4 cũ được gộp và mở rộng)
    
    frame_scores = Frame(root)
    frame_scores.grid(row=3, column=1, columnspan=6, sticky='w', pady=10)

    # Điểm Thường Xuyên
    Label(frame_scores, text="Điểm Thường Xuyên (TX):", font=("Times New Roman", 13)).pack(side=LEFT, padx=5)
    Entry(frame_scores, width=10, textvariable=stringDiemTX).pack(side=LEFT, padx=10)
    
    # Điểm Giữa Kì
    Label(frame_scores, text="Điểm Giữa Kì (GK):", font=("Times New Roman", 13)).pack(side=LEFT, padx=5)
    Entry(frame_scores, width=10, textvariable=stringDiemGK).pack(side=LEFT, padx=10)

    # Điểm Cuối Kì
    Label(frame_scores, text="Điểm Cuối Kì (CK):", font=("Times New Roman", 13)).pack(side=LEFT, padx=5)
    Entry(frame_scores, width=10, textvariable=stringDiemCK).pack(side=LEFT, padx=10)
    
    # TBM (Readonly - chỉ hiển thị)
    Label(frame_scores, text="TBM (Tính toán):", font=("Times New Roman", 13)).pack(side=LEFT, padx=5)
    Entry(frame_scores, width=10, textvariable=stringTBM, state="readonly").pack(side=LEFT, padx=10)


    # ======= Nút chức năng (Phân quyền) =======
    frameButton = Frame(root)
    # Tăng row number để tránh chồng lấn với frame_scores
    frameButton.grid(row=6, column=0, columnspan=10, pady=15) 
    
    Button(frameButton, text="Reset", command=NhapMoi_Click, bg="#2196F3", fg="white", width=10).pack(side=LEFT, padx=10)
    
    btn_them = Button(frameButton, text="Thêm", command=addScore, bg="#4CAF50", fg="white", width=10)
    btn_sua = Button(frameButton, text="Sửa", command=updateScore, bg="#FFC107", fg="black", width=10)
    btn_xoa = Button(frameButton, text="Xóa", command=deleteScore, bg="#F44336", fg="white", width=10)

    btn_them.pack(side=LEFT, padx=10)
    btn_sua.pack(side=LEFT, padx=10)
    btn_xoa.pack(side=LEFT, padx=10)

    btn_XuatFile = Button(frameButton, text="Xuất Điểm", command=export_to_csv, bg="#076DE2", fg="white", width=10)
    btn_XuatFile.pack(side=LEFT, padx=10)
    
    Button(frameButton, text="Thoát", command=close_Diem_form, bg="#9E9E9E", fg="white", width=10).pack(side=LEFT, padx=10)

    # ÁP DỤNG PHÂN QUYỀN GIAO DIỆN
    if user_role != 'Admin':
        btn_them.config(state=DISABLED, relief=SUNKEN, bg="#ccc", fg="#666")
        btn_sua.config(state=DISABLED, relief=SUNKEN, bg="#ccc", fg="#666")
        btn_xoa.config(state=DISABLED, relief=SUNKEN, bg="#ccc", fg="#666")
        btn_them_mh.config(state=DISABLED, relief=SUNKEN, bg="#ccc", fg="#666")
        btn_XuatFile.config(state=DISABLED, relief=SUNKEN, bg="#ccc", fg="#666")
        

    # ======= Bảng dữ liệu (Treeview) =======
    
    # Cột mới: Thêm TX, GK, CK, TBM và bỏ LoaiDiem
    columns = ("MaHS", "HoTenHS", "MaMH", "TenMH", "ThuongXuyen", "Giuaki", "Cuoiki", "TBM")
    tree = ttk.Treeview(root, columns=columns, show="headings", height=10)
    
    # Cấu hình cột hiển thị
    tree.heading("MaHS", text="Mã HS")
    tree.column("MaHS", width=80, anchor=CENTER)

    tree.heading("HoTenHS", text="Tên Học Sinh")
    tree.column("HoTenHS", width=180, anchor='w')

    tree.heading("MaMH", text="Mã MH")
    tree.column("MaMH", width=80, anchor=CENTER)

    tree.heading("TenMH", text="Tên Môn Học")
    tree.column("TenMH", width=180, anchor='w')

    tree.heading("ThuongXuyen", text="Thường xuyên")
    tree.column("ThuongXuyen", width=80, anchor=CENTER)

    tree.heading("Giuaki", text="Giữa kì")
    tree.column("Giuaki", width=80, anchor=CENTER)

    tree.heading("Cuoiki", text="Cuối kì")
    tree.column("Cuoiki", width=80, anchor=CENTER)

    tree.heading("TBM", text="TBM")
    tree.column("TBM", width=80, anchor=CENTER)

    # Thay đổi vị trí Treeview (row 7 -> row 7)
    tree.grid(row=7, column=0, columnspan=10, padx=10, pady=10, sticky='nsew')

    # Thanh cuộn
    scroll_y = ttk.Scrollbar(root, orient=VERTICAL, command=tree.yview)
    scroll_x = ttk.Scrollbar(root, orient=HORIZONTAL, command=tree.xview)
    tree.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)
    scroll_y.grid(row=7, column=10, sticky='ns')
    scroll_x.grid(row=8, column=0, columnspan=10, sticky='ew')

    # Liên kết sự kiện click chuột
    tree.bind('<<TreeviewSelect>>', item_selected)
    
    root.protocol("WM_DELETE_WINDOW", close_Diem_form)

    # Cấu hình cho Treeview giãn nở
    root.grid_rowconfigure(7, weight=1)
    root.grid_columnconfigure((0, 9), weight=1)
    
    # ======= KẾT NỐI & TẢI DỮ LIỆU =======
    db.connect_db() # Đảm bảo connect_db() được gọi
    load_combobox_data()
    load_scores()