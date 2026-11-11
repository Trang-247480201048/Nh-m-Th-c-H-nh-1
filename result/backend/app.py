
import os
import logging
import re
from datetime import date, datetime

import pyodbc
from flask import Flask, jsonify, request, session
from flask_cors import CORS
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash


# ==================================================
# 1. CAU HINH UNG DUNG
# ==================================================

load_dotenv()

app = Flask(__name__)

app.secret_key = os.getenv(
    "MEDICARE_SECRET_KEY",
    "change-this-secret-key-before-deployment"
)

CORS(
    app,
    resources={
        r"/api/*": {
            "origins": [
                "http://127.0.0.1:5500",
                "http://localhost:5500",
                "http://127.0.0.1:5001",
                "http://localhost:5001"
            ]
        }
    },
    supports_credentials=True
)

logging.basicConfig(level=logging.INFO)

SERVER = os.getenv("SQL_SERVER")
DATABASE = os.getenv("SQL_DATABASE", "MediCare")
DRIVER = os.getenv(
    "SQL_DRIVER",
    "ODBC Driver 18 for SQL Server"
)


# ==================================================
# 2. KET NOI SQL SERVER
# ==================================================

def get_connection():
    if not SERVER:
        raise RuntimeError(
            "Chua cau hinh SQL_SERVER trong file .env"
        )

    connection_string = (
        f"DRIVER={{{DRIVER}}};"
        f"SERVER={SERVER};"
        f"DATABASE={DATABASE};"
        "Trusted_Connection=yes;"
        "TrustServerCertificate=yes;"
    )

    return pyodbc.connect(
        connection_string,
        timeout=5
    )


# ==================================================
# 3. HAM TRA VE LOI JSON
# ==================================================

def error_response(message, status_code=500):
    return jsonify({
        "status": "error",
        "message": message
    }), status_code


# ==================================================
# 4. HAM DINH DANG NGAY GIO
# ==================================================

def format_date(value):
    if value is None:
        return ""

    if hasattr(value, "strftime"):
        return value.strftime("%Y-%m-%d")

    return str(value)[:10]


def format_time(value):
    if value is None:
        return ""

    if hasattr(value, "strftime"):
        return value.strftime("%H:%M")

    return str(value)[:5]


# ==================================================
# 5. TRANG KIEM TRA BACKEND
# GET /
# ==================================================

@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "message": "MediCare Backend dang hoat dong!",
        "status": "success"
    })


# ==================================================
# 6. KIEM TRA KET NOI SQL SERVER
# GET /api/kiem-tra
# ==================================================

@app.route("/api/kiem-tra", methods=["GET"])
def kiem_tra():
    conn = None

    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT DB_NAME()")
        database_name = cursor.fetchone()[0]

        cursor.close()

        return jsonify({
            "status": "success",
            "message": "Ket noi SQL Server thanh cong!",
            "database": database_name
        })

    except Exception:
        logging.exception("Loi kiem tra SQL Server")

        return error_response(
            "Khong the ket noi SQL Server. "
            "Hay kiem tra file .env va dich vu SQL Server.",
            500
        )

    finally:
        if conn:
            conn.close()


# ==================================================
# 7. API LAY DANH SACH LICH HEN
# GET /api/lich-hen
# ==================================================

