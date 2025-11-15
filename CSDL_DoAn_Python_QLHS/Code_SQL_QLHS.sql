--Tạo CSDL Quản lý sinh viên  
create database QuanLyHocSinh on 
(
	name = QuanLyHocSinh_Data,
	filename = 'E:\DoAn_Python\CSDL\QuanLyHocSinh_data.mdf',
	size = 10mb,
	maxsize = 50mb,
	filegrowth = 5mb
)

log on
(
	name = QuanLyHocSinh_Log,
	filename = 'E:\DoAn_Python\CSDL\QuanLyHocSinh_log.ldf',
	size = 10mb,
	maxsize = 50mb,
	filegrowth = 5mb
)

use QuanLyHocSinh


-- TẠO BẢNG :
--Tạo bảng LOPHOC
create table LOPHOC
(
    MaLop NVARCHAR(50) PRIMARY KEY,
    TenLop NVARCHAR(50) UNIQUE NOT NULL,
    Khoi INT NOT NULL,
    MaGVCN NVARCHAR(50)
);

create table HOCSINH
(
	MaHS NVARCHAR(50) PRIMARY KEY,
	HoTenHS NVARCHAR(50),
	NgaySinh DATE,
	GioiTinh NVARCHAR(50),
	Email NVARCHAR(50) ,
	MaLop NVARCHAR(50),
	MaDiaChi NVARCHAR(50)
);

create table MONHOC
(
	MaMH NVARCHAR(50) PRIMARY KEY,
	TenMH NVARCHAR(50)
);

create table GVCN
(
	MaGVCN NVARCHAR(50) PRIMARY KEY,
	TenGiaoVien NVARCHAR(50),
    DienThoai NVARCHAR(50),
    Email NVARCHAR(50)
);

create table DIACHI
(
	MaDiaChi NVARCHAR(50) PRIMARY KEY,
    DiaChi NVARCHAR(250)
);

create table DIEM
(
    MaHS NVARCHAR(50),
    MaMH NVARCHAR(50),
    ThuongXuyen FLOAT,
    Giuaki FLOAT,
	Cuoiki FLOAT,
	TBM FLOAT,
	PRIMARY KEY (MaHS, MaMH)
);

create table HOCPHI
(
	MaHP NVARCHAR(50) PRIMARY KEY,
    HocPhi DECIMAL(10,2) NOT NULL,
    DaDong DECIMAL(10,2),
	ConNo DECIMAL(10,2),
    TrangThai NVARCHAR(50),
    MaHS NVARCHAR(50)
);

create table NGUOIDUNG
(
	UserID NVARCHAR(50) PRIMARY KEY,
	MatKhau NVARCHAR(50) NOT NULL,
	VaiTro NVARCHAR (50)
);

--TẠO KHÓA NGOẠI :
alter table HOCSINH add constraint fk_HOCSINH_LOPHOC foreign key (MaLop) references LOPHOC(MaLop)
alter table HOCSINH add constraint fk_HOCSINH_DIACHI foreign key (MaDiaChi) references DIACHI(MaDiaChi)
alter table LOPHOC add constraint fk_LOPHOC_GVCN foreign key (MaGVCN) references GVCN(MaGVCN)
alter table DIEM add constraint fk_DIEM_HOCSINH foreign key (MaHS) references HOCSINH(MaHS)
alter table DIEM add constraint fk_DIEM_MONHOC foreign key (MaMH) references MONHOC(MaMH)
alter table HOCPHI add constraint fk_HOCPHI_HOCSINH foreign key (MaHS) references HOCSINH(MaHS)
--alter table NGUOIDUNG add constraint fk_NGUOIDUNG_HOCSINH foreign key (MaHS) references HOCSINH(MaHS)
--Insert 
INSERT INTO GVCN (MaGVCN, TenGiaoVien, DienThoai, Email) VALUES
(N'GV001', N'Nguyễn Thị Hồng', N'0901234567', N'hongnt@agu.edu'),
(N'GV002', N'Lê Văn Minh', N'0902345678', N'minhlv@agu.edu'),
(N'GV003', N'Trần Ánh Tuyết', N'0903456789', N'tuyetta@agu.edu'),
(N'GV004', N'Phạm Quang Thắng', N'0904567890', N'thangpq@agu.edu'),
(N'GV005', N'Hoàng Thanh Nga', N'0905678901', N'ngath@agu.edu'),
(N'GV006', N'Đỗ Hữu Lộc', N'0906789012', N'locdh@agu.edu'),
(N'GV007', N'Vũ Thị Mai', N'0907890123', N'maivt@agu.edu');

INSERT INTO MONHOC (MaMH, TenMH) VALUES
(N'MH001', N'Toán'),
(N'MH002', N'Ngữ Văn'),
(N'MH003', N'Tiếng Anh'),
(N'MH004', N'Vật Lý'),
(N'MH005', N'Hóa Học'),
(N'MH006', N'Sinh Học'),
(N'MH007', N'Lịch Sử');

