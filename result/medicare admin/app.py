
import os
import re
import pyodbc

from flask import (
    Flask, render_template, request, redirect,
    url_for, session, jsonify, flash
)
from flask_cors import CORS
from dotenv import load_dotenv
from functools import wraps
from datetime import date, datetime, time, timedelta
from werkzeug.security import check_password_hash, generate_password_hash

def build_schedule_slots(shifts, appointments, slot_minutes=30):
    """
    Chia ca làm việc thành các ô thời gian 30 phút.
    appointments là danh sách lịch hẹn đọc từ SQL Server.
    """
    slots = []

    for shift in shifts:
        start = datetime.strptime(shift["start"], "%H:%M")
        end = datetime.strptime(shift["end"], "%H:%M")

        current = start

        while current + timedelta(minutes=slot_minutes) <= end:
            slot_end = current + timedelta(minutes=slot_minutes)
            start_text = current.strftime("%H:%M")
            end_text = slot_end.strftime("%H:%M")

            # Chỉ lấy lịch hẹn của đúng bác sĩ, đúng ngày,
            # và giờ khám nằm trong ô hiện tại.
            booked_appointments = [
                appointment
                for appointment in appointments
                if appointment["doctor_id"] == shift["doctor_id"]
                and appointment["date_iso"] == shift["date_iso"]
                and appointment["time"] >= start_text
                and appointment["time"] < end_text
                and appointment["status"] != "Đã hủy"
            ]

            if not shift["status"]:
                status = "off"
                label = "Ca đã tắt"
            elif len(booked_appointments) >= 1:
                status = "booked"
                label = "Đã có lịch hẹn"
            else:
                status = "available"
                label = "Còn trống"

            slots.append({
                "shift_id": shift["id"],
                "doctor_id": shift["doctor_id"],
                "date_iso": shift["date_iso"],
                "day": shift["day"],
                "start": start_text,
                "end": end_text,
                "label": label,
                "status": status,
                "booked": len(booked_appointments),
                "appointments": booked_appointments,
                "note": shift["note"]
            })

            current = slot_end

    return slots


load_dotenv()

# =====================================================
# 1. CAU HINH SQL SERVER
# =====================================================

SQL_SERVER = os.getenv("SQL_SERVER", r"LAPTOP-6A5KNTQH\SQLEXPRESS")
SQL_DATABASE = os.getenv("SQL_DATABASE", "MediCare")
SQL_DRIVER = os.getenv("SQL_DRIVER", "ODBC Driver 18 for SQL Server")

app = Flask(__name__)
app.config["SESSION_COOKIE_NAME"] = "medicare_admin_session"
app.secret_key = os.getenv(
    "MEDICARE_SECRET_KEY",
    "change-this-secret-key-before-deployment"
)

CORS(
    app,
    resources={
        r"/api/*": {
            "origins": ["http://127.0.0.1:5500"]
        }
    }
)

ADMIN_USERNAME = os.getenv("MEDICARE_ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("MEDICARE_ADMIN_PASSWORD", "Admin@12345")
ADMIN_PASSWORD_HASH = generate_password_hash(ADMIN_PASSWORD)


def get_db_connection():
    connection_string = (
        f"DRIVER={{{SQL_DRIVER}}};"
        f"SERVER={SQL_SERVER};"
        f"DATABASE={SQL_DATABASE};"
        "Trusted_Connection=yes;"
        "TrustServerCertificate=yes;"
    )
    return pyodbc.connect(connection_string)

def get_pending_appointments_count():
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT COUNT(*)
            FROM dbo.LichHen
            WHERE TrangThai = N'Chờ xác nhận'
               OR TrangThai IS NULL
        """)
        return cursor.fetchone()[0]
    finally:
        conn.close()


@app.context_processor
def inject_pending_count():
    try:
        return {"pending_count": get_pending_appointments_count()}
    except Exception:
        app.logger.exception("Lỗi đếm lịch hẹn chờ xác nhận")
        return {"pending_count": None}


# =====================================================
# 2. CAC HAM DUNG CHUNG
# =====================================================

def admin_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if not session.get("admin_logged_in"):
            return redirect(url_for("login", next=request.path))
        return view(*args, **kwargs)
    return wrapped_view


def get_doctor_specialty(doctor_name):
    """Tra cứu chuyên khoa trực tiếp từ SQL Server."""
    name = (doctor_name or "").strip()

    if not name:
        return "Chưa phân loại"

    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT TOP 1 ck.TenChuyenKhoa
            FROM dbo.BacSi AS bs
            INNER JOIN dbo.ChuyenKhoa AS ck
                ON bs.ChuyenKhoaId = ck.Id
            WHERE LTRIM(RTRIM(bs.HoTen)) = ?
            ORDER BY bs.Id
        """, (name,))

        row = cursor.fetchone()
        return row.TenChuyenKhoa if row else "Chưa phân loại"
    finally:
        conn.close()



# =====================================================
# 2. DANH SACH CHUYEN KHOA VA BAC SI
# =====================================================

def get_specialties_from_db():
    """Lấy danh sách chuyên khoa từ SQL Server."""
    conn = get_db_connection()

    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT Id, TenChuyenKhoa
            FROM dbo.ChuyenKhoa
            ORDER BY TenChuyenKhoa
        """)

        return [
            {
                "id": row.Id,
                "name": row.TenChuyenKhoa
            }
            for row in cursor.fetchall()
        ]

    finally:
        conn.close()


def get_doctors_from_db():
    """Lấy danh sách bác sĩ và hồ sơ từ SQL Server."""
    conn = get_db_connection()

    try:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                bs.Id,
                bs.HoTen,
                bs.ChuyenKhoaId,
                ck.TenChuyenKhoa,
                bs.PhongKham,
                bs.TrangThai,
                hs.HocVi,
                hs.KinhNghiem,
                hs.SoDienThoai,
                hs.Email,
                CASE ck.TenChuyenKhoa
                    WHEN N'Nội khoa' THEN 250000
                    WHEN N'Ngoại khoa' THEN 250000
                    WHEN N'Nhi khoa' THEN 250000
                    WHEN N'Tim mạch' THEN 350000
                    WHEN N'Da liễu' THEN 200000
                    WHEN N'Tai - Mũi - Họng' THEN 250000
                    ELSE 0
                END AS PhiKham,
                (
                    SELECT COUNT(*)
                    FROM dbo.LichHen AS lh
                    WHERE lh.BacSiId = bs.Id
                      AND lh.NgayKham = CAST(GETDATE() AS DATE)
                      AND (
                          lh.TrangThai IS NULL
                          OR lh.TrangThai <> N'Đã hủy'
                      )
                ) AS LichHenHomNay
            FROM dbo.BacSi AS bs
            INNER JOIN dbo.ChuyenKhoa AS ck
                ON bs.ChuyenKhoaId = ck.Id
            LEFT JOIN dbo.HoSoBacSi AS hs
                ON bs.Id = hs.BacSiId
            ORDER BY bs.Id ASC
        """)

        doctors = []

        for row in cursor.fetchall():
            doctors.append({
                "id": row.Id,
                "code": f"BS-{row.Id:03d}",
                "name": row.HoTen or "",
                "title": row.HocVi or "Bác sĩ",
                "specialty": row.TenChuyenKhoa,
                "specialty_id": row.ChuyenKhoaId,
                "experience": row.KinhNghiem or "",
                "status": (
                    "Đang làm việc"
                    if row.TrangThai
                    else "Tạm ngưng"
                ),
                "email": row.Email or "",
                "phone": row.SoDienThoai or "",
                "fee": row.PhiKham or 0,
                "fee_display": f"{(row.PhiKham or 0):,}đ".replace(",", "."),
                "room": row.PhongKham or "",
                "today_booked": row.LichHenHomNay or 0
            })

        return doctors

    finally:
        conn.close()