@app.route("/api/lich-hen", methods=["GET"])
def danh_sach_lich_hen():
    conn = None

    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                lh.Id,
                lh.HoTen,
                lh.SoDienThoai,
                COALESCE(bs.HoTen, lh.BacSi) AS TenBacSi,
                lh.BacSiId,
                lh.NgayKham,
                lh.GioKham,
                lh.LyDo,
                lh.TrangThai,
                lh.NgayTao
            FROM dbo.LichHen AS lh
            LEFT JOIN dbo.BacSi AS bs
                ON lh.BacSiId = bs.Id
            ORDER BY lh.Id DESC
        """)

        rows = cursor.fetchall()
        data = []

        for row in rows:
            data.append({
                "id": row.Id,
                "ho_ten": row.HoTen or "",
                "so_dien_thoai": row.SoDienThoai or "",
                "bac_si": row.TenBacSi or "",
                "bac_si_id": row.BacSiId,
                "ngay_kham": format_date(row.NgayKham),
                "gio_kham": format_time(row.GioKham),
                "ly_do": row.LyDo or "",
                "trang_thai": row.TrangThai or "Chờ xác nhận",
                "ngay_tao": (
                    row.NgayTao.isoformat()
                    if row.NgayTao else ""
                )
            })

        cursor.close()

        return jsonify({
            "status": "success",
            "count": len(data),
            "data": data
        })

    except Exception:
        logging.exception("Loi lay danh sach lich hen")

        return error_response(
            "Khong the lay danh sach lich hen.",
            500
        )

    finally:
        if conn:
            conn.close()


# ==================================================
# 8. API TAO LICH HEN
# POST /api/lich-hen
# Moi khung gio 30 phut chi nhan 1 benh nhan
# ==================================================

@app.route("/api/lich-hen", methods=["POST"])
def tao_lich_hen():
    data = request.get_json(silent=True) or {}

    ho_ten = str(data.get("ho_ten") or "").strip()
    so_dien_thoai = re.sub(
        r"\s+", "", str(data.get("so_dien_thoai") or "")
    )
    bac_si = str(data.get("bac_si") or "").strip()
    ngay_kham = str(data.get("ngay_kham") or "").strip()
    gio_kham = str(data.get("gio_kham") or "").strip()
    ly_do = str(data.get("ly_do") or "").strip()
    bac_si_id_raw = data.get("bac_si_id")

    # 1. Kiem tra du lieu bat buoc
    if not ho_ten or not so_dien_thoai or not ngay_kham or not gio_kham:
        return error_response(
            "Vui lòng nhập đầy đủ thông tin bắt buộc.", 400
        )

    if not re.fullmatch(r"(0\d{9}|\+84\d{9})", so_dien_thoai):
        return error_response("Số điện thoại không hợp lệ.", 400)

    if len(ho_ten) > 150 or len(ly_do) > 1000:
        return error_response("Thông tin nhập quá dài.", 400)

    if bac_si_id_raw is None and not bac_si:
        return error_response("Vui lòng chọn bác sĩ.", 400)

    # 2. Kiem tra ngay
    try:
        ngay_kham_obj = date.fromisoformat(ngay_kham)
    except ValueError:
        return error_response("Ngày khám không hợp lệ.", 400)

    if ngay_kham_obj < date.today():
        return error_response("Không thể đặt lịch cho ngày đã qua.", 400)

    # 3. Kiem tra gio bat dau cua khung 30 phut
    if not re.fullmatch(r"\d{2}:\d{2}", gio_kham):
        return error_response("Giờ khám không hợp lệ.", 400)

    hour, minute = map(int, gio_kham.split(":"))

    if hour > 23 or minute not in (0, 30):
        return error_response(
            "Giờ khám phải bắt đầu ở phút 00 hoặc 30.", 400
        )

    conn = None

    try:
        conn = get_connection()
        cursor = conn.cursor()

        # Bat dau transaction de tranh hai nguoi dat cung mot khung gio
        cursor.execute("SET TRANSACTION ISOLATION LEVEL SERIALIZABLE")

        # 4. Kiem tra bac si
        if bac_si_id_raw is not None:
            try:
                bac_si_id = int(bac_si_id_raw)
            except (TypeError, ValueError):
                return error_response("Mã bác sĩ không hợp lệ.", 400)

            cursor.execute("""
                SELECT Id, HoTen
                FROM dbo.BacSi
                WHERE Id = ? AND TrangThai = 1
            """, (bac_si_id,))
        else:
            cursor.execute("""
                SELECT Id, HoTen
                FROM dbo.BacSi
                WHERE HoTen = ? AND TrangThai = 1
            """, (bac_si,))

        doctor = cursor.fetchone()

        if not doctor:
            conn.rollback()
            return error_response(
                "Không tìm thấy bác sĩ đang hoạt động.", 400
            )

        bac_si_id = doctor[0]
        ten_bac_si = doctor[1]

        # 5. Kiem tra ca lam viec co chua tron 30 phut khong
        cursor.execute("""
            SELECT TOP 1
                Id,
                SoLuongToiDa
            FROM dbo.LichLamViec WITH (UPDLOCK, HOLDLOCK)
            WHERE BacSiId = ?
              AND NgayLamViec = ?
              AND TrangThai = 1
              AND CAST(GioBatDau AS time) <= CAST(? AS time)
              AND CAST(GioKetThuc AS time) >= DATEADD(
                    MINUTE, 30, CAST(? AS time)
              )
            ORDER BY GioBatDau
        """, (
            bac_si_id,
            ngay_kham_obj,
            gio_kham,
            gio_kham
        ))

        shift = cursor.fetchone()

        if not shift:
            conn.rollback()
            return error_response(
                "Khung giờ không thuộc ca làm việc đang mở "
                "hoặc không đủ 30 phút. Vui lòng chọn giờ khác.",
                409
            )

        # 6. Kiem tra khung gio da co benh nhan dat chua
        cursor.execute("""
            SELECT COUNT(*)
            FROM dbo.LichHen WITH (UPDLOCK, HOLDLOCK)
            WHERE BacSiId = ?
              AND NgayKham = ?
              AND CAST(GioKham AS time) = CAST(? AS time)
              AND (
                    TrangThai IS NULL
                    OR TrangThai <> N'Đã hủy'
              )
        """, (
            bac_si_id,
            ngay_kham_obj,
            gio_kham
        ))

        booked_count = cursor.fetchone()[0]

        # Moi khung 30 phut chi nhan 1 benh nhan
        if booked_count >= 1:
            conn.rollback()
            return error_response(
                "Khung giờ này đã có bệnh nhân đặt. "
                "Vui lòng chọn khung giờ khác.",
                409
            )

        # 7. Luu lich hen vao SQL Server
        cursor.execute("""
            INSERT INTO dbo.LichHen
            (
                HoTen,
                SoDienThoai,
                BacSi,
                BacSiId,
                NgayKham,
                GioKham,
                LyDo
            )
            OUTPUT INSERTED.Id
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            ho_ten,
            so_dien_thoai,
            ten_bac_si,
            bac_si_id,
            ngay_kham_obj,
            gio_kham,
            ly_do or None
        ))

        new_id = cursor.fetchone()[0]

        conn.commit()

        return jsonify({
            "status": "success",
            "message": "Đặt lịch khám thành công!",
            "id": new_id,
            "code": f"LH-{new_id:06d}",
            "bac_si_id": bac_si_id,
            "bac_si": ten_bac_si,
            "ngay_kham": ngay_kham,
            "gio_kham": gio_kham
        }), 201

    except Exception:
        if conn:
            conn.rollback()

        logging.exception("Loi tao lich hen")

        return error_response(
            "Không thể tạo lịch hẹn. "
            "Hãy kiểm tra dữ liệu và SQL Server.",
            500
        )

    finally:
        if conn:
            conn.close()

