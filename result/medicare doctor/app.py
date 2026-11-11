import os
from datetime import date, timedelta
from functools import wraps
import pyodbc
from dotenv import load_dotenv
from flask import Flask, flash, jsonify, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash

load_dotenv()
app = Flask(__name__)
app.secret_key = os.environ.get('MEDICARE_DOCTOR_SECRET_KEY')
if not app.secret_key:
    raise RuntimeError('Cần đặt MEDICARE_DOCTOR_SECRET_KEY trong file .env')
app.config.update(SESSION_COOKIE_HTTPONLY=True, SESSION_COOKIE_SAMESITE='Lax',
                  SESSION_COOKIE_NAME='medicare_doctor_session')

SQL_SERVER = os.getenv('SQL_SERVER', r'LAPTOP-6A5KNTQH\SQLEXPRESS')
SQL_DATABASE = os.getenv('SQL_DATABASE', 'MediCare')
SQL_DRIVER = os.getenv('SQL_DRIVER', 'ODBC Driver 18 for SQL Server')

def get_db_connection():
    return pyodbc.connect(
        f'DRIVER={{{SQL_DRIVER}}};SERVER={SQL_SERVER};DATABASE={SQL_DATABASE};'
        'Trusted_Connection=yes;TrustServerCertificate=yes;'
    )

def doctor_required(fn):
    @wraps(fn)
    def wrapped(*args, **kwargs):
        if not session.get('doctor_id'):
            if request.path.startswith('/api/'):
                return jsonify({'success': False, 'message': 'Phiên đăng nhập bác sĩ đã hết hạn. Vui lòng đăng nhập lại.'}), 401
            return redirect(url_for('doctor_login'))
        return fn(*args, **kwargs)
    return wrapped

@app.route('/')
def home():
    return redirect(url_for('doctor_dashboard' if session.get('doctor_id') else 'doctor_login'))

@app.route('/doctor/login', methods=['GET', 'POST'])
def doctor_login():
    if session.get('doctor_id'):
        return redirect(url_for('doctor_dashboard'))
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT tk.BacSiId, tk.MatKhauHash, bs.HoTen, ck.TenChuyenKhoa
                    FROM dbo.TaiKhoanBacSi AS tk
                    JOIN dbo.BacSi AS bs ON bs.Id = tk.BacSiId
                    JOIN dbo.HoSoBacSi AS hs ON hs.BacSiId = bs.Id
                    JOIN dbo.ChuyenKhoa AS ck ON ck.Id = bs.ChuyenKhoaId
                    WHERE LOWER(LTRIM(RTRIM(hs.Email))) = LOWER(?) AND tk.KichHoat = 1
                ''', username)
                row = cursor.fetchone()
            if row and check_password_hash(row.MatKhauHash, password):
                session.clear()
                session['doctor_id'] = int(row.BacSiId)
                session['doctor_name'] = row.HoTen
                session['doctor_specialty'] = row.TenChuyenKhoa
                return redirect(url_for('doctor_dashboard'))
            flash('Tên đăng nhập hoặc mật khẩu không đúng.', 'error')
        except pyodbc.Error:
            app.logger.exception('Không thể đăng nhập bác sĩ')
            flash('Không thể kết nối cơ sở dữ liệu. Kiểm tra SQL Server và bảng tài khoản.', 'error')
    return render_template('doctor-login.html')

@app.post('/doctor/logout')
@doctor_required
def doctor_logout():
    session.clear()
    return redirect(url_for('doctor_login'))

@app.get('/doctor/dashboard')
@doctor_required
def doctor_dashboard():
    # Đặt HTML Tổng quan bác sĩ hiện tại vào templates/doctor-dashboard.html.
    return render_template('doctor-dashboard.html',
                           doctor_name=session['doctor_name'],
                           doctor_specialty=session['doctor_specialty'],
                           doctor_id=session['doctor_id'])

@app.get('/api/doctor/me')
@doctor_required
def doctor_me():
    return jsonify({'id': session['doctor_id'], 'name': session['doctor_name'],
                    'specialty': session['doctor_specialty']})

@app.get('/api/doctor/appointments')
@doctor_required
def doctor_appointments():
    day = request.args.get('date', date.today().isoformat())
    try:
        day = date.fromisoformat(day)
    except ValueError:
        return jsonify({'success': False, 'message': 'Ngày không hợp lệ'}), 400
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT Id, HoTen, SoDienThoai, NgayKham, GioKham, LyDo, TrangThai
                FROM dbo.LichHen
                WHERE BacSiId = ? AND NgayKham = ?
                  AND TrangThai IN (N'Đã xác nhận', N'Đang khám', N'Hoàn tất')
                ORDER BY GioKham, Id
            ''', session['doctor_id'], day)
            status_map = {'Đã xác nhận': 'confirmed', 'Đang khám': 'in_progress', 'Hoàn tất': 'completed'}
            result = []
            for row in cursor.fetchall():
                time_text = str(row.GioKham)[:5] if row.GioKham else '00:00'
                result.append({
                    'id': row.Id,
                    'time': time_text,
                    'endTime': '',
                    'status': status_map.get(row.TrangThai, 'confirmed'),
                    'room': 'Chưa phân phòng',
                    'reason': row.LyDo or '',
                    'history': '',
                    'recordDone': True,
                    'patient': {
                        'id': row.Id,
                        'code': f'LH-{row.Id:06d}',
                        'name': row.HoTen or 'Chưa có tên',
                        'gender': '', 'age': ''
                    }
                })
        return jsonify(result)
    except pyodbc.Error:
        app.logger.exception('Lỗi lấy lịch bác sĩ')
        return jsonify({'success': False, 'message': 'Không đọc được lịch khám'}), 500