def get_doctor_profile_from_db(doctor_id):
    """Lấy hồ sơ chi tiết bác sĩ từ SQL Server."""
    conn = get_db_connection()

    try:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                bs.Id,
                bs.HoTen,
                bs.ChuyenKhoaId,
                ck.TenChuyenKhoa,
                bs.PhongKham,
                bs.TrangThai,
                hs.HocVi,
                hs.BangCap,
                hs.KinhNghiem,
                hs.DaoTao,
                hs.ChuyenMon,
                hs.NoiCongTac,
                hs.SoDienThoai,
                hs.Email,
                hs.GioiThieu,
                CASE ck.TenChuyenKhoa
                    WHEN N'Nội khoa' THEN 250000
                    WHEN N'Ngoại khoa' THEN 250000
                    WHEN N'Nhi khoa' THEN 250000
                    WHEN N'Tim mạch' THEN 350000
                    WHEN N'Da liễu' THEN 200000
                    WHEN N'Tai - Mũi - Họng' THEN 250000
                    ELSE 0
                END AS PhiKham
            FROM dbo.BacSi AS bs
            INNER JOIN dbo.ChuyenKhoa AS ck
                ON bs.ChuyenKhoaId = ck.Id
            LEFT JOIN dbo.HoSoBacSi AS hs
                ON bs.Id = hs.BacSiId
            WHERE bs.Id = ?
        """, (doctor_id,))

        row = cursor.fetchone()

        if row is None:
            return None

        fee = row.PhiKham or 0

        return {
            "id": row.Id,
            "code": f"BS-{row.Id:03d}",
            "name": row.HoTen or "",
            "title": row.HocVi or "Bác sĩ",
            "specialty": row.TenChuyenKhoa or "",
            "specialty_id": row.ChuyenKhoaId,
            "room": row.PhongKham or "",
            "status": (
                "Đang làm việc"
                if row.TrangThai
                else "Tạm ngưng"
            ),
            "email": row.Email or "",
            "phone": row.SoDienThoai or "",
            "experience": row.KinhNghiem or "",
            "education": row.BangCap or "",
            "training": row.DaoTao or "",
            "degree": row.HocVi or "",
            "focus": row.ChuyenMon or "",
            "workplace": row.NoiCongTac or "",
            "fee": fee,
            "fee_display": f"{fee:,}đ".replace(",", "."),
            "intro": row.GioiThieu or ""
        }

    finally:
        conn.close()

# =====================================================
# 3. DOC LICH HEN TU SQL SERVER
# =====================================================

def get_appointments_from_db():
    # Dung chinh ma benh nhan cua API /api/patients de hai trang trung nhau.
    # Ma LH-xxxxxx la ID lich hen, KHONG phai ma benh nhan.
    def phone_key(phone):
        return (str(phone or "")
                .replace(" ", "").replace("-", "")
                .replace(".", "").replace("+", ""))

    patient_code_by_phone = {}
    try:
        for patient in get_patients_from_db():
            key = phone_key(patient.get("phone"))
            if key:
                patient_code_by_phone[key] = patient.get("id", "—")
    except Exception:
        # Khong lam hong trang lich hen neu bang benh nhan dang gap loi.
        app.logger.exception("Khong doc duoc ma benh nhan cho danh sach lich hen")

    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT
                lh.Id,
                lh.HoTen,
                lh.SoDienThoai,
                lh.BacSi,
                lh.BacSiId,
                lh.NgayKham,
                lh.GioKham,
                lh.LyDo,
                lh.TrangThai,
                ck.TenChuyenKhoa
            FROM dbo.LichHen AS lh
            LEFT JOIN dbo.BacSi AS bs
                ON lh.BacSiId = bs.Id
            LEFT JOIN dbo.ChuyenKhoa AS ck
                ON bs.ChuyenKhoaId = ck.Id
            ORDER BY lh.Id DESC
        """)

        result = []
        for row in cursor.fetchall():
            appointment_date = row.NgayKham
            doctor_name = (
                row.BacSi or ""
            ).strip()

            if row.BacSiId and row.BacSiId:
                # Ưu tiên tên bác sĩ trong bảng BacSi nếu có liên kết ID.
                if row.BacSi:
                    doctor_name = row.BacSi

            result.append({
                "id": row.Id,
                "code": f"LH-{row.Id:06d}",
                "patient": row.HoTen or "",
                "patient_code": patient_code_by_phone.get(
                    phone_key(row.SoDienThoai), "—"
                ),
                "phone": row.SoDienThoai or "",
                "time": str(row.GioKham)[:5] if row.GioKham else "",
                "doctor": doctor_name,
                "specialty": (
                    row.TenChuyenKhoa
                    or get_doctor_specialty(doctor_name)
                ),
                "date": (
                    appointment_date.strftime("%d/%m/%Y")
                    if appointment_date else ""
                ),
                "reason": row.LyDo or "",
                "status": row.TrangThai or "Chờ xác nhận"
            })

        return result
    finally:
        conn.close()


def get_schedule_appointments_from_db(doctor_id, selected_date):
    """Lấy lịch hẹn của bác sĩ trong ngày được chọn."""
    conn = get_db_connection()

    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT
                lh.Id,
                lh.BacSiId,
                lh.HoTen,
                lh.SoDienThoai,
                lh.NgayKham,
                lh.GioKham,
                lh.TrangThai,
                lh.LyDo
            FROM dbo.LichHen AS lh
            WHERE lh.BacSiId = ?
              AND lh.NgayKham = ?
              AND (
                  lh.TrangThai IS NULL
                  OR lh.TrangThai <> N'Đã hủy'
              )
            ORDER BY lh.GioKham
        """, (doctor_id, selected_date))

        appointments = []

        for row in cursor.fetchall():
            appointments.append({
                "id": row.Id,
                "doctor_id": row.BacSiId,
                "patient": row.HoTen or "Chưa có tên",
                "phone": row.SoDienThoai or "",
                "date_iso": (
                    row.NgayKham.strftime("%Y-%m-%d")
                    if row.NgayKham else ""
                ),
                "time": str(row.GioKham)[:5] if row.GioKham else "",
                "status": row.TrangThai or "Chờ xác nhận",
                "reason": row.LyDo or ""
            })

        return appointments

    finally:
        conn.close()

def update_appointment_status(code, status):
    if not code or not code.startswith("LH-"):
        return False

    try:
        appointment_id = int(code[3:])
    except (ValueError, TypeError):
        return False

    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE dbo.LichHen
            SET TrangThai = ?
            WHERE Id = ?
        """, (status, appointment_id))

        updated = cursor.rowcount > 0
        conn.commit()
        return updated
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


# =====================================================
# 4. DOC LICH LAM VIEC TU SQL SERVER
# =====================================================

