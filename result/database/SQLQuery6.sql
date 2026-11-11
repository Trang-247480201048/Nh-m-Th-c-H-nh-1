USE MediCare;
GO


IF OBJECT_ID('dbo.TaiKhoanNguoiDung', 'U') IS NULL
BEGIN
    CREATE TABLE dbo.TaiKhoanNguoiDung (
        Id INT IDENTITY(1,1) PRIMARY KEY,
        HoTen NVARCHAR(100) NOT NULL,
        SoDienThoai VARCHAR(15) NOT NULL,
        Email NVARCHAR(255) NULL,
        MatKhau NVARCHAR(255) NOT NULL,
        NgayTao DATETIME2 NOT NULL
            DEFAULT SYSDATETIME(),
        TrangThai NVARCHAR(30) NOT NULL
            DEFAULT N'Hoạt động',

        CONSTRAINT UQ_TaiKhoan_SoDienThoai
            UNIQUE (SoDienThoai)
    );

    CREATE UNIQUE INDEX UX_TaiKhoan_Email
    ON dbo.TaiKhoanNguoiDung(Email)
    WHERE Email IS NOT NULL;
END;
GO


IF COL_LENGTH('dbo.TaiKhoanNguoiDung', 'NgaySinh') IS NULL
BEGIN
    ALTER TABLE dbo.TaiKhoanNguoiDung
    ADD NgaySinh DATE NULL;
END;
GO


SELECT * FROM dbo.TaiKhoanNguoiDung;
GO