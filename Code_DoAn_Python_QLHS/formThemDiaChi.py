from tkinter import *
from tkinter import ttk, messagebox
import Connect as db  # file Connect.py có connect_db()
import formHocSinh as hs  # <-- import form học sinh để quay lại
import formMeNu as mn


def center_window(win, w=600, h=420):
    ws = win.winfo_screenwidth()
    hs = win.winfo_screenheight()
    x = (ws // 2) - (w // 2)
    y = (hs // 2) - (h // 2)
    win.geometry(f'{w}x{h}+{x}+{y}')

def start_DiaChi(menu_root=None):
    """Form quản lý bảng ĐỊA CHỈ"""
    db.connect_db()

    root = Toplevel()
    root.title("Quản Lý Địa Chỉ")
    root.minsize(600, 420)
    root.resizable(width=True, height=True)
    center_window(root, 600, 420)
    #root.geometry("600x420")
    root.config(bg="#F0F8FF")

    # ======= Frame nhập dữ liệu =======
    frame_form = LabelFrame(root, text="Thông tin địa chỉ", bg="#F0F8FF", padx=10, pady=10)
    frame_form.pack(fill="x", padx=10, pady=10)

    Label(frame_form, text="Mã Địa Chỉ:", bg="#F0F8FF").grid(row=0, column=0, sticky="w", padx=5, pady=5)
    maDC_entry = Entry(frame_form, width=30)
    maDC_entry.grid(row=0, column=1, padx=5, pady=5)

    Label(frame_form, text="Tên Địa Chỉ:", bg="#F0F8FF").grid(row=1, column=0, sticky="w", padx=5, pady=5)
    tenDC_entry = Entry(frame_form, width=30)
    tenDC_entry.grid(row=1, column=1, padx=5, pady=5)

    # ======= Treeview hiển thị =======
    frame_tree = Frame(root, bg="#F0F8FF")
    frame_tree.pack(fill="both", expand=True, padx=10, pady=10)

    columns = ("MaDiaChi", "DiaChi")
    tree = ttk.Treeview(frame_tree, columns=columns, show="headings")
    tree.heading("MaDiaChi", text="Mã Địa Chỉ")
    tree.heading("DiaChi", text="Địa Chỉ")
    tree.column("MaDiaChi", width=120)
    tree.column("DiaChi", width=300)
    tree.pack(side=LEFT, fill=BOTH, expand=True)

    # Thanh cuộn dọc
    scroll_y = ttk.Scrollbar(frame_tree, orient=VERTICAL, command=tree.yview)
    tree.configure(yscroll=scroll_y.set)
    scroll_y.pack(side=RIGHT, fill=Y)

    # ======= Hàm xử lý =======
    def load_data():
        """Tải danh sách địa chỉ từ CSDL lên Treeview."""
        try:
            sql = "SELECT MaDiaChi, DiaChi FROM DIACHI"
            db.cursor.execute(sql)
            rows = db.cursor.fetchall()
            tree.delete(*tree.get_children())  # Xóa dữ liệu cũ trong Treeview
            for row in rows:
                tree.insert('', 'end', values=(row[0], row[1]))
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi tải dữ liệu: {e}")

    def clear_form():
        maDC_entry.delete(0, END)
        tenDC_entry.delete(0, END)
        tree.selection_remove(tree.selection())


    # === THÊM ===
    def them_dia_chi():
        ma = maDC_entry.get().strip()
        ten = tenDC_entry.get().strip()
        if not ma or not ten:
            messagebox.showwarning("Thiếu dữ liệu", "Vui lòng nhập đầy đủ thông tin.")
            return
        try:
            db.cursor.execute("INSERT INTO DIACHI (MaDiaChi, DiaChi) VALUES (?, ?)", (ma, ten))
            db.conn.commit()
            load_data()
            clear_form()
            messagebox.showinfo("Thành công", "Đã thêm địa chỉ mới.")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể thêm địa chỉ.\n{e}")

    # === SỬA ===
    def sua_dia_chi():
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Chưa chọn", "Vui lòng chọn địa chỉ cần sửa.")
            return
        ma = maDC_entry.get().strip()
        ten = tenDC_entry.get().strip()
        try:
            db.cursor.execute("UPDATE DIACHI SET DiaChi=? WHERE MaDiaChi=?", (ten, ma))
            db.conn.commit()
            load_data()
            clear_form()
            messagebox.showinfo("Thành công", "Đã cập nhật địa chỉ.")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể sửa địa chỉ.\n{e}")

    # === XÓA ===
    def xoa_dia_chi():
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Chưa chọn", "Vui lòng chọn địa chỉ cần xóa.")
            return
        ma = tree.item(selected[0], "values")[0]
        if messagebox.askyesno("Xác nhận", f"Bạn có chắc muốn xóa {ma}?"):
            try:
                db.cursor.execute("DELETE FROM DIACHI WHERE MaDiaChi=?", (ma,))
                db.conn.commit()
                load_data()
                clear_form()
                messagebox.showinfo("Thành công", "Đã xóa địa chỉ.")
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể xóa địa chỉ.\n{e}")

    def select_row(event):
        selected = tree.selection()
        if selected:
            values = tree.item(selected[0], "values")
            maDC_entry.delete(0, END)
            maDC_entry.insert(0, values[0])
            tenDC_entry.delete(0, END)
            tenDC_entry.insert(0, values[1])

    tree.bind("<<TreeviewSelect>>", select_row)

    # === Nút quay lại ===
    def quay_lai():
        root.destroy()
        hs.start_HS(menu_root,mn.menu_vaitro)  # mở lại form học sinh

    # ======= Các nút chức năng =======
    frame_btn = Frame(root, bg="#F0F8FF")
    frame_btn.pack(pady=10)

    Button(frame_btn, text="Thêm", bg="#4CAF50", fg="white", width=10, command=them_dia_chi).grid(row=0, column=0, padx=5)
    Button(frame_btn, text="Sửa", bg="#FFC107", fg="black", width=10, command=sua_dia_chi).grid(row=0, column=1, padx=5)
    Button(frame_btn, text="Xóa", bg="#F44336", fg="white", width=10, command=xoa_dia_chi).grid(row=0, column=2, padx=5)
    Button(frame_btn, text="Làm mới", bg="#2196F3", fg="white", width=10, command=clear_form).grid(row=0, column=3, padx=5)
    Button(frame_btn, text="Quay lại", bg="#9C27B0", fg="white", width=10, command=quay_lai).grid(row=0, column=4, padx=5)
    #Button(frame_btn, text="Thoát", bg="#9E9E9E", fg="white", width=10, command=root.destroy).grid(row=0, column=5, padx=5)

    # ======= Tải dữ liệu ban đầu =======
    load_data()

    root.mainloop()


# Test chạy riêng file
if __name__ == "__main__":
    start_DiaChi()