def get_work_shifts_from_db(doctor_id):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT
                llv.Id,
                llv.BacSiId,
                llv.NgayLamViec,
                llv.GioBatDau,
                llv.GioKetThuc,
                llv.SoLuongToiDa,
                llv.GhiChu,
                llv.TrangThai,
                (
                    SELECT COUNT(*)
                    FROM dbo.LichHen AS lh
                    WHERE lh.BacSiId = llv.BacSiId
                      AND lh.NgayKham = llv.NgayLamViec
                      AND lh.GioKham >=
                          CONVERT(VARCHAR(5), llv.GioBatDau, 108)
                      AND lh.GioKham <
                          CONVERT(VARCHAR(5), llv.GioKetThuc, 108)
                      AND (
                        lh.TrangThai IS NULL
                        OR lh.TrangThai <> N'Đã hủy'
                    )
                ) AS SoLichHen
            FROM dbo.LichLamViec AS llv
            WHERE llv.BacSiId = ?
            ORDER BY llv.NgayLamViec, llv.GioBatDau
        """, (doctor_id,))

        shifts = []
        weekday_names = [
            "Thứ Hai", "Thứ Ba", "Thứ Tư",
            "Thứ Năm", "Thứ Sáu", "Thứ Bảy",
            "Chủ Nhật"
        ]

        for row in cursor.fetchall():
            work_date = row.NgayLamViec
            start_time = str(row.GioBatDau)[:5]
            end_time = str(row.GioKetThuc)[:5]

            shifts.append({
                "id": row.Id,
                "doctor_id": row.BacSiId,
                "day": weekday_names[work_date.weekday()],
                "date": work_date.strftime("%d/%m/%Y"),
                "date_iso": work_date.strftime("%Y-%m-%d"),
                "start": start_time,
                "end": end_time,
                "morning": f"{start_time} – {end_time}",
                "afternoon": "",
                "morning_booked": row.SoLichHen or 0,
                "morning_capacity": row.SoLuongToiDa,
                "afternoon_booked": 0,
                "afternoon_capacity": 0,
                "booked": row.SoLichHen or 0,
                "capacity": row.SoLuongToiDa,
                "note": row.GhiChu or "",
                "status": bool(row.TrangThai)
            })

        return shifts
    finally:
        conn.close()


def create_work_shift(doctor_id, work_date, start_time,
                      end_time, capacity, note):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT Id
            FROM dbo.BacSi
            WHERE Id = ?
        """, (doctor_id,))

        if cursor.fetchone() is None:
            raise ValueError("Không tìm thấy bác sĩ.")

        cursor.execute("""
            INSERT INTO dbo.LichLamViec
                (BacSiId, NgayLamViec, GioBatDau, GioKetThuc,
                 SoLuongToiDa, GhiChu, TrangThai, NgayTao)
            VALUES (?, ?, ?, ?, ?, ?, 1, SYSDATETIME())
        """, (
            doctor_id, work_date, start_time,
            end_time, capacity, note or None
        ))

        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


# =====================================================
# 5. DANG NHAP / DANG XUAT
# =====================================================

@app.route("/login", methods=["GET", "POST"])
def login():
    if session.get("admin_logged_in"):
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if (
            username == ADMIN_USERNAME
            and check_password_hash(ADMIN_PASSWORD_HASH, password)
        ):
            session.clear()
            session["admin_logged_in"] = True
            session["admin_username"] = username

            next_url = request.args.get("next", "")
            if next_url.startswith("/") and not next_url.startswith("//"):
                return redirect(next_url)

            return redirect(url_for("dashboard"))

        flash(
            "Tên đăng nhập hoặc mật khẩu chưa đúng. Vui lòng thử lại.",
            "error"
        )

    return render_template("login.html")


