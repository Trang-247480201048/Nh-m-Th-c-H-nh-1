USE MediCare;
GO

IF OBJECT_ID('dbo.LichLamViec', 'U') IS NULL
BEGIN
    CREATE TABLE dbo.LichLamViec
    (
        Id INT IDENTITY(1,1) PRIMARY KEY,
        BacSiId INT NOT NULL,
        NgayLamViec DATE NOT NULL,
        GioBatDau TIME(0) NOT NULL,
        GioKetThuc TIME(0) NOT NULL,
        SoLuongToiDa INT NOT NULL DEFAULT 14,
        GhiChu NVARCHAR(255) NULL,
        TrangThai BIT NOT NULL DEFAULT 1,
        NgayTao DATETIME2 NOT NULL DEFAULT SYSDATETIME(),

        CONSTRAINT FK_LichLamViec_BacSi
            FOREIGN KEY (BacSiId) REFERENCES dbo.BacSi(Id),

        CONSTRAINT CK_LichLamViec_Gio
            CHECK (GioKetThuc > GioBatDau),

        CONSTRAINT CK_LichLamViec_SoLuong
            CHECK (SoLuongToiDa > 0)
    );
END;
GO
SELECT *
FROM dbo.LichLamViec;

SELECT
    bs.Id,
    bs.HoTen,
    ck.TenChuyenKhoa,
    bs.PhongKham,
    bs.TrangThai
FROM dbo.BacSi AS bs
JOIN dbo.ChuyenKhoa AS ck
    ON bs.ChuyenKhoaId = ck.Id
ORDER BY bs.Id;