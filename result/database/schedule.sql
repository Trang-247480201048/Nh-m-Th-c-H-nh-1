
USE MediCare;
GO

-- Tạo ca làm việc ngày 28/10/2026 cho tất cả bác sĩ
-- Ca sáng: 08:00 - 12:00
-- Ca chiều: 13:00 - 17:00

DECLARE @NgayLamViec DATE = '2026-10-28';

-- Ca sáng
INSERT INTO dbo.LichLamViec
(
    BacSiId,
    NgayLamViec,
    GioBatDau,
    GioKetThuc,
    SoLuongToiDa,
    GhiChu,
    TrangThai,
    NgayTao
)
SELECT
    bs.Id,
    @NgayLamViec,
    '08:00',
    '12:00',
    8,
    N'Ca sáng - dữ liệu kiểm thử',
    1,
    GETDATE()
FROM dbo.BacSi AS bs
WHERE NOT EXISTS
(
    SELECT 1
    FROM dbo.LichLamViec AS llv
    WHERE llv.BacSiId = bs.Id
      AND llv.NgayLamViec = @NgayLamViec
      AND llv.GioBatDau = '08:00'
      AND llv.GioKetThuc = '12:00'
);

-- Ca chiều
INSERT INTO dbo.LichLamViec
(
    BacSiId,
    NgayLamViec,
    GioBatDau,
    GioKetThuc,
    SoLuongToiDa,
    GhiChu,
    TrangThai,
    NgayTao
)
SELECT
    bs.Id,
    @NgayLamViec,
    '13:00',
    '17:00',
    8,
    N'Ca chiều - dữ liệu kiểm thử',
    1,
    GETDATE()
FROM dbo.BacSi AS bs
WHERE NOT EXISTS
(
    SELECT 1
    FROM dbo.LichLamViec AS llv
    WHERE llv.BacSiId = bs.Id
      AND llv.NgayLamViec = @NgayLamViec
      AND llv.GioBatDau = '13:00'
      AND llv.GioKetThuc = '17:00'
);

-- Kiểm tra kết quả
SELECT
    bs.Id AS BacSiId,
    bs.HoTen,
    llv.NgayLamViec,
    llv.GioBatDau,
    llv.GioKetThuc,
    llv.SoLuongToiDa,
    llv.TrangThai
FROM dbo.BacSi AS bs
LEFT JOIN dbo.LichLamViec AS llv
    ON llv.BacSiId = bs.Id
    AND llv.NgayLamViec = @NgayLamViec
ORDER BY bs.Id, llv.GioBatDau;
GO
SELECT
    COUNT(*) AS TongSoBacSi,
    COUNT(DISTINCT BacSiId) AS SoBacSiCoCa
FROM dbo.LichLamViec
WHERE NgayLamViec = '2026-10-28';