@app.post("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


# =====================================================
# 6. DASHBOARD
# =====================================================

@app.route("/")
@admin_required
def dashboard():
    try:
        appointment_list = get_appointments_from_db()
        db_error = None
    except Exception:
        app.logger.exception("Không đọc được lịch hẹn")
        appointment_list = []
        db_error = "Không thể tải lịch hẹn từ cơ sở dữ liệu."

    return render_template(
        "dashboard.html",
        appointments=appointment_list,
        today=date.today().strftime("%d/%m/%Y"),
        admin_username=session.get("admin_username", "admin"),
        db_error=db_error,
        active_page="dashboard"
    )


# =====================================================
# 7. API XAC NHAN / HUY LICH HEN
# =====================================================

@app.post("/api/appointments/<code>/confirm")
@admin_required
def confirm_appointment(code):
    try:
        updated = update_appointment_status(code, "Đã xác nhận")
        if not updated:
            return jsonify({
                "success": False,
                "message": "Không tìm thấy lịch hẹn."
            }), 404

        return jsonify({
            "success": True,
            "status": "Đã xác nhận",
            "message": "Đã xác nhận lịch hẹn thành công."
        })
    except Exception:
        app.logger.exception("Lỗi xác nhận lịch hẹn")
        return jsonify({
            "success": False,
            "message": "Không thể cập nhật lịch hẹn."
        }), 500


@app.post("/api/appointments/<code>/cancel")
@admin_required
def cancel_appointment(code):
    try:
        updated = update_appointment_status(code, "Đã hủy")
        if not updated:
            return jsonify({
                "success": False,
                "message": "Không tìm thấy lịch hẹn."
            }), 404

        return jsonify({
            "success": True,
            "status": "Đã hủy",
            "message": "Đã hủy lịch hẹn thành công."
        })
    except Exception:
        app.logger.exception("Lỗi hủy lịch hẹn")
        return jsonify({
            "success": False,
            "message": "Không thể cập nhật lịch hẹn."
        }), 500


# =====================================================
# 8. TRANG QUAN LY LICH HEN
# =====================================================

@app.get("/api/appointments/form-options")
@admin_required
def appointment_form_options():
    try:
        doctors = get_doctors_from_db()
        specialties = get_specialties_from_db()
        return jsonify({"success": True, "doctors": doctors, "specialties": specialties})
    except Exception:
        app.logger.exception("Lỗi lấy danh sách bác sĩ cho form đặt lịch")
        return jsonify({"success": False, "message": "Không thể tải bác sĩ/chuyên khoa từ SQL Server."}), 500


APPOINTMENT_MINUTES = 30


def available_appointment_slots(cursor, doctor_id, exam_date):
    """Khung 30 phút thuộc ca đang bật, không đè lên lịch chưa hủy."""
    cursor.execute("""
        SELECT GioBatDau, GioKetThuc, SoLuongToiDa
        FROM dbo.LichLamViec
        WHERE BacSiId = ? AND NgayLamViec = ? AND TrangThai = 1
        ORDER BY GioBatDau
    """, (doctor_id, exam_date))
    shifts = cursor.fetchall()
    cursor.execute("""
        SELECT GioKham FROM dbo.LichHen
        WHERE BacSiId = ? AND NgayKham = ?
          AND (TrangThai IS NULL OR TrangThai <> N'Đã hủy')
    """, (doctor_id, exam_date))
    booked = []
    for row in cursor.fetchall():
        raw = str(row.GioKham)[:5]
        try:
            booked.append(datetime.combine(exam_date, time.fromisoformat(raw)))
        except ValueError:
            continue

    slots = {}
    now = datetime.now()
    duration = timedelta(minutes=APPOINTMENT_MINUTES)
    for shift in shifts:
        begin = datetime.combine(exam_date, time.fromisoformat(str(shift.GioBatDau)[:8]))
        end = datetime.combine(exam_date, time.fromisoformat(str(shift.GioKetThuc)[:8]))
        current = begin
        while current + duration <= end:
            if current >= now:
                overlap = any(current < b + duration and b < current + duration for b in booked)
                key = current.strftime('%H:%M')
                # Bất kỳ ca hợp lệ nào còn chỗ thì slot được chọn.
                slots[key] = slots.get(key, False) or not overlap
            current += duration
    return [{"time": key, "end": (datetime.combine(exam_date, time.fromisoformat(key)) + duration).strftime('%H:%M'),
             "available": slots[key]} for key in sorted(slots)]


@app.get("/api/appointments/available-slots")
@admin_required
def appointment_available_slots():
    try:
        doctor_id = int(request.args.get('doctor_id', ''))
        exam_date = date.fromisoformat(request.args.get('date', ''))
    except (ValueError, TypeError):
        return jsonify({"success": False, "message": "Bác sĩ hoặc ngày khám không hợp lệ."}), 400
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT Id FROM dbo.BacSi WHERE Id = ? AND TrangThai = 1", (doctor_id,))
        if not cursor.fetchone():
            return jsonify({"success": False, "message": "Bác sĩ không hoạt động."}), 400
        return jsonify({"success": True, "duration_minutes": APPOINTMENT_MINUTES,
                        "slots": available_appointment_slots(cursor, doctor_id, exam_date)})
    except Exception:
        app.logger.exception('Lỗi tải giờ khám trống')
        return jsonify({"success": False, "message": "Không thể tải giờ trống từ SQL Server."}), 500
    finally:
        if conn:
            conn.close()


@app.post("/api/appointments")
@admin_required
def create_counter_appointment():
    """Đặt lịch tại quầy; ghi cùng bảng LichHen với lịch online."""
    data = request.get_json(silent=True) or {}
    patient = str(data.get("patient", "")).strip()
    phone = str(data.get("phone", "")).strip()
    reason = str(data.get("reason", "")).strip()
    try:
        doctor_id = int(data.get("doctor_id"))
        exam_date = date.fromisoformat(str(data.get("date", "")))
        exam_time = time.fromisoformat(str(data.get("time", "")))
    except (ValueError, TypeError):
        return jsonify({"success": False, "message": "Bác sĩ, ngày hoặc giờ khám không hợp lệ."}), 400
    if not patient or not phone:
        return jsonify({"success": False, "message": "Cần nhập họ tên và số điện thoại."}), 400
    if len(patient) > 150 or len(phone) > 30 or len(reason) > 1000:
        return jsonify({"success": False, "message": "Thông tin nhập quá dài."}), 400
    if datetime.combine(exam_date, exam_time) < datetime.now():
        return jsonify({"success": False, "message": "Không thể đặt lịch ở thời điểm đã qua."}), 400

    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT HoTen, ChuyenKhoaId FROM dbo.BacSi WHERE Id = ? AND TrangThai = 1", (doctor_id,))
        doctor = cursor.fetchone()
        if doctor is None:
            return jsonify({"success": False, "message": "Bác sĩ không tồn tại hoặc đã ngừng hoạt động."}), 400

        # Khóa theo bác sĩ + ngày để hai lượt đặt cùng lúc không vượt qua kiểm tra.
        lock_name = f"MediCare:booking:{doctor_id}:{exam_date.isoformat()}"
        cursor.execute("""
            SET NOCOUNT ON;
            DECLARE @result int;
            EXEC @result = sp_getapplock @Resource=?, @LockMode='Exclusive',
                @LockOwner='Transaction', @LockTimeout=10000;
            SELECT @result;
        """, (lock_name,))
        if cursor.fetchone()[0] < 0:
            conn.rollback()
            return jsonify({"success": False, "message": "Hệ thống đang xử lý lịch của bác sĩ. Vui lòng thử lại."}), 409

        slot_key = exam_time.strftime('%H:%M')
        slots = available_appointment_slots(cursor, doctor_id, exam_date)
        chosen = next((slot for slot in slots if slot['time'] == slot_key), None)
        if chosen is None:
            conn.rollback()
            return jsonify({"success": False, "message": "Giờ khám phải thuộc ca làm việc đang bật và đủ 30 phút. Hãy chọn giờ khác."}), 409
        if not chosen['available']:
            conn.rollback()
            return jsonify({"success": False, "message": "Khung giờ này đã có lịch khám. Hãy chọn giờ còn trống."}), 409

        # Các cột này đều đang được backend Admin sử dụng để đọc lịch.
        cursor.execute("""
            INSERT INTO dbo.LichHen
                (HoTen, SoDienThoai, BacSi, BacSiId, NgayKham, GioKham, LyDo, TrangThai)
            OUTPUT INSERTED.Id
            VALUES (?, ?, ?, ?, ?, ?, ?, N'Đã xác nhận')
        """, (patient, phone, doctor.HoTen, doctor_id, exam_date, exam_time, reason or None))
        new_id = cursor.fetchone()[0]
        conn.commit()
        return jsonify({"success": True, "code": f"LH-{new_id:06d}",
                        "message": "Đã lưu lịch hẹn tại quầy vào SQL Server."}), 201
    except Exception:
        if conn:
            conn.rollback()
        app.logger.exception("Lỗi tạo lịch hẹn tại quầy")
        return jsonify({"success": False, "message": "Không thể lưu lịch. Kiểm tra cấu trúc bảng LichHen và nhật ký Flask."}), 500
    finally:
        if conn:
            conn.close()


@app.route("/appointments")
@admin_required
def appointments_page():
    try:
        appointment_list = get_appointments_from_db()
        db_error = None
    except Exception:
        app.logger.exception("Không đọc được lịch hẹn")
        appointment_list = []
        db_error = "Không thể tải lịch hẹn từ cơ sở dữ liệu."

    return render_template(
        "appointments.html",
        appointments=appointment_list,
        today=date.today().strftime("%d/%m/%Y"),
        admin_username=session.get("admin_username", "admin"),
        db_error=db_error,
        active_page="appointments"
    )


@app.route("/doctors", methods=["GET", "POST"])
@admin_required
def doctors_page():

    # -----------------------------
    # THEM BAC SI
    # -----------------------------
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        specialty_id = request.form.get("specialty_id", "").strip()
        room = request.form.get("room", "").strip()

        if not name or not specialty_id:
            flash(
                "Vui lòng nhập tên bác sĩ và chọn chuyên khoa.",
                "error"
            )
            return redirect(url_for("doctors_page"))

        conn = None

        try:
            specialty_id = int(specialty_id)
            conn = get_db_connection()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT Id
                FROM dbo.ChuyenKhoa
                WHERE Id = ?
            """, (specialty_id,))

            if cursor.fetchone() is None:
                flash("Chuyên khoa không tồn tại.", "error")
                return redirect(url_for("doctors_page"))

            cursor.execute("""
                INSERT INTO dbo.BacSi
                    (HoTen, ChuyenKhoaId, PhongKham, TrangThai, NgayTao)
                OUTPUT INSERTED.Id
                VALUES (?, ?, ?, 1, SYSDATETIME())
            """, (name, specialty_id, room or None))

            new_doctor_id = cursor.fetchone()[0]

            cursor.execute("""
                INSERT INTO dbo.HoSoBacSi (
                    BacSiId,
                    PhiKham
                )
                SELECT
                    ?,
                    CASE ck.TenChuyenKhoa
                        WHEN N'Nội khoa' THEN 250000
                        WHEN N'Ngoại khoa' THEN 250000
                        WHEN N'Nhi khoa' THEN 250000
                        WHEN N'Tim mạch' THEN 350000
                        WHEN N'Da liễu' THEN 200000
                        WHEN N'Tai - Mũi - Họng' THEN 250000
                        ELSE 0
                    END
                FROM dbo.ChuyenKhoa AS ck
                WHERE ck.Id = ?
            """, (new_doctor_id, specialty_id))

            conn.commit()
            flash("Đã thêm bác sĩ thành công.", "success")

        except ValueError:
            flash("Chuyên khoa không hợp lệ.", "error")

        except Exception:
            if conn:
                conn.rollback()

            app.logger.exception("Lỗi thêm bác sĩ")
            flash(
                "Không thể thêm bác sĩ vào SQL Server.",
                "error"
            )

        finally:
            if conn:
                conn.close()

        return redirect(url_for("doctors_page"))

    # -----------------------------
    # DOC DU LIEU VA PHAN TRANG
    # -----------------------------
    try:
        # Lấy danh sách bác sĩ và chuyên khoa từ SQL Server
        all_doctors = get_doctors_from_db()
        specialty_options = get_specialties_from_db()


        # Lấy điều kiện tìm kiếm từ URL
        keyword = request.args.get("keyword", "").strip()
        selected_specialty = request.args.get("specialty", "").strip()
        selected_status = request.args.get("status", "").strip()

        # Lọc danh sách trước khi phân trang
        filtered_doctors = all_doctors

        if keyword:
            keyword_lower = keyword.casefold()

            filtered_doctors = [
                d for d in filtered_doctors
                if keyword_lower in d["name"].casefold()
                or keyword_lower in d["code"].casefold()
                or keyword_lower in d["room"].casefold()
            ]

        if selected_specialty:
            filtered_doctors = [
                d for d in filtered_doctors
                if d["specialty"] == selected_specialty
            ]

        if selected_status:
            filtered_doctors = [
                d for d in filtered_doctors
                if d["status"] == selected_status
            ]

        # Thống kê toàn bộ bác sĩ, không chỉ trang đang xem
        total_doctors = len(all_doctors)

        active_doctors = sum(
            1 for d in all_doctors
            if d["status"] == "Đang làm việc"
        )

        off_shift_doctors = sum(
            1 for d in all_doctors
            if d["status"] == "Ngoài ca"
        )

        suspended_doctors = sum(
            1 for d in all_doctors
            if d["status"] == "Tạm ngưng"
        )

        # Mỗi trang hiển thị tối đa 6 bác sĩ
        per_page = 6
        filtered_total = len(filtered_doctors)

        total_pages = max(
            1,
            (filtered_total + per_page - 1) // per_page
        )

        try:
            page = int(request.args.get("page", 1))
        except (ValueError, TypeError):
            page = 1

        # Đảm bảo số trang hợp lệ
        page = max(1, min(page, total_pages))

        # Lấy đúng 6 bác sĩ của trang hiện tại
        start_index = (page - 1) * per_page
        end_index = start_index + per_page

        doctors = filtered_doctors[start_index:end_index]

        db_error = None

    except Exception:
        app.logger.exception("Lỗi tải danh sách bác sĩ")

        doctors = []
        specialty_options = []
        keyword = request.args.get("keyword", "").strip()
        selected_specialty = request.args.get("specialty", "").strip()
        selected_status = request.args.get("status", "").strip()

        total_doctors = 0
        active_doctors = 0
        off_shift_doctors = 0
        suspended_doctors = 0
        filtered_total = 0
        page = 1
        total_pages = 1

        db_error = "Không thể tải dữ liệu bác sĩ từ SQL Server."

    # Truyền dữ liệu sang doctors.html
    return render_template(
        "doctors.html",
        doctors=doctors,
        specialties=[
            s["name"] for s in specialty_options
        ],
        specialty_options=specialty_options,

        total_doctors=total_doctors,
        active_doctors=active_doctors,
        off_shift_doctors=off_shift_doctors,
        suspended_doctors=suspended_doctors,

        filtered_total=filtered_total,
        page=page,
        total_pages=total_pages,
        keyword=keyword,
        selected_specialty=selected_specialty,
        selected_status=selected_status,

        today=date.today().strftime("%d/%m/%Y"),
        admin_username=session.get("admin_username", "admin"),
        active_page="doctors",
        db_error=db_error
    )

@app.route("/api/doctors/<int:doctor_id>/profile", methods=["GET"])
@admin_required
def doctor_profile_api(doctor_id):
    try:
        # 1. Lấy thông tin hồ sơ bác sĩ
        profile = get_doctor_profile_from_db(doctor_id)

        if profile is None:
            return jsonify({
                "success": False,
                "message": "Không tìm thấy bác sĩ."
            }), 404

        # Ngày hiện tại trên máy chủ Flask
        today = date.today()

        # 2. Lấy lịch hẹn của bác sĩ trong hôm nay
        appointments = get_schedule_appointments_from_db(
            doctor_id,
            today
        )

        profile["today_appointments"] = [
            {
                "id": item["id"],
                "time": item["time"],
                "patient_name": item["patient"],
                "phone": item["phone"],
                "reason": item["reason"],
                "status": item["status"]
            }
            for item in appointments
        ]

        # 3. Lấy lịch làm việc và chỉ giữ các ca hôm nay
        all_shifts = get_work_shifts_from_db(doctor_id)

        today_iso = today.isoformat()

        today_shifts = [
            shift for shift in all_shifts
            if shift["date_iso"] == today_iso
        ]

        profile["today_shifts"] = [
            {
                "id": shift["id"],
                "start": shift["start"],
                "end": shift["end"],
                "status": (
                    "Đang hoạt động"
                    if shift["status"]
                    else "Đã tắt"
                ),
                "note": shift.get("note", "")
            }
            for shift in today_shifts
        ]

        # Trả dữ liệu cho giao diện
        return jsonify({
            "success": True,
            "doctor": profile
        })

    except Exception:
        app.logger.exception("Lỗi API hồ sơ bác sĩ")

        return jsonify({
            "success": False,
            "message": "Không thể tải thông tin hồ sơ bác sĩ."
        }), 500



# =====================================================
# 10. QUAN LY LICH LAM VIEC
# =====================================================

@app.route("/schedule", methods=["GET", "POST"])
@admin_required
def schedule_page():
    if request.method == "POST":
        doctor_id = None

        try:
            doctor_id = int(request.form.get("doctor_id", ""))
            work_date = date.fromisoformat(
                request.form.get("work_date", "")
            )
            start_time = request.form.get("start_time", "").strip()
            end_time = request.form.get("end_time", "").strip()
            capacity = int(request.form.get("capacity", "14"))
            note = request.form.get("note", "").strip()

            if not start_time or not end_time or end_time <= start_time:
                flash("Giờ kết thúc phải sau giờ bắt đầu.", "error")
                return redirect(url_for("schedule_page", doctor=doctor_id))

            if capacity < 1:
                flash("Số lượng lịch tối đa phải lớn hơn 0.", "error")
                return redirect(url_for("schedule_page", doctor=doctor_id))

            create_work_shift(
                doctor_id,
                work_date,
                start_time,
                end_time,
                capacity,
                note
            )

            flash("Đã thêm ca làm việc vào SQL Server.", "success")

        except (ValueError, TypeError):
            flash("Vui lòng kiểm tra lại thông tin ca làm việc.", "error")

        except Exception:
            app.logger.exception("Lỗi thêm ca làm việc")
            flash("Không thể lưu ca làm việc vào SQL Server.", "error")

        return redirect(url_for(
            "schedule_page",
            doctor=doctor_id
        ) if doctor_id else url_for("schedule_page"))


    doctor_list = []
    selected_doctor = None
    shifts = []
    slots = []
    db_error = None

    selected_date_text = request.args.get(
        "date", date.today().isoformat()
    )

    try:
        selected_date = date.fromisoformat(selected_date_text)
    except ValueError:
        selected_date = date.today()

    try:
        doctor_list = get_doctors_from_db()
        doctor_param = request.args.get("doctor", "").strip()

        try:
            selected_id = (
                int(doctor_param)
                if doctor_param
                else (doctor_list[0]["id"] if doctor_list else None)
            )
        except ValueError:
            selected_id = doctor_list[0]["id"] if doctor_list else None

        selected_doctor = next(
            (d for d in doctor_list if d["id"] == selected_id),
            None
        )

        if selected_doctor:
            all_shifts = get_work_shifts_from_db(
                selected_doctor["id"]
            )

            shifts = [
                shift for shift in all_shifts
                if shift["date_iso"] == selected_date.isoformat()
            ]

            appointments = get_schedule_appointments_from_db(
                selected_doctor["id"], selected_date
            )

            slots = build_schedule_slots(
                shifts, appointments, slot_minutes=30
            )

    except Exception:
        app.logger.exception("Lỗi tải thời khóa biểu")
        db_error = (
            "Không thể tải thời khóa biểu từ SQL Server. "
            "Hãy kiểm tra kết nối và cấu trúc bảng."
        )

    total_shifts = len(shifts)
    active_shifts = sum(1 for s in shifts if s["status"])
    inactive_shifts = total_shifts - active_shifts
    total_capacity = sum(s["capacity"] or 0 for s in shifts)
    total_booked = sum(s["booked"] or 0 for s in shifts)

    fill_rate = (
        round(total_booked * 100 / total_capacity)
        if total_capacity > 0 else 0
    )

    return render_template(
        "schedule.html",
        doctors=doctor_list,
        selected_doctor=selected_doctor,
        shifts=shifts,
        slots=slots,
        selected_date=selected_date.isoformat(),
        total_shifts=total_shifts,
        active_shifts=active_shifts,
        inactive_shifts=inactive_shifts,
        total_capacity=total_capacity,
        total_booked=total_booked,
        fill_rate=fill_rate,
        today=date.today().strftime("%d/%m/%Y"),
        today_iso=date.today().isoformat(),
        admin_username=session.get("admin_username", "admin"),
        active_page="schedule",
        db_error=db_error
    )



@app.post("/api/schedule/<int:shift_id>/toggle")
@admin_required
def toggle_work_shift(shift_id):
    conn = None

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE dbo.LichLamViec
            SET TrangThai =
                CASE WHEN TrangThai = 1 THEN 0 ELSE 1 END
            WHERE Id = ?
        """, (shift_id,))

        if cursor.rowcount == 0:
            conn.rollback()
            return jsonify({
                "success": False,
                "message": "Không tìm thấy ca làm việc."
            }), 404

        conn.commit()

        return jsonify({
            "success": True,
            "message": "Đã cập nhật trạng thái ca làm việc."
        })

    except Exception:
        if conn:
            conn.rollback()

        app.logger.exception("Lỗi đổi trạng thái ca làm việc")

        return jsonify({
            "success": False,
            "message": "Không thể cập nhật trạng thái ca."
        }), 500

    finally:
        if conn:
            conn.close()


