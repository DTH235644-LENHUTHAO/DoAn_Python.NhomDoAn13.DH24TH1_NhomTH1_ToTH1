from tkinter import *
from tkinter import ttk, messagebox
import Connect as db 
import formHocSinh as hs 
import formMeNu as mn
import formDiem as diem
import pyodbc 


def center_window(win, w=600, h=420):
    ws = win.winfo_screenwidth()
    hs = win.winfo_screenheight()
    x = (ws // 2) - (w // 2)
    y = (hs // 2) - (h // 2)
    win.geometry(f'{w}x{h}+{x}+{y}')

def start_MonHoc(menu_root=None): 
    """Form quản lý bảng MONHOC (Mã MH, Tên MH)"""
    # Khởi tạo kết nối CSDL
    db.connect_db()

    root = Toplevel()
    root.title("Quản Lý Môn Học")
    root.minsize(600, 420)
    root.resizable(width=True, height=True)
    center_window(root, 600, 420)
    #root.geometry("600x420")
    root.config(bg="#F0F8FF")

    # ======= Biến cho Entry =======
    stringMaMH = StringVar()
    stringTenMH = StringVar()
    
    # Biến lưu Mã MH cũ khi chọn sửa/xóa
    old_MaMH = StringVar() 

    # ======= Frame nhập dữ liệu =======
    frame_form = LabelFrame(root, text="Thông tin Môn Học", bg="#F0F8FF", padx=10, pady=10)
    frame_form.pack(fill="x", padx=10, pady=10)

    Label(frame_form, text="Mã Môn Học:", bg="#F0F8FF").grid(row=0, column=0, sticky="w", padx=5, pady=5)
    maMH_entry = Entry(frame_form, width=30, textvariable=stringMaMH)
    maMH_entry.grid(row=0, column=1, padx=5, pady=5)

    Label(frame_form, text="Tên Môn Học:", bg="#F0F8FF").grid(row=1, column=0, sticky="w", padx=5, pady=5)
    tenMH_entry = Entry(frame_form, width=30, textvariable=stringTenMH)
    tenMH_entry.grid(row=1, column=1, padx=5, pady=5)

    # ======= Treeview hiển thị =======
    frame_tree = Frame(root, bg="#F0F8FF")
    frame_tree.pack(fill="both", expand=True, padx=10, pady=10)

    columns = ("MaMH", "TenMH")
    tree = ttk.Treeview(frame_tree, columns=columns, show="headings")
    tree.heading("MaMH", text="Mã Môn Học")
    tree.heading("TenMH", text="Tên Môn Học")
    tree.column("MaMH", width=120, anchor=CENTER)
    tree.column("TenMH", width=300, anchor=W)
    tree.pack(side=LEFT, fill=BOTH, expand=True)

    # Thanh cuộn dọc
    scroll_y = ttk.Scrollbar(frame_tree, orient=VERTICAL, command=tree.yview)
    tree.configure(yscroll=scroll_y.set)
    scroll_y.pack(side=RIGHT, fill=Y)

    # ======= Hàm xử lý CSDL ======= 
    def load_data():
        """Tải danh sách môn học từ CSDL lên Treeview."""
        try:
            sql = "SELECT MaMH, TenMH FROM MONHOC ORDER BY MaMH"
            db.cursor.execute(sql)
            rows = db.cursor.fetchall()
            tree.delete(*tree.get_children())  # Xóa dữ liệu cũ trong Treeview
            for row in rows:
                tree.insert('', 'end', values=(row[0], row[1]))
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi tải dữ liệu: {e}")

    def clear_form():
        """Xóa trắng form và xóa chọn trên Treeview."""
        stringMaMH.set("")
        stringTenMH.set("")
        old_MaMH.set("")
        try:
            if tree.selection():
                tree.selection_remove(tree.selection())
        except Exception:
            pass
            
    # === THÊM ===
    def them_mon_hoc():
        
        ma = stringMaMH.get().strip()
        ten = stringTenMH.get().strip()
        
        if not ma or not ten:
            messagebox.showwarning("Thiếu dữ liệu", "Vui lòng nhập đầy đủ Mã và Tên Môn Học.")
            return
            
        try:
            # Kiểm tra Mã MH đã tồn tại
            db.cursor.execute("SELECT 1 FROM MONHOC WHERE MaMH=?", (ma,))
            if db.cursor.fetchone():
                 messagebox.showerror("Lỗi", f"Mã Môn Học '{ma}' đã tồn tại.")
                 return
                 
            sql = "INSERT INTO MONHOC (MaMH, TenMH) VALUES (?, ?)"
            db.cursor.execute(sql, (ma, ten))
            db.conn.commit()
            messagebox.showinfo("Thành công", "Đã thêm Môn Học mới.")
            load_data()
            clear_form()
        except pyodbc.Error as e:
            messagebox.showerror("Lỗi CSDL", f"Lỗi SQL: {e}")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể thêm Môn Học.\n{e}")

    # === SỬA ===
    def sua_mon_hoc():

        ma_moi = stringMaMH.get().strip()
        ten_moi = stringTenMH.get().strip()
        ma_cu = old_MaMH.get()
        
        if not ma_cu:
            messagebox.showwarning("Chưa chọn", "Vui lòng chọn Môn Học cần sửa.")
            return
            
        if not ma_moi or not ten_moi:
            messagebox.showwarning("Thiếu dữ liệu", "Vui lòng nhập đầy đủ Mã và Tên Môn Học.")
            return
            
        try:
            # 1. Kiểm tra Mã mới có bị trùng với Mã khác không (trừ chính nó)
            if ma_moi != ma_cu:
                 db.cursor.execute("SELECT 1 FROM MONHOC WHERE MaMH=?", (ma_moi,))
                 if db.cursor.fetchone():
                     messagebox.showerror("Lỗi Trùng Lặp", f"Mã Môn Học mới '{ma_moi}' đã tồn tại.")
                     return
                     
            # 2. Thực hiện Update
            sql = "UPDATE MONHOC SET MaMH=?, TenMH=? WHERE MaMH=?"
            db.cursor.execute(sql, (ma_moi, ten_moi, ma_cu))
            db.conn.commit()
            messagebox.showinfo("Thành công", f"Đã cập nhật Môn Học {ma_moi}.")
            load_data()
            clear_form()
        except pyodbc.Error as e:
            messagebox.showerror("Lỗi CSDL", f"Lỗi SQL: {e}")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể sửa Môn Học.\n{e}")

    # === XÓA ===
    def xoa_mon_hoc():
        
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Chưa chọn", "Vui lòng chọn Môn Học cần xóa.")
            return
            
        ma_xoa = tree.item(selected[0], "values")[0]
        
        if messagebox.askyesno("Xác nhận", f"Bạn có chắc muốn xóa Môn Học Mã {ma_xoa}? Thao tác này có thể gây lỗi khóa ngoại."):
            try:
                sql = "DELETE FROM MONHOC WHERE MaMH=?"
                db.cursor.execute(sql, (ma_xoa,))
                db.conn.commit()
                messagebox.showinfo("Thành công", "Đã xóa Môn Học.")
                load_data()
                clear_form()
            except pyodbc.Error as e:
                if 'foreign key' in str(e).lower():
                    messagebox.showerror("Lỗi Khóa Ngoại", "Không thể xóa vì Môn Học này đang được sử dụng ở bảng khác.")
                else:
                    messagebox.showerror("Lỗi CSDL", f"Lỗi SQL: {e}")
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể xóa Môn Học.\n{e}")

    def select_row(event):
        """Lấy dữ liệu từ Treeview lên Entry khi click chọn."""
        selected = tree.selection()
        if selected:
            values = tree.item(selected[0], "values")
            stringMaMH.set(values[0])
            stringTenMH.set(values[1])
            old_MaMH.set(values[0]) # Lưu lại mã gốc
        else:
            clear_form()

    tree.bind("<<TreeviewSelect>>", select_row)

    # === Nút quay lại ===
    def quay_lai():
        root.destroy()
        diem.start_Diem(menu_root,mn.menu_vaitro)
        
    # ======= Các nút chức năng =======
    frame_btn = Frame(root, bg="#F0F8FF")
    frame_btn.pack(pady=10)

    Button(frame_btn, text="Thêm", bg="#4CAF50", fg="white", width=10, command=them_mon_hoc).grid(row=0, column=0, padx=5)
    Button(frame_btn, text="Sửa", bg="#FFC107", fg="black", width=10, command=sua_mon_hoc).grid(row=0, column=1, padx=5)
    Button(frame_btn, text="Xóa", bg="#F44336", fg="white", width=10, command=xoa_mon_hoc).grid(row=0, column=2, padx=5)
    Button(frame_btn, text="Làm mới", bg="#2196F3", fg="white", width=10, command=clear_form).grid(row=0, column=3, padx=5)
    Button(frame_btn, text="Quay lại", bg="#9C27B0", fg="white", width=10, command=quay_lai).grid(row=0, column=4, padx=5)
    #Button(frame_btn, text="Thoát", bg="#9E9E9E", fg="white", width=10, command=root.destroy).grid(row=0, column=5, padx=5)

    # ======= Tải dữ liệu ban đầu =======
    load_data()

    # Xử lý khi đóng cửa sổ
    root.protocol("WM_DELETE_WINDOW", quay_lai)

    root.mainloop()


# Test chạy riêng file
if __name__ == "__main__":
    start_MonHoc(user_role='Admin')