# ==================================================
# 9. API LAY DANH SACH BAC SI
# GET /api/bac-si
# ==================================================

@app.route("/api/bac-si", methods=["GET"])
def danh_sach_bac_si():
    conn = None

    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                bs.Id,
                bs.HoTen,
                ck.TenChuyenKhoa,
                bs.PhongKham,
                bs.TrangThai
            FROM dbo.BacSi AS bs
            LEFT JOIN dbo.ChuyenKhoa AS ck
                ON bs.ChuyenKhoaId = ck.Id
            WHERE bs.TrangThai = 1
            ORDER BY ck.TenChuyenKhoa, bs.HoTen
        """)

        rows = cursor.fetchall()
        data = []

        for row in rows:
            data.append({
                "id": row[0],
                "name": row[1] or "",
                "specialty": row[2] or "Chưa phân loại",
                "room": row[3] or "",
                "active": bool(row[4])
            })

        cursor.close()

        return jsonify({
            "status": "success",
            "count": len(data),
            "data": data
        })

    except Exception:
        logging.exception("Loi lay danh sach bac si")

        return error_response(
            "Khong the lay danh sach bac si. "
            "Hay kiem tra bang BacSi va ChuyenKhoa.",
            500
        )

    finally:
        if conn:
            conn.close()


# ==================================================
# 10. API LAY KHUNG GIO LAM VIEC CUA BAC SI
# GET /api/lich-lam-viec
# ==================================================

@app.get("/api/lich-lam-viec")
def lay_khung_gio_lam_viec():
    bac_si_id = request.args.get("bac_si_id", type=int)
    ngay_kham = request.args.get("ngay_kham", "").strip()

    if not bac_si_id or not ngay_kham:
        return error_response(
            "Vui lòng cung cấp mã bác sĩ và ngày khám.", 400
        )

    try:
        ngay_kham_obj = date.fromisoformat(ngay_kham)
    except ValueError:
        return error_response("Ngày khám không hợp lệ.", 400)

    if ngay_kham_obj < date.today():
        return error_response(
            "Không thể xem lịch khám của ngày đã qua.", 400
        )

    conn = None

    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                llv.Id,
                llv.GioBatDau,
                llv.GioKetThuc
            FROM dbo.LichLamViec AS llv
            INNER JOIN dbo.BacSi AS bs
                ON bs.Id = llv.BacSiId
            WHERE llv.BacSiId = ?
              AND llv.NgayLamViec = ?
              AND llv.TrangThai = 1
              AND bs.TrangThai = 1
            ORDER BY llv.GioBatDau
        """, (bac_si_id, ngay_kham_obj))

        shifts = cursor.fetchall()
        slots = []

        for shift in shifts:
            start_minutes = (
                shift.GioBatDau.hour * 60
                + shift.GioBatDau.minute
            )

            end_minutes = (
                shift.GioKetThuc.hour * 60
                + shift.GioKetThuc.minute
            )

            current = start_minutes

            # Chia ca lam viec thanh cac khung 30 phut
            while current + 30 <= end_minutes:
                slot_start = (
                    f"{current // 60:02d}:{current % 60:02d}"
                )
                slot_end_minutes = current + 30
                slot_end = (
                    f"{slot_end_minutes // 60:02d}:"
                    f"{slot_end_minutes % 60:02d}"
                )

                cursor.execute("""
                    SELECT COUNT(*)
                    FROM dbo.LichHen
                    WHERE BacSiId = ?
                      AND NgayKham = ?
                      AND CAST(GioKham AS time) = CAST(? AS time)
                      AND (
                            TrangThai IS NULL
                            OR TrangThai <> N'Đã hủy'
                      )
                """, (
                    bac_si_id,
                    ngay_kham_obj,
                    slot_start
                ))

                booked_count = cursor.fetchone()[0]

                slots.append({
                    "shift_id": shift.Id,
                    "start": slot_start,
                    "end": slot_end,
                    "time": f"{slot_start} - {slot_end}",
                    "capacity": 1,
                    "booked": booked_count,
                    "available": booked_count == 0
                })

                current += 30

        cursor.close()

        return jsonify({
            "status": "success",
            "count": len(slots),
            "data": slots
        })

    except Exception:
        logging.exception("Loi lay khung gio lam viec")

        return error_response(
            "Không thể tải khung giờ làm việc của bác sĩ.", 500
        )

    finally:
        if conn:
            conn.close()


