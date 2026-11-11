
USE MediCare;
GO

/* =========================================================
   1. TẠO BẢNG CHUYÊN KHOA NẾU CHƯA CÓ
   ========================================================= */

IF OBJECT_ID('dbo.ChuyenKhoa', 'U') IS NULL
BEGIN
    CREATE TABLE dbo.ChuyenKhoa (
        Id INT IDENTITY(1,1) PRIMARY KEY,
        TenChuyenKhoa NVARCHAR(100) NOT NULL UNIQUE
    );
END;
GO

/* =========================================================
   2. TẠO BẢNG BÁC SĨ NẾU CHƯA CÓ
   ========================================================= */

IF OBJECT_ID('dbo.BacSi', 'U') IS NULL
BEGIN
    CREATE TABLE dbo.BacSi (
        Id INT IDENTITY(1,1) PRIMARY KEY,
        HoTen NVARCHAR(150) NOT NULL,
        ChuyenKhoaId INT NOT NULL,
        PhongKham NVARCHAR(50) NULL,
        TrangThai BIT NOT NULL DEFAULT 1,
        NgayTao DATETIME2 NOT NULL DEFAULT SYSDATETIME(),

        CONSTRAINT FK_BacSi_ChuyenKhoa
            FOREIGN KEY (ChuyenKhoaId)
            REFERENCES dbo.ChuyenKhoa(Id)
    );
END;
GO

/* =========================================================
   3. THÊM 6 CHUYÊN KHOA NẾU CHƯA CÓ
   ========================================================= */

INSERT INTO dbo.ChuyenKhoa (TenChuyenKhoa)
SELECT v.Ten
FROM (VALUES
    (N'Nội khoa'),
    (N'Ngoại khoa'),
    (N'Nhi khoa'),
    (N'Tim mạch'),
    (N'Da liễu'),
    (N'Tai - Mũi - Họng')
) AS v(Ten)
WHERE NOT EXISTS (
    SELECT 1
    FROM dbo.ChuyenKhoa c
    WHERE c.TenChuyenKhoa = v.Ten
);
GO

/* =========================================================
   4. THÊM 24 BÁC SĨ NẾU CHƯA CÓ
   ========================================================= */

INSERT INTO dbo.BacSi (HoTen, ChuyenKhoaId, PhongKham)
SELECT v.HoTen, c.Id, v.PhongKham
FROM (VALUES
    (N'BS. Nguyễn Hà Phương', N'Nội khoa', N'Phòng 101'),
    (N'BS. Trần Minh Anh', N'Nội khoa', N'Phòng 102'),
    (N'BS. Lê Hoàng Nam', N'Nội khoa', N'Phòng 103'),
    (N'BS. Phạm Thu Hà', N'Nội khoa', N'Phòng 104'),

    (N'BS. Nguyễn Văn An', N'Ngoại khoa', N'Phòng 201'),
    (N'BS. Trần Quốc Việt', N'Ngoại khoa', N'Phòng 202'),
    (N'BS. Lê Văn Minh', N'Ngoại khoa', N'Phòng 203'),
    (N'BS. Hoàng Đức Long', N'Ngoại khoa', N'Phòng 204'),

    (N'BS. Nguyễn Thị Lan', N'Nhi khoa', N'Phòng 301'),
    (N'BS. Phạm Minh Hương', N'Nhi khoa', N'Phòng 302'),
    (N'BS. Trần Thu Trang', N'Nhi khoa', N'Phòng 303'),
    (N'BS. Đỗ Ngọc Anh', N'Nhi khoa', N'Phòng 304'),

    (N'BS. Nguyễn Văn Bình', N'Tim mạch', N'Phòng 401'),
    (N'BS. Trần Thị Mai', N'Tim mạch', N'Phòng 402'),
    (N'BS. Lê Quốc Huy', N'Tim mạch', N'Phòng 403'),
    (N'BS. Phạm Văn Sơn', N'Tim mạch', N'Phòng 404'),

    (N'BS. Nguyễn Thu Hà', N'Da liễu', N'Phòng 501'),
    (N'BS. Trần Ngọc Mai', N'Da liễu', N'Phòng 502'),
    (N'BS. Lê Thanh Hằng', N'Da liễu', N'Phòng 503'),
    (N'BS. Phạm Quỳnh Anh', N'Da liễu', N'Phòng 504'),

    (N'BS. Nguyễn Đức Anh', N'Tai - Mũi - Họng', N'Phòng 601'),
    (N'BS. Trần Minh Đức', N'Tai - Mũi - Họng', N'Phòng 602'),
    (N'BS. Lê Thị Hương', N'Tai - Mũi - Họng', N'Phòng 603'),
    (N'BS. Hoàng Minh Châu', N'Tai - Mũi - Họng', N'Phòng 604')
) AS v(HoTen, TenChuyenKhoa, PhongKham)
INNER JOIN dbo.ChuyenKhoa c
    ON c.TenChuyenKhoa = v.TenChuyenKhoa
WHERE NOT EXISTS (
    SELECT 1
    FROM dbo.BacSi b
    WHERE b.HoTen = v.HoTen
);
GO

/* =========================================================
   5. KIỂM TRA DANH SÁCH BÁC SĨ VÀ CHUYÊN KHOA
   ========================================================= */

SELECT
    b.Id,
    b.HoTen,
    c.TenChuyenKhoa,
    b.PhongKham,
    b.TrangThai
FROM dbo.BacSi b
LEFT JOIN dbo.ChuyenKhoa c
    ON c.Id = b.ChuyenKhoaId
ORDER BY c.Id, b.Id;
GO

/* =========================================================
   6. KIỂM TRA CHUYÊN KHOA CỦA HAI LỊCH HẸN BỊ LỖI
   Lưu ý: đang giả định dbo.LichHen có cột BacSi lưu tên.
   ========================================================= */

SELECT
    lh.Id AS MaLichHen,
    lh.BacSi AS TenBacSiTrongLichHen,
    c.TenChuyenKhoa,
    lh.NgayKham,
    lh.GioKham,
    lh.TrangThai
FROM dbo.LichHen lh
LEFT JOIN dbo.BacSi b
    ON LTRIM(RTRIM(lh.BacSi)) = LTRIM(RTRIM(b.HoTen))
LEFT JOIN dbo.ChuyenKhoa c
    ON c.Id = b.ChuyenKhoaId
WHERE lh.Id IN (17, 11)
ORDER BY lh.Id DESC;
GO
