# MediCare Admin Dashboard có đăng nhập

## Chạy trên Windows
Mở PowerShell trong thư mục dự án:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python app.py
```

Nếu PowerShell chặn `Activate.ps1`, chạy lệnh sau trong đúng cửa sổ PowerShell hiện tại rồi kích hoạt lại:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

Có thể bỏ qua bước kích hoạt môi trường và chạy trực tiếp:
```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe app.py
```

Mở http://127.0.0.1:5000. Khi chưa đăng nhập, website tự chuyển về màn đăng nhập. Sau khi đăng nhập, bấm Đăng xuất để quay lại màn đăng nhập.

## Tài khoản demo
- Tên đăng nhập: `admin`
- Mật khẩu: `Admin@12345`

## Tùy chỉnh tài khoản qua biến môi trường (PowerShell)
Trước khi chạy app, có thể đặt tài khoản khác:
```powershell
$env:MEDICARE_ADMIN_USERNAME="ten_quan_tri"
$env:MEDICARE_ADMIN_PASSWORD="mat_khau_moi"
$env:MEDICARE_SECRET_KEY="chuoi_bi_mat_dai_va_ngau_nhien"
python app.py
```

## Lưu ý
Đây là bản demo học tập. Dữ liệu lịch hẹn vẫn là dữ liệu mẫu trong bộ nhớ. Trước khi dùng thật cần lưu tài khoản trong database, CSRF protection, giới hạn thử mật khẩu, HTTPS, cấu hình secret key an toàn và triển khai không bật debug.