# ==================================================
# 11. API THEM BAC SI
# POST /api/bac-si
# ==================================================

@app.route("/api/bac-si", methods=["POST"])
def them_bac_si():
    data = request.get_json(silent=True) or {}

    ho_ten = str(
        data.get("name") or ""
    ).strip()

    chuyen_khoa = str(
        data.get("specialty") or ""
    ).strip()

    phong_kham = str(
        data.get("room") or ""
    ).strip()

    if not ho_ten or not chuyen_khoa:
        return error_response(
            "Vui long nhap ten bac si va chuyen khoa.",
            400
        )

    conn = None

    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT Id
            FROM dbo.ChuyenKhoa
            WHERE TenChuyenKhoa = ?
        """, (chuyen_khoa,))

        specialty_row = cursor.fetchone()

        if specialty_row is None:
            return error_response(
                "Chuyen khoa chua ton tai trong co so du lieu.",
                400
            )

        specialty_id = specialty_row[0]

        cursor.execute("""
            SELECT COUNT(*)
            FROM dbo.BacSi
            WHERE HoTen = ?
              AND ChuyenKhoaId = ?
        """, (
            ho_ten,
            specialty_id
        ))

        if cursor.fetchone()[0] > 0:
            return error_response(
                "Bac si nay da ton tai trong chuyen khoa.",
                409
            )

        cursor.execute("""
            INSERT INTO dbo.BacSi
            (
                HoTen,
                ChuyenKhoaId,
                PhongKham,
                TrangThai
            )
            OUTPUT INSERTED.Id
            VALUES (?, ?, ?, 1)
        """, (
            ho_ten,
            specialty_id,
            phong_kham or None
        ))

        new_id = cursor.fetchone()[0]

        conn.commit()
        cursor.close()

        return jsonify({
            "status": "success",
            "message": "Them bac si thanh cong!",
            "data": {
                "id": new_id,
                "name": ho_ten,
                "specialty": chuyen_khoa,
                "room": phong_kham,
                "active": True
            }
        }), 201

    except Exception:
        if conn:
            conn.rollback()

        logging.exception("Loi them bac si")

        return error_response(
            "Khong the them bac si. "
            "Hay kiem tra du lieu SQL Server.",
            500
        )

    finally:
        if conn:
            conn.close()


# ==================================================
# 12. API DANG NHAP TAI KHOAN
# POST /api/auth/login
# ==================================================

@app.post("/api/auth/login")
def login_user():
    data = request.get_json(silent=True) or {}

    username = str(
        data.get("username", "")
    ).strip()

    password = str(
        data.get("password", "")
    )

    if not username or not password:
        return jsonify({
            "success": False,
            "message": (
                "Vui lòng nhập số điện thoại/email "
                "và mật khẩu."
            )
        }), 400

    conn = None

    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                Id,
                HoTen,
                SoDienThoai,
                Email,
                MatKhauHash,
                TrangThai
            FROM dbo.TaiKhoanNguoiDung
            WHERE SoDienThoai = ?
               OR Email = ?
        """, (
            username,
            username.lower()
        ))

        user = cursor.fetchone()
        cursor.close()

        if not user:
            return jsonify({
                "success": False,
                "message": (
                    "Thông tin đăng nhập không đúng "
                    "hoặc tài khoản không hoạt động."
                )
            }), 401

        if not check_password_hash(
            user.MatKhauHash,
            password
        ):
            return jsonify({
                "success": False,
                "message": (
                    "Thông tin đăng nhập không đúng "
                    "hoặc tài khoản không hoạt động."
                )
            }), 401

        if user.TrangThai != "Hoạt động":
            return jsonify({
                "success": False,
                "message": (
                    "Thông tin đăng nhập không đúng "
                    "hoặc tài khoản không hoạt động."
                )
            }), 401

        session.clear()

        session["user_id"] = user.Id
        session["user_name"] = user.HoTen

        return jsonify({
            "success": True,
            "message": "Đăng nhập thành công.",
            "user": {
                "id": user.Id,
                "fullname": user.HoTen,
                "phone": user.SoDienThoai,
                "email": user.Email or ""
            }
        })

    except Exception:
        app.logger.exception(
            "Loi dang nhap tai khoan"
        )

        return jsonify({
            "success": False,
            "message": (
                "Không thể đăng nhập lúc này. "
                "Vui lòng thử lại."
            )
        }), 500

    finally:
        if conn:
            conn.close()


