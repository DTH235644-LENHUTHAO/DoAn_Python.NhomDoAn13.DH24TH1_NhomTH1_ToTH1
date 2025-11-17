from tkinter import *
from tkinter import messagebox, ttk
import pyodbc
import Connect as db 
import csv 
from tkinter import filedialog 

# Biến toàn cục cho widgets và data
tree = None
cbHS = None 
hs_name_to_id = {} 

# ====== Hàm canh giữa cửa sổ ======
def center_window(win, w=1000, h=500):
    ws = win.winfo_screenwidth()
    hs = win.winfo_screenheight()
    x = (ws // 2) - (w // 2)
    y = (hs // 2) - (h // 2)
    win.geometry(f'{w}x{h}+{x}+{y}')

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
        title=f"Lưu Báo Cáo Học Phí ({export_mode.capitalize()}) Dưới Dạng CSV",
        initialfile="BaoCaoHocPhi.csv"
    )
    
    if not filepath:
        # Người dùng nhấn Cancel
        return

    try:
        # Tiêu đề cột (Phải khớp thứ tự trong Treeview)
        headers = ["Mã HP", "Mã HS", "Tên Học Sinh", "Học Phí", "Đã Đóng", "Còn Nợ", "Trạng Thái"]
        
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

def calculate_conno_and_status(hocphi, dadong):
    """Tính toán còn nợ và trạng thái, trả về (conno, trangthai)."""
    
    if isinstance(hocphi, str): hocphi = hocphi.replace(',', '')
    if isinstance(dadong, str): dadong = dadong.replace(',', '')
    
    try:
        hocphi = float(hocphi)
        dadong = float(dadong)
    except ValueError:
        return 0.0, "Lỗi định dạng số"
        
    conno = hocphi - dadong
    
    if conno <= 0:
        trangthai = "Đã đóng đủ"
        conno_hien_thi = 0.0 # Nếu đóng thừa, vẫn hiển thị nợ là 0
    elif conno == hocphi:
        trangthai = "Chưa đóng"
        conno_hien_thi = conno
    else:
        trangthai = "Chưa đủ"
        conno_hien_thi = conno
        
    return conno_hien_thi, trangthai

def start_HP(menu_window, user_role):
    global tree, cbHS, hs_name_to_id
    
    root = Toplevel(menu_window)
    root.title("Quản Lý Học Phí")
    root.minsize(1000, 500)

    center_window(root, 1000, 500)
    menu_window.withdraw()

    # ======= Biến giao diện =======
    stringMaHP = StringVar()
    stringTenHS = StringVar() 
    stringHocPhi = StringVar()
    stringDaDong = StringVar()
    stringConNo = StringVar() 
    stringTrangThai = StringVar()
    stringMaHS = StringVar() 
    
    old_MaHP = StringVar()

    # ======= HÀM CHỨC NĂNG CSDL VÀ RESET =======

    def load_combobox_data():
        """Tải danh sách Tên Học Sinh và mapping Mã/Tên."""
        global hs_name_to_id
        hs_name_to_id = {}
        try:
            db.cursor.execute("SELECT MaHS, HoTenHS FROM HOCSINH ORDER BY HoTenHS")
            rows = db.cursor.fetchall()
            
            names = []
            for maHS, tenHS in rows:
                names.append(tenHS)
                hs_name_to_id[tenHS] = maHS
                
            cbHS['values'] = names
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi tải combobox: {e}")

    def load_hocphi():
        """Tải dữ liệu học phí lên Treeview. Lấy đủ 6 cột từ CSDL."""
        try:
            sql = """
            SELECT 
                hp.MaHP, hp.HocPhi, hp.DaDong, hp.ConNo, hp.TrangThai,
                hp.MaHS, hs.HoTenHS
            FROM HOCPHI hp
            JOIN HOCSINH hs ON hp.MaHS = hs.MaHS
            ORDER BY hp.MaHP
            """
            db.cursor.execute(sql)
            rows = db.cursor.fetchall()
            
            tree.delete(*tree.get_children())
            for r in rows:
                tree.insert('', 'end', values=(
                    r[0], # MaHP
                    r[5], # MaHS
                    r[6], # HoTenHS
                    f"{r[1]:.2f}", # HocPhi
                    f"{r[2]:.2f}", # DaDong
                    f"{r[3]:.2f}", # ConNo
                    r[4]           # TrangThai
                ))
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi tải dữ liệu:\n{e}")
            
    def update_conno_and_status(*args):
        """Cập nhật Còn Nợ và Trạng thái khi Học phí/Đã đóng thay đổi (Real-time)."""
        try:
            hocphi_str = stringHocPhi.get().strip()
            dadong_str = stringDaDong.get().strip()
            
            if not hocphi_str or not dadong_str:
                stringConNo.set("0.00")
                stringTrangThai.set("")
                return
            
            conno, trangthai = calculate_conno_and_status(hocphi_str, dadong_str)
            
            stringConNo.set(f"{conno:,.2f}") 
            stringTrangThai.set(trangthai)
            
        except ValueError:
            stringConNo.set("Lỗi")
            stringTrangThai.set("Lỗi định dạng")
        except Exception:
            stringConNo.set("Lỗi")
            stringTrangThai.set("Lỗi")
            
    def update_mahs_display(event=None):
        """Cập nhật Mã HS khi chọn Tên HS."""
        ten_hs = stringTenHS.get()
        mahs = hs_name_to_id.get(ten_hs, "")
        stringMaHS.set(mahs)

    def clear_form_after_crud():
        """Tải lại data, xóa chọn và reset form."""
        load_hocphi() 
        
        tree.unbind('<<TreeviewSelect>>')
        if tree.selection():
            tree.selection_remove(tree.selection())
            
        stringMaHP.set("")
        stringTenHS.set("")
        stringHocPhi.set("")
        stringDaDong.set("")
        stringConNo.set("")
        stringTrangThai.set("")
        stringMaHS.set("")
        old_MaHP.set("") 
        
        tree.bind('<<TreeviewSelect>>', item_selected)
        
    def NhapMoi_Click():
        clear_form_after_crud() 
        
    def item_selected(event):
        """Lấy dữ liệu từ Treeview khi người dùng click."""
        selected = tree.focus()
        if not selected: return
        
        values = tree.item(selected, 'values')
        if not values: return
            
        
        stringMaHP.set(values[0])
        stringMaHS.set(values[1])
        stringTenHS.set(values[2])
        stringHocPhi.set(values[3].replace(',', ''))
        stringDaDong.set(values[4].replace(',', ''))
        stringConNo.set(values[5])
        stringTrangThai.set(values[6])
        
        old_MaHP.set(values[0])

    def check_permission():
        """Kiểm tra vai trò người dùng."""
        if user_role != 'Admin':
            messagebox.showerror("Lỗi Phân Quyền", "Bạn không có quyền thực hiện thao tác này.")
            return False
        return True

    def addHocPhi():
        if not check_permission(): return

        mahp = stringMaHP.get().strip()
        ten_hs = stringTenHS.get().strip()
        
        try:
            hocphi_val = float(stringHocPhi.get().strip().replace(',', ''))
            dadong_val = float(stringDaDong.get().strip().replace(',', ''))
        except ValueError:
            messagebox.showerror("Lỗi", "Học Phí và Đã Đóng phải là số.")
            return

        if not all([mahp, ten_hs, str(hocphi_val), str(dadong_val)]):
            messagebox.showwarning("Thiếu dữ liệu", "Vui lòng nhập đủ Mã HP, Tên HS, Học Phí và Đã Đóng.")
            return
        
        if ten_hs not in hs_name_to_id:
            messagebox.showerror("Lỗi", "Tên học sinh không hợp lệ.")
            return
            
        mahs = hs_name_to_id[ten_hs]
        
        # <<< TÍNH TOÁN ConNo VÀ TrangThai TRƯỚC KHI LƯU >>>
        conno_val, trangthai = calculate_conno_and_status(hocphi_val, dadong_val)

        try:
            db.cursor.execute("SELECT 1 FROM HOCPHI WHERE MaHP=?", (mahp,))
            if db.cursor.fetchone():
                messagebox.showerror("Lỗi Trùng Lặp", f"Mã Học Phí '{mahp}' đã tồn tại.")
                return

            db.cursor.execute("SELECT 1 FROM HOCPHI WHERE MaHS=?", (mahs,))
            if db.cursor.fetchone():
                messagebox.showerror("Lỗi Trùng Lặp", f"Học sinh '{ten_hs}' đã có thông tin học phí.")
                return

            # CÂU LỆNH INSERT CÓ THÊM CỘT CONNO
            sql = "INSERT INTO HOCPHI (MaHP, HocPhi, DaDong, ConNo, TrangThai, MaHS) VALUES (?, ?, ?, ?, ?, ?)"
            db.cursor.execute(sql, (mahp, hocphi_val, dadong_val, conno_val, trangthai, mahs))
            db.conn.commit()
            messagebox.showinfo("Thành công", f"Đã thêm học phí cho HS {ten_hs}")
            clear_form_after_crud() 
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi thêm học phí:\n{e}")

    def updateHocPhi():
        if not check_permission(): return
            
        mahp = stringMaHP.get().strip()
        old_mahp = old_MaHP.get()

        if not old_mahp:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn một dòng để Sửa.")
            return
        
        ten_hs = stringTenHS.get().strip()
        
        try:
            hocphi_val = float(stringHocPhi.get().strip().replace(',', ''))
            dadong_val = float(stringDaDong.get().strip().replace(',', ''))
        except ValueError:
            messagebox.showerror("Lỗi", "Học Phí và Đã Đóng phải là số.")
            return

        if ten_hs not in hs_name_to_id:
            messagebox.showerror("Lỗi", "Tên học sinh không hợp lệ.")
            return
            
        mahs = hs_name_to_id[ten_hs]
        
        # <<< TÍNH TOÁN ConNo VÀ TrangThai TRƯỚC KHI LƯU >>>
        conno_val, trangthai = calculate_conno_and_status(hocphi_val, dadong_val)

        try:
            if mahp != old_mahp:
                db.cursor.execute("SELECT 1 FROM HOCPHI WHERE MaHP=?", (mahp,))
                if db.cursor.fetchone():
                    messagebox.showerror("Lỗi Trùng Lặp", f"Mã Học Phí mới '{mahp}' đã tồn tại.")
                    return
            
            # CÂU LỆNH UPDATE CÓ THÊM CỘT CONNO
            sql = """
            UPDATE HOCPHI 
            SET MaHP = ?, HocPhi = ?, DaDong = ?, ConNo = ?, TrangThai = ?, MaHS = ? 
            WHERE MaHP = ?
            """
            db.cursor.execute(sql, (mahp, hocphi_val, dadong_val, conno_val, trangthai, mahs, old_mahp))
            db.conn.commit()
            messagebox.showinfo("Thành công", f"Đã cập nhật học phí {mahp}.")
            clear_form_after_crud() 
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi cập nhật học phí:\n{e}")

    def deleteHocPhi():
        if not check_permission(): return
            
        mahp = old_MaHP.get()
        ten_hs = stringTenHS.get().strip()

        if not mahp:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn một dòng để Xóa.")
            return

        if not messagebox.askyesno("Xác nhận", f"Bạn có chắc chắn muốn xóa học phí Mã {mahp} của HS {ten_hs}?"):
            return

        try:
            sql = "DELETE FROM HOCPHI WHERE MaHP = ?"
            db.cursor.execute(sql, (mahp,))
            db.conn.commit()
            messagebox.showinfo("Thành công", "Đã xóa học phí.")
            clear_form_after_crud()
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi xóa học phí:\n{e}")

    def close_HP_form():
        root.destroy()
        menu_window.deiconify()
        
    # ======= GIAO DIỆN =======
    
    Label(root, text="QUẢN LÝ THÔNG TIN HỌC PHÍ", fg="red", font=("Times New Roman", 20, "bold")).grid(row=0, column=0, 
                                                                                                       columnspan=4, pady=20)
    
    root.grid_columnconfigure((0, 3), weight=1) 
    
    # Row 1: Mã HP
    Label(root, text="Mã Học Phí:", font=("Times New Roman", 13)).grid(row=1, column=0, sticky='e', padx=10, pady=5)
    Entry(root, width=25, textvariable=stringMaHP).grid(row=1, column=1, sticky='w')
    
    # Row 2: Tên HS
    Label(root, text="Tên Học Sinh:", font=("Times New Roman", 13)).grid(row=2, column=0, sticky='e', padx=10, pady=5)
    cbHS = ttk.Combobox(root, width=22, textvariable=stringTenHS, state="readonly")
    cbHS.grid(row=2, column=1, sticky='w')
    cbHS.bind('<<ComboboxSelected>>', update_mahs_display) 
    
    # Row 2, Cột 2: Mã HS (Hiển thị)
    Label(root, text="Mã Học Sinh:", font=("Times New Roman", 13)).grid(row=2, column=2, sticky='e', padx=10, pady=5)
    Entry(root, width=25, textvariable=stringMaHS, state='readonly').grid(row=2, column=3, sticky='w') 
    
    # Row 3: Học Phí
    Label(root, text="Học Phí (VNĐ):", font=("Times New Roman", 13)).grid(row=3, column=0, sticky='e', padx=10, pady=5)
    Entry(root, width=25, textvariable=stringHocPhi).grid(row=3, column=1, sticky='w')
    stringHocPhi.trace_add("write", update_conno_and_status) 
    
    # Row 3, Cột 2: Còn Nợ
    Label(root, text="Còn Nợ (VNĐ):", font=("Times New Roman", 13)).grid(row=3, column=2, sticky='e', padx=10, pady=5)
    Entry(root, width=25, textvariable=stringConNo, state='readonly', fg="#FF4500", font=("Times New Roman", 13, "bold")).grid(row=3, column=3, sticky='w') 

    # Row 4: Đã Đóng
    Label(root, text="Đã Đóng (VNĐ):", font=("Times New Roman", 13)).grid(row=4, column=0, sticky='e', padx=10, pady=5)
    Entry(root, width=25, textvariable=stringDaDong).grid(row=4, column=1, sticky='w')
    stringDaDong.trace_add("write", update_conno_and_status) 

    # Row 4, Cột 2: Trạng Thái
    Label(root, text="Trạng Thái:", font=("Times New Roman", 13)).grid(row=4, column=2, sticky='e', padx=10, pady=5)
    Entry(root, width=25, textvariable=stringTrangThai, state='readonly', fg="blue",
           font=("Times New Roman", 13, "bold")).grid(row=4, column=3, sticky='w')


    # ======= Nút chức năng (Phân quyền) =======
    frameButton = Frame(root)
    frameButton.grid(row=6, column=0, columnspan=4, pady=15) 
    
    Button(frameButton, text="Reset", command=NhapMoi_Click, bg="#2196F3", fg="white", width=10).pack(side=LEFT, padx=10)
    
    btn_them = Button(frameButton, text="Thêm", command=addHocPhi, bg="#4CAF50", fg="white", width=10)
    btn_sua = Button(frameButton, text="Sửa", command=updateHocPhi, bg="#FFC107", fg="black", width=10)
    btn_xoa = Button(frameButton, text="Xóa", command=deleteHocPhi, bg="#F44336", fg="white", width=10)

    btn_them.pack(side=LEFT, padx=10)
    btn_sua.pack(side=LEFT, padx=10)
    btn_xoa.pack(side=LEFT, padx=10)

    # Nút Xuất CSV mới (liên kết với hàm đã cập nhật)
    btn_XuatFile = Button(frameButton, text="Xuất HP", command=export_to_csv, bg="#076DE2", fg="white", width=10)
    btn_XuatFile.pack(side=LEFT, padx=10)
    
    Button(frameButton, text="Thoát", command=close_HP_form, bg="#9E9E9E", fg="white", width=10).pack(side=LEFT, padx=10)

    # ÁP DỤNG PHÂN QUYỀN GIAO DIỆN
    if user_role != 'Admin':
        btn_them.config(state=DISABLED, relief=SUNKEN, bg="#ccc", fg="#666")
        btn_sua.config(state=DISABLED, relief=SUNKEN, bg="#ccc", fg="#666")
        btn_xoa.config(state=DISABLED, relief=SUNKEN, bg="#ccc", fg="#666")
        btn_XuatFile.config(state=DISABLED, relief=SUNKEN, bg="#ccc", fg="#666")


    # ======= Bảng dữ liệu (Treeview) =======
    
    columns = ("MaHP", "MaHS", "HoTenHS", "HocPhi", "DaDong", "ConNo", "TrangThai") 
    tree = ttk.Treeview(root, columns=columns, show="headings", height=10)
    
    # Cấu hình cột hiển thị
    tree.heading("MaHP", text="Mã HP"); tree.column("MaHP", width=80, anchor=CENTER)
    tree.heading("MaHS", text="Mã HS"); tree.column("MaHS", width=80, anchor=CENTER)
    tree.heading("HoTenHS", text="Tên Học Sinh"); tree.column("HoTenHS", width=150, anchor='w')
    tree.heading("HocPhi", text="Học Phí"); tree.column("HocPhi", width=120, anchor=E)
    tree.heading("DaDong", text="Đã Đóng"); tree.column("DaDong", width=120, anchor=E)
    tree.heading("ConNo", text="Còn Nợ"); tree.column("ConNo", width=120, anchor=E) 
    tree.heading("TrangThai", text="Trạng Thái"); tree.column("TrangThai", width=120, anchor=CENTER)

    tree.grid(row=7, column=0, columnspan=4, padx=10, pady=10, sticky='nsew')

    # Thanh cuộn
    scroll_y = ttk.Scrollbar(root, orient=VERTICAL, command=tree.yview)
    scroll_x = ttk.Scrollbar(root, orient=HORIZONTAL, command=tree.xview)
    tree.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)
    scroll_y.grid(row=7, column=4, sticky='ns')
    scroll_x.grid(row=8, column=0, columnspan=4, sticky='ew')

    # Cấu hình cho Treeview giãn nở
    root.grid_rowconfigure(7, weight=1)
    
    # Liên kết sự kiện click chuột
    tree.bind('<<TreeviewSelect>>', item_selected)
    root.protocol("WM_DELETE_WINDOW", close_HP_form)

    # ======= KẾT NỐI & TẢI DỮ LIỆU =======
    db.connect_db()
    load_combobox_data()
    load_hocphi()