@app.post("/api/schedule/<int:shift_id>/delete")
@admin_required
def delete_work_shift(shift_id):
    conn = None

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Không xóa ca nếu ca đó đã có lịch hẹn chưa bị hủy.
        cursor.execute("""
            SELECT COUNT(*)
            FROM dbo.LichHen AS lh
            INNER JOIN dbo.LichLamViec AS llv
                ON lh.BacSiId = llv.BacSiId
                AND lh.NgayKham = llv.NgayLamViec
                AND CONVERT(TIME, lh.GioKham) >= llv.GioBatDau
                AND CONVERT(TIME, lh.GioKham) < llv.GioKetThuc
            WHERE llv.Id = ?
              AND lh.TrangThai <> N'Đã hủy'
        """, (shift_id,))

        booked_count = cursor.fetchone()[0]

        if booked_count > 0:
            return jsonify({
                "success": False,
                "message": (
                    "Ca đã có lịch hẹn. Hãy xử lý các lịch hẹn "
                    "trước khi xóa ca."
                )
            }), 400

        cursor.execute("""
            DELETE FROM dbo.LichLamViec
            WHERE Id = ?
        """, (shift_id,))

        if cursor.rowcount == 0:
            conn.rollback()
            return jsonify({
                "success": False,
                "message": "Không tìm thấy ca làm việc."
            }), 404

        conn.commit()

        return jsonify({
            "success": True,
            "message": "Đã xóa ca làm việc."
        })

    except Exception:
        if conn:
            conn.rollback()

        app.logger.exception("Lỗi xóa ca làm việc")

        return jsonify({
            "success": False,
            "message": "Không thể xóa ca làm việc."
        }), 500

    finally:
        if conn:
            conn.close()