# ==================================================
# 13. API DANG KY TAI KHOAN
# POST /api/auth/register
# ==================================================

@app.post("/api/auth/register")
def register_user():
    data = request.get_json(silent=True) or {}

    fullname = str(
        data.get("fullname", "")
    ).strip()

    birthday = str(
        data.get("birthday", "")
    ).strip()

    phone = str(
        data.get("phone", "")
    ).strip()

    email = str(
        data.get("email", "")
    ).strip().lower()

    password = str(
        data.get("password", "")
    )

    if not fullname or not phone or not password:
        return jsonify({
            "success": False,
            "message": (
                "Vui lòng nhập họ tên, số điện thoại "
                "và mật khẩu."
            )
        }), 400

    if len(password) < 8:
        return jsonify({
            "success": False,
            "message": (
                "Mật khẩu phải có ít nhất 8 ký tự."
            )
        }), 400

    if not re.fullmatch(
        r"[0-9+() .-]{9,20}",
        phone
    ):
        return jsonify({
            "success": False,
            "message": "Số điện thoại không hợp lệ."
        }), 400

    if email and not re.fullmatch(
        r"[^@\s]+@[^@\s]+\.[^@\s]+",
        email
    ):
        return jsonify({
            "success": False,
            "message": "Email không hợp lệ."
        }), 400

    try:
        birth_date = (
            date.fromisoformat(birthday)
            if birthday else None
        )

        if birth_date and birth_date > date.today():
            return jsonify({
                "success": False,
                "message": (
                    "Ngày sinh không được ở tương lai."
                )
            }), 400

    except ValueError:
        return jsonify({
            "success": False,
            "message": "Ngày sinh không hợp lệ."
        }), 400

    password_hash = generate_password_hash(password)
    conn = None

    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT Id
            FROM dbo.TaiKhoanNguoiDung
            WHERE SoDienThoai = ?
               OR (? <> '' AND Email = ?)
        """, (
            phone,
            email,
            email
        ))

        if cursor.fetchone():
            return jsonify({
                "success": False,
                "message": (
                    "Số điện thoại hoặc email "
                    "đã được đăng ký."
                )
            }), 409

        cursor.execute("""
            INSERT INTO dbo.TaiKhoanNguoiDung
            (
                HoTen,
                SoDienThoai,
                Email,
                NgaySinh,
                MatKhauHash,
                TrangThai
            )
            OUTPUT INSERTED.Id
            VALUES (?, ?, ?, ?, ?, N'Hoạt động')
        """, (
            fullname,
            phone,
            email or None,
            birth_date,
            password_hash
        ))

        user_id = cursor.fetchone()[0]

        conn.commit()
        cursor.close()

        return jsonify({
            "success": True,
            "message": "Đăng ký tài khoản thành công.",
            "user": {
                "id": user_id,
                "fullname": fullname,
                "phone": phone,
                "email": email
            }
        }), 201

    except Exception:
        if conn:
            conn.rollback()

        app.logger.exception(
            "Loi dang ky tai khoan"
        )

        return jsonify({
            "success": False,
            "message": (
                "Không thể đăng ký lúc này. "
                "Vui lòng thử lại."
            )
        }), 500

    finally:
        if conn:
            conn.close()


# ==================================================
# 14. API DANG XUAT
# POST /api/auth/logout
# ==================================================

@app.post("/api/auth/logout")
def logout_user():
    session.pop("user_id", None)
    session.pop("user_name", None)

    return jsonify({
        "success": True,
        "message": "Đã đăng xuất."
    })


# ==================================================
# 15. API LAY TAI KHOAN DANG DANG NHAP
# GET /api/auth/me
# ==================================================

@app.get("/api/auth/me")
def current_user():
    user_id = session.get("user_id")

    if not user_id:
        return jsonify({
            "success": False,
            "message": "Bạn chưa đăng nhập."
        }), 401

    conn = None

    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                Id,
                HoTen,
                SoDienThoai,
                Email
            FROM dbo.TaiKhoanNguoiDung
            WHERE Id = ?
              AND TrangThai = N'Hoạt động'
        """, (user_id,))

        user = cursor.fetchone()

        cursor.close()

        if not user:
            session.pop("user_id", None)
            session.pop("user_name", None)

            return jsonify({
                "success": False,
                "message": (
                    "Tài khoản không tồn tại "
                    "hoặc đã bị khóa."
                )
            }), 401

        return jsonify({
            "success": True,
            "user": {
                "id": user.Id,
                "fullname": user.HoTen,
                "phone": user.SoDienThoai,
                "email": user.Email or ""
            }
        })

    except Exception:
        app.logger.exception(
            "Loi lay tai khoan dang dang nhap"
        )

        return jsonify({
            "success": False,
            "message": (
                "Không thể kiểm tra tài khoản lúc này."
            )
        }), 500

    finally:
        if conn:
            conn.close()


