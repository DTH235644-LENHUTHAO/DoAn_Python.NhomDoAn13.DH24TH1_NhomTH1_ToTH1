# 🎓  
### **Ứng dụng Quản Lý Học Sinh – Python, Tkinter & SQL Server**  
**Đồ án môn học: Chuyên đề Python (COS525)**  
**Trường Đại học An Giang – Khoa Công Nghệ Thông Tin**

---

## 👥 Thành viên thực hiện  
**Giảng viên hướng dẫn:** ThS. Nguyễn Ngọc Minh  
| MSSV | Họ tên | Lớp |
|------|--------|------|
| DTH235644 | Lê Nhựt Hào | DH24TH1 – Nhóm 1 – Tổ 1 |
| DTH235768 | Nguyễn Chí Thanh | DH24TH3 – Nhóm 1 – Tổ 1 |

---

## 📘 Giới thiệu  
Ứng dụng **Quản Lý Học Sinh** được xây dựng nhằm hỗ trợ các trường học quản lý dữ liệu học sinh một cách hiệu quả, chính xác và hiện đại hơn. Dự án giúp thay thế việc quản lý thủ công bằng sổ sách hoặc Excel – vốn dễ nhầm lẫn, khó tìm kiếm và không bảo mật.

Hệ thống sử dụng **Python + Tkinter** để phát triển giao diện và **SQL Server** làm nơi lưu trữ dữ liệu tập trung.  
Ứng dụng đáp ứng tốt nhu cầu quản lý thông tin học sinh, điểm số, lớp học, học phí và phân quyền người dùng.

---

## 🚀 Tính năng chính  
### 🔹 Quản lý học sinh  
- Thêm, sửa, xóa học sinh  
- Nhập thông tin cá nhân, lớp học, địa chỉ  
- Hiển thị danh sách bằng Treeview

### 🔹 Quản lý điểm  
- Thêm điểm TX, GK, CK  
- Tự động tính điểm trung bình môn  
- Cập nhật và xuất dữ liệu điểm  

### 🔹 Quản lý lớp học  
- Quản lý mã lớp, tên lớp, khối và giáo viên chủ nhiệm  

### 🔹 Quản lý học phí  
- Theo dõi học phí: đã đóng – còn nợ – trạng thái  
- Cập nhật học phí theo học sinh  

### 🔹 Tìm kiếm & tra cứu  
- Tìm kiếm nhanh theo mã, tên, lớp, môn hoặc thông tin liên quan  

### 🔹 Phân quyền đăng nhập  
- **Admin**: toàn quyền quản lý  
- **User**: quyền xem và thao tác hạn chế  

---

## 🛠️ Công nghệ sử dụng  
- **Python**  
- **Tkinter** – xây dựng giao diện  
- **SQL Server 2014** – quản lý dữ liệu  

---

## 🗄️ Thiết kế cơ sở dữ liệu  
Hệ thống gồm các bảng chính:  
- **HOCSINH** – thông tin học sinh  
- **LOPHOC** – thông tin lớp học  
- **DIEM** – điểm từng môn học  
- **HOCPHI** – học phí và trạng thái  
- **MONHOC**, **DIACHI**, **GVCN**, **USERS**  

Các bảng được liên kết bằng khóa chính và khóa ngoại, đảm bảo toàn vẹn dữ liệu.

---

## 📚 Tài liệu tham khảo  
1. Nguyễn Văn Hòa (2022), *Giáo trình Lập trình Python cơ bản*, NXB ĐHQG TPHCM  
2. https://timoday.edu.vn/xay-dung-chuong-trinh-quan-ly-ban-hang-bang-c/  
3. https://www.w3schools.com/python/  