# =====================================================
# 11. QUAN LY BENH NHAN - DOC TRUC TIEP TU SQL SERVER
# =====================================================

def get_patients_from_db():
    """Tra benh nhan co tai khoan va benh nhan chi dat lich.

    Dung dung truy van tu Backend Patient de hai phia dong bo du lieu.
    """
    conn = get_db_connection()
    try:
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
        results = []
        today = date.today()

        for row in cursor.fetchall():
            age = None
            if row.NgaySinh:
                age = today.year - row.NgaySinh.year
                if (today.month, today.day) < (row.NgaySinh.month, row.NgaySinh.day):
                    age -= 1

            if row.TaiKhoanId is not None:
                code = f"BN-{row.TaiKhoanId:05d}"
            else:
                code = f"BN-LH-{row.MaLichHenDauTien:06d}"

            if row.TaiKhoanId is None or row.TrangThai == "Hoạt động":
                status = "Đang hoạt động"
            else:
                status = "Đã khóa"

            results.append({
                "id": code,
                "name": row.HoTen or "",
                "phone": row.SoDienThoai or "",
                "age": age,
                "dob": row.NgaySinh.strftime("%Y-%m-%d") if row.NgaySinh else "",
                "email": row.Email or "",
                "last_visit": (
                    row.LanKhamGanNhat.strftime("%Y-%m-%d")
                    if row.LanKhamGanNhat else ""
                ),
                "visits": row.SoLuotKham or 0,
                "status": status
            })

        return results
    finally:
        conn.close()