# ==================================================
# 16. API LICH SU KHAM BENH CUA BENH NHAN
# GET /api/my-appointments?phone=...
# ==================================================

@app.get("/api/my-appointments")
def my_appointments():
    phone = request.args.get(
        "phone",
        ""
    ).strip()

    if not phone:
        return jsonify({
            "success": False,
            "message": "Vui lòng cung cấp số điện thoại."
        }), 400

    normalized_phone = re.sub(
        r"\D",
        "",
        phone
    )

    conn = None

    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                lh.Id,
                lh.HoTen,
                lh.SoDienThoai,
                COALESCE(bs.HoTen, lh.BacSi) AS TenBacSi,
                ck.TenChuyenKhoa,
                lh.NgayKham,
                lh.GioKham,
                lh.LyDo,
                lh.TrangThai
            FROM dbo.LichHen AS lh
            LEFT JOIN dbo.BacSi AS bs
                ON lh.BacSiId = bs.Id
            LEFT JOIN dbo.ChuyenKhoa AS ck
                ON bs.ChuyenKhoaId = ck.Id
            WHERE REPLACE(
                    REPLACE(
                        REPLACE(
                            REPLACE(lh.SoDienThoai, ' ', ''),
                            '-',
                            ''
                        ),
                        '.',
                        ''
                    ),
                    '+',
                    ''
                  ) = ?
            ORDER BY lh.Id DESC
        """, (normalized_phone,))

        rows = cursor.fetchall()
        appointments = []

        for row in rows:
            row_phone = re.sub(
                r"\D",
                "",
                str(row.SoDienThoai or "")
            )

            if row_phone != normalized_phone:
                continue

            appointments.append({
                "id": row.Id,
                "code": f"LH-{row.Id:06d}",
                "patient": row.HoTen or "",
                "phone": row.SoDienThoai or "",
                "doctor": row.TenBacSi or "",
                "specialty": (
                    row.TenChuyenKhoa
                    or "Chưa có thông tin"
                ),
                "date": format_date(row.NgayKham),
                "time": format_time(row.GioKham),
                "reason": row.LyDo or "",
                "status": row.TrangThai or "Chờ xác nhận"
            })

        cursor.close()

        return jsonify({
            "success": True,
            "appointments": appointments
        })

    except Exception:
        app.logger.exception(
            "Loi lay lich su kham benh"
        )

        return jsonify({
            "success": False,
            "message": (
                "Không thể tải lịch sử khám bệnh."
            )
        }), 500

    finally:
        if conn:
            conn.close()
# ==================================================
# 17. API LAY DANH SACH BENH NHAN
# GET /api/benh-nhan
# ==================================================

@app.route("/api/benh-nhan", methods=["GET"])
def danh_sach_benh_nhan():
    conn = None

    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            WITH LichHenTongHop AS (
                SELECT
                    REPLACE(
                        REPLACE(
                            REPLACE(
                                REPLACE(SoDienThoai, ' ', ''),
                                '-',
                                ''
                            ),
                            '.',
                            ''
                        ),
                        '+',
                        ''
                    ) AS SoDienThoaiKey,

                    MAX(HoTen) AS HoTenDatLich,
                    MAX(SoDienThoai) AS SoDienThoaiGoc,
                    MAX(NgayKham) AS LanKhamGanNhat,
                    COUNT(*) AS SoLuotKham,
                    MIN(Id) AS MaLichHenDauTien

                FROM dbo.LichHen
                WHERE SoDienThoai IS NOT NULL
                GROUP BY
                    REPLACE(
                        REPLACE(
                            REPLACE(
                                REPLACE(SoDienThoai, ' ', ''),
                                '-',
                                ''
                            ),
                            '.',
                            ''
                        ),
                        '+',
                        ''
                    )
            ),

            TaiKhoan AS (
                SELECT
                    Id,
                    HoTen,
                    SoDienThoai,
                    Email,
                    NgaySinh,
                    TrangThai,

                    REPLACE(
                        REPLACE(
                            REPLACE(
                                REPLACE(SoDienThoai, ' ', ''),
                                '-',
                                ''
                            ),
                            '.',
                            ''
                        ),
                        '+',
                        ''
                    ) AS SoDienThoaiKey

                FROM dbo.TaiKhoanNguoiDung
            )

            SELECT
                tk.Id AS TaiKhoanId,
                COALESCE(tk.HoTen, lh.HoTenDatLich) AS HoTen,
                COALESCE(tk.SoDienThoai, lh.SoDienThoaiGoc)
                    AS SoDienThoai,
                tk.Email,
                tk.NgaySinh,
                tk.TrangThai,
                lh.LanKhamGanNhat,
                ISNULL(lh.SoLuotKham, 0) AS SoLuotKham,
                lh.MaLichHenDauTien

            FROM TaiKhoan AS tk

            FULL OUTER JOIN LichHenTongHop AS lh
                ON tk.SoDienThoaiKey = lh.SoDienThoaiKey

            ORDER BY HoTen
        """)

        rows = cursor.fetchall()
        data = []

        for row in rows:
            tuoi = None

            if row.NgaySinh:
                today = date.today()
                tuoi = today.year - row.NgaySinh.year

                if (
                    (today.month, today.day)
                    < (row.NgaySinh.month, row.NgaySinh.day)
                ):
                    tuoi -= 1

            # Bệnh nhân có tài khoản dùng mã theo ID tài khoản.
            # Người chỉ đặt lịch dùng mã theo lịch hẹn đầu tiên.
            if row.TaiKhoanId is not None:
                ma_benh_nhan = f"BN-{row.TaiKhoanId:05d}"
            else:
                ma_benh_nhan = (
                    f"BN-LH-{row.MaLichHenDauTien:06d}"
                )

            if row.TaiKhoanId is None:
                trang_thai = "Đang hoạt động"
            elif row.TrangThai == "Hoạt động":
                trang_thai = "Đang hoạt động"
            else:
                trang_thai = "Đã khóa"

            data.append({
                "id": row.TaiKhoanId,
                "ma_benh_nhan": ma_benh_nhan,
                "ho_ten": row.HoTen or "",
                "so_dien_thoai": row.SoDienThoai or "",
                "email": row.Email or "",
                "ngay_sinh": format_date(row.NgaySinh),
                "tuoi": tuoi,
                "lan_kham_gan_nhat": format_date(
                    row.LanKhamGanNhat
                ),
                "so_luot_kham": row.SoLuotKham or 0,
                "trang_thai": trang_thai
            })

        cursor.close()

        return jsonify({
            "status": "success",
            "count": len(data),
            "data": data
        })

    except Exception:
        logging.exception("Loi lay danh sach benh nhan")

        return error_response(
            "Khong the lay danh sach benh nhan.",
            500
        )

    finally:
        if conn:
            conn.close()

# ==================================================
# 17. CHAY BACKEND
# ==================================================

if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )
