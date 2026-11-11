import getpass
from werkzeug.security import generate_password_hash
from app import get_db_connection

ACCOUNTS = [(1, 'bs_noi'), (5, 'bs_ngoai'), (9, 'bs_nhi'),
            (13, 'bs_timmach'), (17, 'bs_dalieu'), (21, 'bs_tmh')]

password = getpass.getpass('Nhập mật khẩu demo cho 6 tài khoản (không hiển thị): ')
if len(password) < 10:
    raise ValueError('Mật khẩu cần ít nhất 10 ký tự')
conn = get_db_connection()
try:
    cursor = conn.cursor()
    cursor.execute('''
        IF OBJECT_ID(N'dbo.TaiKhoanBacSi', N'U') IS NULL
        CREATE TABLE dbo.TaiKhoanBacSi (
            BacSiId INT NOT NULL PRIMARY KEY REFERENCES dbo.BacSi(Id),
            TenDangNhap NVARCHAR(50) NOT NULL UNIQUE,
            MatKhauHash NVARCHAR(255) NOT NULL,
            KichHoat BIT NOT NULL DEFAULT 1
        )
    ''')
    for doctor_id, username in ACCOUNTS:
        cursor.execute('SELECT Id FROM dbo.BacSi WHERE Id = ?', doctor_id)
        if not cursor.fetchone():
            raise ValueError(f'Không tìm thấy bác sĩ ID {doctor_id}')
        cursor.execute('''
            IF NOT EXISTS (SELECT 1 FROM dbo.TaiKhoanBacSi WHERE BacSiId = ?)
                INSERT INTO dbo.TaiKhoanBacSi (BacSiId, TenDangNhap, MatKhauHash)
                VALUES (?, ?, ?)
        ''', doctor_id, doctor_id, username, generate_password_hash(password))
    conn.commit()
    print('Đã tạo bảng (nếu chưa có) và thêm các tài khoản chưa tồn tại.')
    print('Tài khoản:', ', '.join(u for _, u in ACCOUNTS))
except Exception:
    conn.rollback()
    raise
finally:
    conn.close()
