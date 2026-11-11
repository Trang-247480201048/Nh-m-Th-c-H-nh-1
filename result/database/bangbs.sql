
USE MediCare;
GO

-- 1. Cac cot hien co trong bang BacSi
SELECT
    COLUMN_NAME,
    DATA_TYPE,
    IS_NULLABLE
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_SCHEMA = 'dbo'
  AND TABLE_NAME = 'BacSi'
ORDER BY ORDINAL_POSITION;

-- 2. Cac cot hien co trong bang ChuyenKhoa
SELECT
    COLUMN_NAME,
    DATA_TYPE,
    IS_NULLABLE
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_SCHEMA = 'dbo'
  AND TABLE_NAME = 'ChuyenKhoa'
ORDER BY ORDINAL_POSITION;

-- 3. Kiem tra bang LichLamViec da ton tai chua
SELECT
    COLUMN_NAME,
    DATA_TYPE,
    IS_NULLABLE
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_SCHEMA = 'dbo'
  AND TABLE_NAME = 'LichLamViec'
ORDER BY ORDINAL_POSITION;

-- 4. Kiem tra du lieu bac si hien tai
SELECT TOP 30
    bs.*,
    ck.TenChuyenKhoa
FROM dbo.BacSi AS bs
LEFT JOIN dbo.ChuyenKhoa AS ck
    ON bs.ChuyenKhoaId = ck.Id
ORDER BY bs.Id;