@app.route("/patients", endpoint="patients")
@admin_required
def patients_page():
    # Giao dien nhan du lieu dong tu /api/patients, khong nhung danh sach mau.
    return render_template(
        "patients.html",
        patients=[],
        today_long=date.today().strftime("%A, %d/%m/%Y"),
        today=date.today().strftime("%d/%m/%Y"),
        admin_username=session.get("admin_username", "admin"),
        active_page="patients"
    )


@app.get("/api/patients")
@admin_required
def patients_api():
    try:
        patients = get_patients_from_db()
        return jsonify({
            "success": True,
            "count": len(patients),
            "patients": patients
        })
    except Exception:
        app.logger.exception("Loi doc danh sach benh nhan tu SQL Server")
        return jsonify({
            "success": False,
            "message": "Khong the tai benh nhan tu SQL Server."
        }), 500


@app.post("/api/patients")
@admin_required
def create_patient():
    """Tao tai khoan benh nhan THAT trong SQL Server, khong luu RAM.

    Yeu cau Admin nhap mat khau du 8 ky tu; khong tao tai khoan voi
    mat khau mac dinh hay mat khau khong ai biet.
    """
    data = request.get_json(silent=True) or request.form
    name = str(data.get("name", "")).strip()
    phone = str(data.get("phone", "")).strip()
    email = str(data.get("email", "")).strip().lower()
    dob = str(data.get("dob", "")).strip()
    password = str(data.get("password", ""))

    if not name or not phone or not password:
        return jsonify({
            "success": False,
            "message": "Can nhap ho ten, so dien thoai va mat khau."
        }), 400
    if len(password) < 8:
        return jsonify({
            "success": False,
            "message": "Mat khau phai co it nhat 8 ky tu."
        }), 400
    if len(name) > 150 or not re.fullmatch(r"[0-9+() .-]{9,20}", phone):
        return jsonify({
            "success": False,
            "message": "Ho ten hoac so dien thoai khong hop le."
        }), 400
    if email and (len(email) > 254 or not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email)):
        return jsonify({
            "success": False,
            "message": "Email khong hop le."
        }), 400
    try:
        birth_date = date.fromisoformat(dob) if dob else None
        if birth_date and birth_date > date.today():
            raise ValueError("future birth date")
    except ValueError:
        return jsonify({
            "success": False,
            "message": "Ngay sinh khong hop le."
        }), 400

    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT Id FROM dbo.TaiKhoanNguoiDung
            WHERE SoDienThoai = ? OR (? <> '' AND Email = ?)
        """, (phone, email, email))
        if cursor.fetchone():
            return jsonify({
                "success": False,
                "message": "So dien thoai hoac email da duoc dang ky."
            }), 409

        cursor.execute("""
            INSERT INTO dbo.TaiKhoanNguoiDung
                (HoTen, SoDienThoai, Email, NgaySinh, MatKhauHash, TrangThai)
            OUTPUT INSERTED.Id
            VALUES (?, ?, ?, ?, ?, N'Hoạt động')
        """, (
            name, phone, email or None, birth_date,
            generate_password_hash(password)
        ))
        new_id = cursor.fetchone()[0]
        conn.commit()
        return jsonify({
            "success": True,
            "message": "Da tao benh nhan trong SQL Server.",
            "patient": {"id": f"BN-{new_id:05d}", "name": name, "phone": phone}
        }), 201
    except Exception:
        if conn:
            conn.rollback()
        app.logger.exception("Loi them benh nhan vao SQL Server")
        return jsonify({
            "success": False,
            "message": "Khong the luu benh nhan vao SQL Server."
        }), 500
    finally:
        if conn:
            conn.close()


# =====================================================
# 12. KIEM TRA KET NOI SQL SERVER
# =====================================================

@app.route("/test-db")
@admin_required
def test_db():
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT DB_NAME()")
        database_name = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM dbo.LichHen")
        appointment_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM dbo.BacSi")
        doctor_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM dbo.LichLamViec")
        shift_count = cursor.fetchone()[0]

        return jsonify({
            "success": True,
            "message": "Kết nối SQL Server thành công",
            "database": database_name,
            "appointments": appointment_count,
            "doctors": doctor_count,
            "work_shifts": shift_count
        })
    except Exception as e:
        app.logger.exception("Lỗi kiểm tra SQL Server")
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500
    finally:
        if conn:
            conn.close()


# =====================================================
# 13. API LICH SU KHAM BENH
# =====================================================

@app.get("/api/my-appointments")
def my_appointments_api():
    phone = request.args.get("phone", "").strip()

    if not phone:
        return jsonify({
            "success": False,
            "message": "Vui lòng cung cấp số điện thoại."
        }), 400

    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                lh.Id,
                lh.HoTen,
                lh.SoDienThoai,
                lh.BacSi,
                lh.NgayKham,
                lh.GioKham,
                lh.LyDo,
                lh.TrangThai,
                ck.TenChuyenKhoa
            FROM dbo.LichHen AS lh
            LEFT JOIN dbo.BacSi AS bs
                ON lh.BacSiId = bs.Id
            LEFT JOIN dbo.ChuyenKhoa AS ck
                ON bs.ChuyenKhoaId = ck.Id
            WHERE REPLACE(
                    REPLACE(
                        REPLACE(lh.SoDienThoai, ' ', ''),
                        '-', ''
                    ),
                    '.', ''
                  ) = REPLACE(
                    REPLACE(
                        REPLACE(?, ' ', ''),
                        '-', ''
                    ),
                    '.', ''
                  )
            ORDER BY lh.Id DESC
        """, (phone,))

        appointments = []
        for row in cursor.fetchall():
            appointments.append({
                "id": row.Id,
                "code": f"LH-{row.Id:06d}",
                "patient": row.HoTen or "",
                "phone": row.SoDienThoai or "",
                "doctor": row.BacSi or "",
                "specialty": row.TenChuyenKhoa or "Chưa phân loại",
                "date": (
                    row.NgayKham.strftime("%Y-%m-%d")
                    if row.NgayKham else ""
                ),
                "time": str(row.GioKham)[:5] if row.GioKham else "",
                "reason": row.LyDo or "",
                "status": row.TrangThai or "Chờ xác nhận"
            })

        return jsonify({
            "success": True,
            "appointments": appointments
        })
    except Exception:
        app.logger.exception("Lỗi đọc lịch sử khám bệnh")
        return jsonify({
            "success": False,
            "message": "Không thể tải lịch sử khám bệnh."
        }), 500
    finally:
        if conn:
            conn.close()
# =====================================================
# QUAN LY CHUYEN KHOA VA DICH VU
# =====================================================

@app.route("/chuyen-khoa")
@admin_required
def specialties_page():
    return render_template(
        "chuyen-khoa.html",
        today=date.today().strftime("%d/%m/%Y"),
        admin_username=session.get("admin_username", "admin"),
        active_page="specialties"
    )