@app.get('/api/doctor/upcoming')
@doctor_required
def doctor_upcoming():
    # Ngày mai đến hết 7 ngày tiếp theo, chỉ lịch đã xác nhận của bác sĩ đăng nhập.
    start = date.today() + timedelta(days=1)
    end = date.today() + timedelta(days=7)
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT Id, HoTen, NgayKham, GioKham, LyDo, TrangThai
                FROM dbo.LichHen
                WHERE BacSiId = ? AND NgayKham >= ? AND NgayKham <= ?
                  AND TrangThai IN (N'Đã xác nhận', N'Đang khám')
                ORDER BY NgayKham, GioKham, Id
            ''', session['doctor_id'], start, end)
            appointments = [{
                'id': r.Id,
                'date': r.NgayKham.isoformat(),
                'time': str(r.GioKham)[:5] if r.GioKham else '',
                'patient': r.HoTen or 'Chưa có tên',
                'reason': r.LyDo or '',
                'status': r.TrangThai
            } for r in cursor.fetchall()]
        return jsonify(appointments)
    except pyodbc.Error:
        app.logger.exception('Lỗi lấy lịch khám sắp tới')
        return jsonify({'success': False, 'message': 'Không đọc được lịch khám sắp tới'}), 500

@app.get('/api/doctor/completed')
@doctor_required
def doctor_completed():
    # Lịch đã hoàn tất của bác sĩ ở mọi ngày, không bị giới hạn trong hôm nay.
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT Id, HoTen, NgayKham, GioKham, LyDo
                FROM dbo.LichHen
                WHERE BacSiId = ? AND TrangThai = N'Hoàn tất'
                ORDER BY NgayKham DESC, GioKham DESC, Id DESC
            ''', session['doctor_id'])
            rows = [{
                'id': r.Id, 'date': r.NgayKham.isoformat() if r.NgayKham else '',
                'time': str(r.GioKham)[:5] if r.GioKham else '',
                'patient': r.HoTen or 'Chưa có tên', 'reason': r.LyDo or ''
            } for r in cursor.fetchall()]
        return jsonify(rows)
    except pyodbc.Error:
        app.logger.exception('Lỗi lấy lịch đã khám')
        return jsonify({'success': False, 'message': 'Không đọc được lịch đã khám'}), 500

@app.get('/api/doctor/patients/<int:patient_id>/records')
@doctor_required
def doctor_patient_records(patient_id):
    # Chưa có bảng hồ sơ khám phù hợp để truy vấn; không bịa dữ liệu bệnh án.
    return jsonify([])

@app.post('/api/doctor/appointments/<int:appointment_id>/start')
@app.post('/api/doctor/appointments/<int:appointment_id>/complete')
@doctor_required
def doctor_change_status(appointment_id):
    # Chỉ bác sĩ được phân công mới đổi được trạng thái; chuyển trạng thái có điều kiện.
    complete = request.path.endswith('/complete')
    old_status = 'Đang khám' if complete else 'Đã xác nhận'
    new_status = 'Hoàn tất' if complete else 'Đang khám'
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE dbo.LichHen SET TrangThai = ?
            WHERE Id = ? AND BacSiId = ? AND TrangThai = ?
        ''', new_status, appointment_id, session['doctor_id'], old_status)
        updated = cursor.rowcount > 0
        conn.commit()
        if not updated:
            return jsonify({'success': False, 'message': 'Lịch không thuộc bác sĩ hoặc trạng thái không phù hợp'}), 409
        return jsonify({'success': True, 'status': new_status})
    except pyodbc.Error:
        if conn:
            conn.rollback()
        app.logger.exception('Lỗi cập nhật trạng thái')
        return jsonify({'success': False, 'message': 'Không cập nhật được lịch'}), 500
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    app.run(port=5002, debug=True)
