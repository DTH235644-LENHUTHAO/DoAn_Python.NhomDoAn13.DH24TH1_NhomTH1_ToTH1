from tkinter import *
from tkinter import ttk, messagebox
import Connect as db      # file Connect.py có connect_db() và biến cursor, conn
import formHocSinh as hs  # import form học sinh để quay lại
import formMeNu as mn 
import formLopHoc as lh    # import form menu để quay lại


def center_window(win, w=850, h=500):
    ws = win.winfo_screenwidth()
    hs = win.winfo_screenheight()
    x = (ws // 2) - (w // 2)
    y = (hs // 2) - (h // 2)
    win.geometry(f'{w}x{h}+{x}+{y}')

def start_GiaoVien(menu_root=None):
    """Form quản lý bảng GVCN (Giáo Viên Chủ Nhiệm)"""
    db.connect_db()

    root = Toplevel()
    root.title("Quản Lý Giáo Viên Chủ Nhiệm")
    root.minsize(850, 500)
    root.resizable(width=True, height=True)
    center_window(root, 850, 500)
    #root.geometry("850x500")
    root.config(bg="#F0F8FF")

    # ======= Frame nhập dữ liệu =======
    frame_form = LabelFrame(root, text="Thông tin Giáo Viên", bg="#F0F8FF", padx=10, pady=10)
    frame_form.pack(fill="x", padx=10, pady=10)

    # Dòng 1
    Label(frame_form, text="Mã GVCN:", bg="#F0F8FF").grid(row=0, column=0, sticky="w", padx=5, pady=5)
    maGVCN_entry = Entry(frame_form, width=30)
    maGVCN_entry.grid(row=0, column=1, padx=5, pady=5)

    Label(frame_form, text="Tên Giáo Viên:", bg="#F0F8FF").grid(row=0, column=2, sticky="w", padx=20, pady=5)
    tenGV_entry = Entry(frame_form, width=30)
    tenGV_entry.grid(row=0, column=3, padx=5, pady=5)

    # Dòng 2
    Label(frame_form, text="Điện Thoại:", bg="#F0F8FF").grid(row=1, column=0, sticky="w", padx=5, pady=5)
    dienThoai_entry = Entry(frame_form, width=30)
    dienThoai_entry.grid(row=1, column=1, padx=5, pady=5)

    Label(frame_form, text="Email:", bg="#F0F8FF").grid(row=1, column=2, sticky="w", padx=20, pady=5)
    email_entry = Entry(frame_form, width=30)
    email_entry.grid(row=1, column=3, padx=5, pady=5)


    # ======= Hàm xử lý =======
    def load_data():
        """Tải danh sách GVCN từ CSDL lên Treeview."""
        try:
            # SỬ DỤNG N'...' ĐỂ XỬ LÝ DỮ LIỆU UNICODE/TIẾNG VIỆT CHO TÊN BẢNG/CỘT NẾU CẦN
            sql = "SELECT MaGVCN, TenGiaoVien, DienThoai, Email FROM GVCN"
            db.cursor.execute(sql)
            rows = db.cursor.fetchall()
            tree.delete(*tree.get_children())  # Xóa dữ liệu cũ trong Treeview
            for row in rows:
                tree.insert('', 'end', values=(row[0], row[1], row[2], row[3]))
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi tải dữ liệu: {e}")

    def clear_form():
        maGVCN_entry.delete(0, END)
        tenGV_entry.delete(0, END)
        dienThoai_entry.delete(0, END)
        email_entry.delete(0, END)
        tree.selection_remove(tree.selection())

    # === THÊM ===
    def them_giao_vien():
        ma = maGVCN_entry.get().strip()
        ten = tenGV_entry.get().strip()
        dt = dienThoai_entry.get().strip()
        mail = email_entry.get().strip()
        
        if not ma or not ten:
            messagebox.showwarning("Thiếu dữ liệu", "Vui lòng nhập Mã GVCN và Tên Giáo Viên.")
            return
        
        try:
            sql = "INSERT INTO GVCN (MaGVCN, TenGiaoVien, DienThoai, Email) VALUES (?, ?, ?, ?)"
            db.cursor.execute(sql, (ma, ten, dt, mail))
            db.conn.commit()
            load_data()
            clear_form()
            messagebox.showinfo("Thành công", "Đã thêm Giáo Viên Chủ Nhiệm mới.")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể thêm Giáo Viên.\n{e}")

    # === SỬA ===
    def sua_giao_vien():
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Chưa chọn", "Vui lòng chọn Giáo Viên cần sửa.")
            return
            
        ma_old = tree.item(selected[0], "values")[0] # Lấy mã cũ để tìm kiếm
        ma = maGVCN_entry.get().strip()
        ten = tenGV_entry.get().strip()
        dt = dienThoai_entry.get().strip()
        mail = email_entry.get().strip()
        
        if not ma or not ten:
            messagebox.showwarning("Thiếu dữ liệu", "Mã GVCN và Tên Giáo Viên không được để trống.")
            return
            
        try:
            # Cho phép sửa cả mã, nhưng dùng mã cũ để xác định bản ghi
            sql = "UPDATE GVCN SET MaGVCN=?, TenGiaoVien=?, DienThoai=?, Email=? WHERE MaGVCN=?"
            db.cursor.execute(sql, (ma, ten, dt, mail, ma_old))
            db.conn.commit()
            load_data()
            clear_form()
            messagebox.showinfo("Thành công", "Đã cập nhật thông tin Giáo Viên.")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể sửa thông tin Giáo Viên.\n{e}")

    # === XÓA ===
    def xoa_giao_vien():
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Chưa chọn", "Vui lòng chọn Giáo Viên cần xóa.")
            return
            
        ma = tree.item(selected[0], "values")[0]
        ten = tree.item(selected[0], "values")[1]
        
        if messagebox.askyesno("Xác nhận", f"Bạn có chắc muốn xóa Giáo Viên: {ten} ({ma})?"):
            try:
                db.cursor.execute("DELETE FROM GVCN WHERE MaGVCN=?", (ma,))
                db.conn.commit()
                load_data()
                clear_form()
                messagebox.showinfo("Thành công", "Đã xóa Giáo Viên.")
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể xóa Giáo Viên.\n{e}")

    def select_row(event):
        selected = tree.selection()
        if selected:
            values = tree.item(selected[0], "values")
            
            maGVCN_entry.delete(0, END)
            maGVCN_entry.insert(0, values[0])
            
            tenGV_entry.delete(0, END)
            tenGV_entry.insert(0, values[1])
            
            dienThoai_entry.delete(0, END)
            dienThoai_entry.insert(0, values[2])
            
            email_entry.delete(0, END)
            email_entry.insert(0, values[3])


    # ======= Treeview hiển thị =======
    frame_tree = Frame(root, bg="#F0F8FF")
    frame_tree.pack(fill="both", expand=True, padx=10, pady=10)

    columns = ("MaGVCN", "TenGiaoVien", "DienThoai", "Email")
    tree = ttk.Treeview(frame_tree, columns=columns, show="headings")
    tree.heading("MaGVCN", text="Mã GVCN")
    tree.heading("TenGiaoVien", text="Tên Giáo Viên")
    tree.heading("DienThoai", text="Điện Thoại")
    tree.heading("Email", text="Email")

    tree.column("MaGVCN", width=100, anchor=CENTER)
    tree.column("TenGiaoVien", width=200)
    tree.column("DienThoai", width=120, anchor=CENTER)
    tree.column("Email", width=250)
    
    tree.pack(side=LEFT, fill=BOTH, expand=True)

    # Thanh cuộn dọc
    scroll_y = ttk.Scrollbar(frame_tree, orient=VERTICAL, command=tree.yview)
    tree.configure(yscroll=scroll_y.set)
    scroll_y.pack(side=RIGHT, fill=Y)

    tree.bind("<<TreeviewSelect>>", select_row)

    # === Nút quay lại ===
    def quay_lai():
        root.destroy()
        # Giả định form học sinh có thể mở lại
        lh.start_Lop(menu_root, mn.menu_vaitro)

    # ======= Các nút chức năng =======
    frame_btn = Frame(root, bg="#F0F8FF")
    frame_btn.pack(pady=10)

    Button(frame_btn, text="Thêm", bg="#4CAF50", fg="white", width=12, command=them_giao_vien).grid(row=0, column=0, padx=5)
    Button(frame_btn, text="Sửa", bg="#FFC107", fg="black", width=12, command=sua_giao_vien).grid(row=0, column=1, padx=5)
    Button(frame_btn, text="Xóa", bg="#F44336", fg="white", width=12, command=xoa_giao_vien).grid(row=0, column=2, padx=5)
    Button(frame_btn, text="Làm mới", bg="#2196F3", fg="white", width=12, command=clear_form).grid(row=0, column=3, padx=5)
    Button(frame_btn, text="Quay lại", bg="#9C27B0", fg="white", width=12, command=quay_lai).grid(row=0, column=4, padx=5)
    
    # ======= Tải dữ liệu ban đầu =======
    load_data()

    root.mainloop()