@app.get('/api/admin/specialties')
@admin_required
def ck_api_list():
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute('''SELECT ck.Id, ck.TenChuyenKhoa, COALESCE(cfg.PhiKham,250000) AS PhiKham,
            (SELECT COUNT(*) FROM dbo.BacSi b WHERE b.ChuyenKhoaId=ck.Id) AS DoctorCount
            FROM dbo.ChuyenKhoa ck LEFT JOIN dbo.CauHinhChuyenKhoa cfg ON cfg.ChuyenKhoaId=ck.Id
            ORDER BY ck.Id''')
        specialties = [{'id':int(r.Id),'name':r.TenChuyenKhoa,'fee':float(r.PhiKham),
                        'doctorCount':int(r.DoctorCount),'services':[]} for r in cur.fetchall()]
        by_id = {x['id']:x for x in specialties}
        cur.execute('''SELECT Id, ChuyenKhoaId, TenDichVu, PhiKham, ThoiLuongPhut, TrangThai
                       FROM dbo.DichVuKham ORDER BY Id''')
        for r in cur.fetchall():
            if r.ChuyenKhoaId in by_id:
                by_id[r.ChuyenKhoaId]['services'].append({
                    'id':int(r.Id), 'code':f'DV-{r.Id:03d}', 'name':r.TenDichVu,
                    'fee':float(r.PhiKham), 'duration':int(r.ThoiLuongPhut),
                    'status':r.TrangThai})
        return jsonify(success=True, data=specialties)
    except Exception:
        app.logger.exception('Lỗi tải danh mục dịch vụ')
        return jsonify(success=False,message='Không thể tải danh mục từ SQL Server.'),500
    finally:
        conn.close()

@app.post('/api/admin/specialties')
@admin_required
def ck_api_create_specialty():
    body=request.get_json(silent=True) or {}
    name=str(body.get('name') or '').strip()
    try: fee=float(body.get('fee'))
    except (TypeError,ValueError): fee=-1
    if not name or len(name)>120 or not 0<=fee<=100000000:
        return jsonify(success=False,message='Tên hoặc phí chuyên khoa không hợp lệ.'),400
    conn=get_db_connection()
    try:
        cur=conn.cursor()
        cur.execute('SELECT Id FROM dbo.ChuyenKhoa WHERE TenChuyenKhoa=?',(name,))
        if cur.fetchone(): return jsonify(success=False,message='Chuyên khoa đã tồn tại.'),409
        cur.execute('INSERT INTO dbo.ChuyenKhoa(TenChuyenKhoa) OUTPUT INSERTED.Id VALUES (?)',(name,))
        new_id=int(cur.fetchone()[0])
        cur.execute('INSERT INTO dbo.CauHinhChuyenKhoa(ChuyenKhoaId,PhiKham) VALUES (?,?)',(new_id,fee))
        conn.commit()
        return jsonify(success=True,id=new_id),201
    except Exception:
        conn.rollback(); app.logger.exception('Lỗi tạo chuyên khoa')
        return jsonify(success=False,message='Không tạo được chuyên khoa; kiểm tra cấu trúc bảng ChuyenKhoa.'),500
    finally: conn.close()

@app.put('/api/admin/specialties/<int:specialty_id>')
@admin_required
def ck_api_update_specialty(specialty_id):
    body=request.get_json(silent=True) or {}
    name=str(body.get('name') or '').strip()
    try: fee=float(body.get('fee'))
    except (TypeError,ValueError): fee=-1
    if not name or len(name)>120 or not 0<=fee<=100000000:
        return jsonify(success=False,message='Tên hoặc phí chuyên khoa không hợp lệ.'),400
    conn=get_db_connection()
    try:
        cur=conn.cursor()
        cur.execute('SELECT Id FROM dbo.ChuyenKhoa WHERE Id=?',(specialty_id,))
        if not cur.fetchone(): return jsonify(success=False,message='Không thấy chuyên khoa.'),404
        cur.execute('SELECT Id FROM dbo.ChuyenKhoa WHERE TenChuyenKhoa=? AND Id<>?',(name,specialty_id))
        if cur.fetchone(): return jsonify(success=False,message='Tên chuyên khoa bị trùng.'),409
        cur.execute('UPDATE dbo.ChuyenKhoa SET TenChuyenKhoa=? WHERE Id=?',(name,specialty_id))
        cur.execute('''UPDATE dbo.CauHinhChuyenKhoa SET PhiKham=? WHERE ChuyenKhoaId=?;
                       IF @@ROWCOUNT=0 INSERT INTO dbo.CauHinhChuyenKhoa(ChuyenKhoaId,PhiKham) VALUES (?,?)''',
                    (fee,specialty_id,specialty_id,fee))
        conn.commit()
        return jsonify(success=True)
    except Exception:
        conn.rollback(); app.logger.exception('Lỗi sửa chuyên khoa')
        return jsonify(success=False,message='Không sửa được chuyên khoa.'),500
    finally: conn.close()

def ck_validate_service(body):
    name=str(body.get('name') or '').strip()
    try: fee=float(body.get('fee')); duration=int(body.get('duration'))
    except (ValueError,TypeError): return None
    status=body.get('status')
    if not name or len(name)>120 or not 0<fee<=100000000 or duration not in (15,20,30,45,60) or status not in ('active','paused'):
        return None
    return name,fee,duration,status

@app.post('/api/admin/specialties/<int:specialty_id>/services')
@admin_required
def ck_api_create_service(specialty_id):
    values=ck_validate_service(request.get_json(silent=True) or {})
    if not values: return jsonify(success=False,message='Thông tin dịch vụ không hợp lệ.'),400
    conn=get_db_connection()
    try:
        cur=conn.cursor()
        cur.execute('SELECT Id FROM dbo.ChuyenKhoa WHERE Id=?',(specialty_id,))
        if not cur.fetchone(): return jsonify(success=False,message='Không thấy chuyên khoa.'),404
        cur.execute('''INSERT INTO dbo.DichVuKham(ChuyenKhoaId,TenDichVu,PhiKham,ThoiLuongPhut,TrangThai)
                       OUTPUT INSERTED.Id VALUES (?,?,?,?,?)''',(specialty_id,*values))
        new_id=int(cur.fetchone()[0]); conn.commit()
        return jsonify(success=True,id=new_id),201
    except Exception:
        conn.rollback(); app.logger.exception('Lỗi tạo dịch vụ')
        return jsonify(success=False,message='Không lưu được dịch vụ vào SQL Server.'),500
    finally: conn.close()

@app.put('/api/admin/services/<int:service_id>')
@admin_required
def ck_api_update_service(service_id):
    values=ck_validate_service(request.get_json(silent=True) or {})
    if not values: return jsonify(success=False,message='Thông tin dịch vụ không hợp lệ.'),400
    conn=get_db_connection()
    try:
        cur=conn.cursor()
        cur.execute('''UPDATE dbo.DichVuKham SET TenDichVu=?,PhiKham=?,ThoiLuongPhut=?,TrangThai=?,
                       NgayCapNhat=SYSDATETIME() WHERE Id=?''',(*values,service_id))
        if cur.rowcount==0: return jsonify(success=False,message='Không thấy dịch vụ.'),404
        conn.commit(); return jsonify(success=True)
    except Exception:
        conn.rollback(); app.logger.exception('Lỗi sửa dịch vụ')
        return jsonify(success=False,message='Không sửa được dịch vụ.'),500
    finally: conn.close()

# =====================================================
# 14. CHAY UNG DUNG
# =====================================================

if __name__ == "__main__":
    app.run(debug=True, port=5001)
