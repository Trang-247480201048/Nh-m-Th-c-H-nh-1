
import os
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
                "patient_code": "—",
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
# 11. DANH SACH BENH NHAN (GIU DU LIEU HIEN TAI)
# =====================================================

patients = [
    {
        "id": "BN-00128", "name": "Nguyễn Thị Mai",
        "gender": "Nữ", "age": 41, "phone": "0903 456 789",
        "last_visit": "12/09/2026", "visits": 5,
        "status": "Đang hoạt động", "dob": "14/05/1985",
        "email": "mai.nguyen@gmail.com",
        "address": "24 Láng Hạ, Đống Đa, Hà Nội",
        "insurance": "GD4 01 234 567 8901",
        "registered": "15/03/2025"
    },
    {
        "id": "BN-00129", "name": "Phạm Văn Hùng",
        "gender": "Nam", "age": 58, "phone": "0912 345 678",
        "last_visit": "05/10/2026", "visits": 8,
        "status": "Đang hoạt động", "dob": "09/11/1967",
        "email": "hung.pham@gmail.com",
        "address": "Cầu Giấy, Hà Nội",
        "insurance": "GD4 02 345 678 9012",
        "registered": "20/04/2025"
    },
    {
        "id": "BN-00130", "name": "Trần Ngọc Linh",
        "gender": "Nữ", "age": 26, "phone": "0987 654 321",
        "last_visit": "", "visits": 1,
        "status": "Đang hoạt động", "dob": "21/07/2000",
        "email": "linh.tran@gmail.com",
        "address": "Hai Bà Trưng, Hà Nội",
        "insurance": "", "registered": "06/10/2026"
    },
    {
        "id": "BN-00131", "name": "Lê Minh Khang",
        "gender": "Nam", "age": 7, "phone": "0938 222 666",
        "last_visit": "22/08/2026", "visits": 3,
        "status": "Đang hoạt động", "dob": "11/02/2019",
        "email": "khang.le@gmail.com",
        "address": "Thanh Xuân, Hà Nội",
        "insurance": "GD4 03 456 789 0123",
        "registered": "03/02/2026"
    },
    {
        "id": "BN-00132", "name": "Võ Thanh Tâm",
        "gender": "Nữ", "age": 35, "phone": "0909 112 233",
        "last_visit": "18/09/2026", "visits": 2,
        "status": "Đang hoạt động", "dob": "17/04/1991",
        "email": "tam.vo@gmail.com",
        "address": "Ba Đình, Hà Nội",
        "insurance": "GD4 04 567 890 1234",
        "registered": "12/01/2026"
    },
    {
        "id": "BN-00133", "name": "Đặng Quốc Bảo",
        "gender": "Nam", "age": 46, "phone": "0972 456 890",
        "last_visit": "01/10/2026", "visits": 6,
        "status": "Đang hoạt động", "dob": "30/08/1980",
        "email": "bao.dang@gmail.com",
        "address": "Hoàng Mai, Hà Nội",
        "insurance": "GD4 05 678 901 2345",
        "registered": "11/11/2025"
    },
    {
        "id": "BN-00134", "name": "Bùi Thị Hương",
        "gender": "Nữ", "age": 62, "phone": "0918 775 664",
        "last_visit": "20/10/2026", "visits": 12,
        "status": "Đang hoạt động", "dob": "05/01/1964",
        "email": "huong.bui@gmail.com",
        "address": "Long Biên, Hà Nội",
        "insurance": "GD4 06 789 012 3456",
        "registered": "01/09/2024"
    },
    {
        "id": "BN-00135", "name": "Hoàng Anh Tuấn",
        "gender": "Nam", "age": 31, "phone": "0966 231 234",
        "last_visit": "20/10/2026", "visits": 4,
        "status": "Đang hoạt động", "dob": "02/12/1994",
        "email": "tuan.hoang@gmail.com",
        "address": "Nam Từ Liêm, Hà Nội",
        "insurance": "GD4 07 890 123 4567",
        "registered": "18/05/2025"
    },
    {
        "id": "BN-00136", "name": "Ngô Phương Anh",
        "gender": "Nữ", "age": 29, "phone": "0902 555 888",
        "last_visit": "16/07/2026", "visits": 2,
        "status": "Đã khóa", "dob": "19/03/1997",
        "email": "anh.ngo@gmail.com",
        "address": "Đống Đa, Hà Nội",
        "insurance": "", "registered": "08/06/2025"
    }
]


@app.route("/patients", endpoint="patients")
@admin_required
def patients_page():
    return render_template(
        "patients.html",
        patients=patients,
        today_long=date.today().strftime("%A, %d/%m/%Y"),
        today=date.today().strftime("%d/%m/%Y"),
        admin_username=session.get("admin_username", "admin"),
        active_page="patients"
    )


@app.get("/api/patients")
@admin_required
def patients_api():
    return jsonify({"success": True, "patients": patients})


@app.post("/api/patients")
@admin_required
def create_patient():
    data = request.get_json(silent=True) or request.form

    name = str(data.get("name", "")).strip()
    phone = str(data.get("phone", "")).strip()

    if not name or not phone:
        return jsonify({
            "success": False,
            "message": "Vui lòng nhập họ tên và số điện thoại."
        }), 400

    next_number = 128 + len(patients)

    item = {
        "id": f"BN-{next_number:05d}",
        "name": name,
        "gender": str(data.get("gender", "Khác")),
        "age": 0,
        "phone": phone,
        "last_visit": "",
        "visits": 0,
        "status": "Đang hoạt động",
        "dob": str(data.get("dob", "")),
        "email": str(data.get("email", "")),
        "address": str(data.get("address", "")),
        "insurance": "",
        "registered": date.today().strftime("%d/%m/%Y")
    }

    patients.append(item)
    return jsonify({"success": True, "patient": item}), 201


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

# =====================================================
# 14. CHAY UNG DUNG
# =====================================================

if __name__ == "__main__":
    app.run(debug=True, port=5001)
