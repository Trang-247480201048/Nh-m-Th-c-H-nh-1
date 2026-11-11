
USE MediCare;
GO

-- 1. Them cot BacSiId neu chua ton tai
IF COL_LENGTH('dbo.LichHen', 'BacSiId') IS NULL
BEGIN
    ALTER TABLE dbo.LichHen
    ADD BacSiId INT NULL;
END;
GO

-- 2. Lien ket cac lich hen cu voi bang BacSi
-- Doi chieu theo ten bac si dang luu trong LichHen
UPDATE lh
SET lh.BacSiId = bs.Id
FROM dbo.LichHen AS lh
INNER JOIN dbo.BacSi AS bs
    ON LTRIM(RTRIM(lh.BacSi)) = LTRIM(RTRIM(bs.HoTen))
WHERE lh.BacSiId IS NULL;
GO

-- 3. Them khoa ngoai neu chua ton tai
IF NOT EXISTS (
    SELECT 1
    FROM sys.foreign_keys
    WHERE name = 'FK_LichHen_BacSi'
      AND parent_object_id = OBJECT_ID('dbo.LichHen')
)
BEGIN
    ALTER TABLE dbo.LichHen
    ADD CONSTRAINT FK_LichHen_BacSi
        FOREIGN KEY (BacSiId)
        REFERENCES dbo.BacSi(Id);
END;
GO

-- 4. Kiem tra ket qua lien ket
SELECT
    lh.Id,
    lh.HoTen,
    lh.BacSi AS TenBacSiCu,
    lh.BacSiId,
    bs.HoTen AS TenBacSi,
    ck.TenChuyenKhoa,
    lh.NgayKham,
    lh.GioKham,
    lh.TrangThai
FROM dbo.LichHen AS lh
LEFT JOIN dbo.BacSi AS bs
    ON lh.BacSiId = bs.Id
LEFT JOIN dbo.ChuyenKhoa AS ck
    ON bs.ChuyenKhoaId = ck.Id
ORDER BY lh.Id;
GO