INSERT INTO DIACHI (MaDiaChi, DiaChi) VALUES
(N'DC001', N'Phường Mỹ Bình, TP. Long Xuyên, An Giang'),
(N'DC002', N'Phường Châu Phú, TP. Châu Đốc, An Giang'),
(N'DC003', N'Huyện Chợ Mới, An Giang'),
(N'DC004', N'Thị trấn Núi Sập, Huyện Thoại Sơn, An Giang'),
(N'DC005', N'Thị Trấn Óc Eo, Huyện Thoại Sơn, An Giang'),
(N'DC006', N'Phường Đông Xuyên, TP. Long Xuyên, An Giang'),
(N'DC007', N'Thị trấn Cái Dầu, Huyện Châu Phú, An Giang');

INSERT INTO LOPHOC (MaLop, TenLop, Khoi, MaGVCN) VALUES
(N'L10A1', N'10A1', 10, N'GV001'),
(N'L10A2', N'10A2', 10, N'GV002'),
(N'L11B1', N'11B1', 11, N'GV003'),
(N'L11B2', N'11B2', 11, N'GV004'),
(N'L12C1', N'12C1', 12, N'GV005'),
(N'L12C2', N'12C2', 12, N'GV006'),
(N'L10A3', N'10A3', 10, N'GV007');

INSERT INTO HOCSINH (MaHS, HoTenHS, NgaySinh, GioiTinh, Email, MaLop, MaDiaChi) VALUES
(N'HS001', N'Trần Minh Hoàng', '2008-05-15', N'Nam', N'hoangtm@school.com', N'L10A1', N'DC001'),
(N'HS002', N'Lê Thị Lan', '2007-10-20', N'Nữ', N'lanlt@school.com', N'L10A1', N'DC002'),
(N'HS003', N'Phạm Văn Tài', '2006-03-01', N'Nam', N'taipv@school.com', N'L11B1', N'DC003'),
(N'HS004', N'Nguyễn Thu Hiền', '2005-11-25', N'Nữ', N'hiennt@school.com', N'L11B2', N'DC004'),
(N'HS005', N'Võ Đình Khang', '2004-07-07', N'Nam', N'khangvd@school.com', N'L12C1', N'DC005'),
(N'HS006', N'Đặng Thị Thúy', '2008-01-09', N'Nữ', N'thuytdt@school.com', N'L10A2', N'DC006'),
(N'HS007', N'Bùi Chí Dũng', '2007-04-12', N'Nam', N'dungbc@school.com', N'L11B1', N'DC007');

INSERT INTO DIEM (MaHS, MaMH, ThuongXuyen, Giuaki, Cuoiki, TBM) VALUES
(N'HS001', N'MH001', 8.5, 8.5, 9.5, 9.0),   
(N'HS007', N'MH002', 7.0, 8.0, 9.0, 8.33),   
(N'HS002', N'MH001', 9.0, 7.0, 9.0, 8.33),   
(N'HS003', N'MH003', 9.5, 9.5, 9.5, 9.5),   
(N'HS004', N'MH004', 6.0, 7.5, 8.0, 7.5),   
(N'HS005', N'MH005', 8.0, 8.0, 8.0, 8.0),   
(N'HS006', N'MH001', 8.0, 6.5, 7.0, 7.0);   

INSERT INTO HOCPHI (MaHP, HocPhi, DaDong, ConNo, TrangThai, MaHS) VALUES
(N'HP001', 5000000.00, 5000000.00, 0.00, N'Đã đóng đủ', N'HS001'),
(N'HP002', 5000000.00, 3000000.00, 2000000.00, N'Chưa đủ', N'HS002'),
(N'HP003', 5500000.00, 5500000.00, 0.00, N'Đã đóng đủ', N'HS003'),
(N'HP004', 5500000.00, 4000000.00, 1500000.00, N'Chưa đủ', N'HS004'),
(N'HP005', 6000000.00, 6000000.00, 0.00, N'Đã đóng đủ', N'HS005'),
(N'HP006', 5000000.00, 5000000.00, 0.00, N'Đã đóng đủ', N'HS006'),
(N'HP007', 5500000.00, 0.00, 5500000.00, N'Chưa đóng', N'HS007');

INSERT INTO NGUOIDUNG (UserID,MatKhau,VaiTro) VALUES
(N'ID1111', '111111','Admin'),
(N'ID1234', '222222','User'),
(N'ID1235', '333333','User');

SELECT * FROM NGUOIDUNG;
SELECT * FROM HOCSINH;
SELECT * FROM DIACHI;
SELECT * FROM HOCPHI;
SELECT * FROM MONHOC;
SELECT * FROM GVCN;
SELECT * FROM DIEM;
