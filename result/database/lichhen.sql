USE MediCare;
GO

-- 1. Kiểm tra cấu trúc bảng lịch làm việc
SELECT
    TABLE_NAME,
    COLUMN_NAME,
    DATA_TYPE,
    IS_NULLABLE
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_SCHEMA = 'dbo'
  AND TABLE_NAME IN ('LichLamViec', 'LichHen')
ORDER BY TABLE_NAME, ORDINAL_POSITION;
GO

-- 2. Kiểm tra bảng lịch làm việc có dữ liệu chưa
IF OBJECT_ID('dbo.LichLamViec', 'U') IS NOT NULL
BEGIN
    SELECT TOP 20 *
    FROM dbo.LichLamViec;
END
ELSE
BEGIN
    PRINT N'Chưa có bảng LichLamViec';
END;
GO