IF DB_ID(N'MediCare') IS NULL
BEGIN
    CREATE DATABASE MediCare;
END
GO

USE MediCare;
GO

IF OBJECT_ID(N'dbo.LichHen', N'U') IS NULL
BEGIN
    CREATE TABLE dbo.LichHen (
        Id INT IDENTITY(1,1) PRIMARY KEY,
        HoTen NVARCHAR(100) NOT NULL,
        SoDienThoai NVARCHAR(20) NOT NULL,
        BacSi NVARCHAR(100) NOT NULL,
        NgayKham DATE NOT NULL,
        GioKham NVARCHAR(10) NOT NULL,
        LyDo NVARCHAR(500) NULL,
        TrangThai NVARCHAR(30) NOT NULL
            CONSTRAINT DF_LichHen_TrangThai
            DEFAULT N'Chờ xác nhận',
        NgayTao DATETIME2 NOT NULL
            CONSTRAINT DF_LichHen_NgayTao
            DEFAULT SYSDATETIME()
    );
END
GO

SELECT DB_NAME() AS DatabaseName;
SELECT name FROM sys.tables;
GO