from tkinter import *
from tkinter import messagebox
import Connect as db  # import module kết nối CSDL

def center_window(win, w=600, h=300):
    ws = win.winfo_screenwidth()
    hs = win.winfo_screenheight()
    x = (ws // 2) - (w // 2)
    y = (hs // 2) - (h // 2)
    win.geometry(f'{w}x{h}+{x}+{y}')

def start_TimKiem(menu_window, vaitro):
    root = Toplevel(menu_window)
    root.title("Tìm Kiếm Học Sinh")
    center_window(root, 600, 350)

    search_var = StringVar()
    search_by = StringVar(value="HoTenHS")  # Mặc định tìm theo họ tên

    Label(root, text="Nhập thông tin cần tìm:", font=("Arial", 12)).pack(pady=5)
    entry_search = Entry(root, textvariable=search_var, font=("Arial", 12), width=40)
    entry_search.pack(pady=5)

    frame_radio = Frame(root)
    frame_radio.pack(pady=5)
    Radiobutton(frame_radio, text="Họ tên", variable=search_by, value="HoTenHS", font=("Arial", 11)).pack(side=LEFT, padx=20)
    Radiobutton(frame_radio, text="Mã học sinh", variable=search_by, value="MaHS", font=("Arial", 11)).pack(side=LEFT, padx=20)

    info_text = Text(root, width=70, height=10, font=("Arial", 11), state=DISABLED)
    info_text.pack(pady=10)

    def tim_HocSinh():
        key = search_var.get().strip()
        if not key:
            messagebox.showwarning("Cảnh báo", "Vui lòng nhập thông tin tìm kiếm.")
            return
        column = search_by.get()
        try:
            db.connect_db()
            sql = f"""
            SELECT 
                hs.MaHS, hs.HoTenHS, hs.NgaySinh, hs.GioiTinh, hs.Email,
                lh.TenLop, lh.Khoi, gv.TenGiaoVien, dc.DiaChi
            FROM HOCSINH hs
            LEFT JOIN LOPHOC lh ON hs.MaLop = lh.MaLop
            LEFT JOIN GVCN gv ON lh.MaGVCN = gv.MaGVCN
            LEFT JOIN DIACHI dc ON hs.MaDiaChi = dc.MaDiaChi
            WHERE hs.{column} LIKE ?
            """
            param = ('%' + key + '%',)
            db.cursor.execute(sql, param)
            rows = db.cursor.fetchall()

            info_text.config(state=NORMAL)
            info_text.delete('1.0', END)
            if rows:
                for r in rows:
                    ngay_sinh_str = r[2].strftime('%Y-%m-%d') if r[2] else ''
                    info_text.insert(END,
                                     f"Mã HS: {r[0]}\n"
                                     f"Họ Tên: {r[1]}\n"
                                     f"Ngày Sinh: {ngay_sinh_str}\n"
                                     f"Giới Tính: {r[3]}\n"
                                     f"Email: {r[4]}\n"
                                     f"Tên Lớp: {r[5]}\n"
                                     f"Khối: {r[6]}\n"
                                     f"Tên GVCN: {r[7]}\n"
                                     f"Địa Chỉ: {r[8]}\n"
                                     f"{'-'*50}\n")
            else:
                info_text.insert(END, "Không tìm thấy học sinh phù hợp!")
            info_text.config(state=DISABLED)
        except Exception as e:
            messagebox.showerror("Lỗi truy vấn CSDL", str(e))


    def tim_Diem():
        key = search_var.get().strip()
        if not key:
            messagebox.showwarning("Cảnh báo", "Vui lòng nhập thông tin tìm kiếm.")
            return
        column = search_by.get()
        try:
            db.connect_db()
            # Lấy điểm của học sinh phù hợp theo tìm kiếm
            sql = f"""
            SELECT 
                hs.MaHS, hs.HoTenHS, mh.MaMH, mh.TenMH,
                d.ThuongXuyen, d.Giuaki, d.Cuoiki, d.TBM
            FROM HOCSINH hs
            LEFT JOIN DIEM d ON hs.MaHS = d.MaHS
            LEFT JOIN MONHOC mh ON d.MaMH = mh.MaMH
            WHERE hs.{column} LIKE ?
            """
            param = ('%' + key + '%',)
            db.cursor.execute(sql, param)
            rows = db.cursor.fetchall()

            info_text.config(state=NORMAL)
            info_text.delete('1.0', END)
            if rows:
                for r in rows:
                    info_text.insert(END,
                        f"Mã HS: {r[0]}\n"
                        f"Họ Tên: {r[1]}\n"
                        f"Mã Môn: {r[2] or ''}\n"
                        f"Tên Môn: {r[3] or ''}\n"
                        f"Thường Xuyên: {r[4] if r[4] is not None else ''}\n"
                        f"Giữa Kỳ: {r[5] if r[5] is not None else ''}\n"
                        f"Cuối Kỳ: {r[6] if r[6] is not None else ''}\n"
                        f"TBM: {r[7] if r[7] is not None else ''}\n"
                        f"{'-'*50}\n"
                    )
            else:
                info_text.insert(END, "Không tìm thấy học sinh phù hợp!")
            info_text.config(state=DISABLED)

        except Exception as e:
            messagebox.showerror("Lỗi truy vấn CSDL", str(e))
    

    def close_TK_form():
        root.destroy()
        menu_window.deiconify()


    frame_buttons = Frame(root)
    frame_buttons.pack(pady=10)

    btn_timhs = Button(frame_buttons, text="Tìm kiếm", font=("Arial", 12, "bold"), bg="#4CAF50", fg="white", width=12, command=tim_HocSinh)
    btn_timdiem= Button(frame_buttons, text="Xem điểm", font=("Arial", 12, "bold"), bg="#2196F3", fg="white", width=12, command=tim_Diem)
    btn_thoat = Button(frame_buttons, text="Thoát", font=("Arial", 12, "bold"), bg="#9E9E9E", fg="white", width=12, command=close_TK_form)
   
    btn_timhs.pack(side=LEFT, padx=10)
    btn_timdiem.pack(side=LEFT, padx=10)
    btn_thoat.pack(side=LEFT, padx=10)
    root.mainloop()

if __name__ == "__main__":
    start_TimKiem()
