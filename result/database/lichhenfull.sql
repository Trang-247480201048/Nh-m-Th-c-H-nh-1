
USE MediCare;
GO

DECLARE @NgayBatDau DATE = '2026-10-28';
DECLARE @SoNgay INT = 30;

;WITH DanhSachNgay AS
(
    SELECT 0 AS NgayThu
    UNION ALL
    SELECT NgayThu + 1
    FROM DanhSachNgay
    WHERE NgayThu + 1 < @SoNgay
),
CaLam AS
(
    SELECT
        CAST('08:00' AS TIME) AS GioBatDau,
        CAST('12:00' AS TIME) AS GioKetThuc,
        N'Ca sáng - dữ liệu kiểm thử' AS GhiChu
    UNION ALL
    SELECT
        CAST('13:00' AS TIME),
        CAST('17:00' AS TIME),
        N'Ca chiều - dữ liệu kiểm thử'
)
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
    DATEADD(DAY, n.NgayThu, @NgayBatDau),
    c.GioBatDau,
    c.GioKetThuc,
    8,
    c.GhiChu,
    1,
    GETDATE()
FROM dbo.BacSi bs
CROSS JOIN DanhSachNgay n
CROSS JOIN CaLam c
WHERE NOT EXISTS
(
    SELECT 1
    FROM dbo.LichLamViec llv
    WHERE llv.BacSiId = bs.Id
      AND llv.NgayLamViec =
          DATEADD(DAY, n.NgayThu, @NgayBatDau)
      AND llv.GioBatDau = c.GioBatDau
      AND llv.GioKetThuc = c.GioKetThuc
)
OPTION (MAXRECURSION 100);
GO

-- Kiểm tra số lượng ca theo ngày
SELECT
    NgayLamViec,
    COUNT(*) AS TongSoCa,
    COUNT(DISTINCT BacSiId) AS SoBacSi
FROM dbo.LichLamViec
WHERE NgayLamViec BETWEEN '2026-10-28' AND '2026-11-26'
GROUP BY NgayLamViec
ORDER BY NgayLamViec;
GO
