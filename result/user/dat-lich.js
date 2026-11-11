/* ==========================================
   1. CẤU HÌNH API
========================================== */

const API_BASE = "http://127.0.0.1:5000/api";
const API_URL = `${API_BASE}/lich-hen`;

let doctorsFromAPI = [];
let availableTimeSlots = [];
let selectedDoctorId = null;


/* ==========================================
   2. GIÁ KHÁM MẪU
   Chưa lấy giá từ SQL Server.
========================================== */

const consultationFees = {
    "Nội khoa": 250000,
    "Ngoại khoa": 250000,
    "Nhi khoa": 250000,
    "Tim mạch": 350000,
    "Da liễu": 200000,
    "Tai - Mũi - Họng": 250000
};

function getConsultationFee(specialty) {
    return consultationFees[specialty] ?? null;
}

function formatCurrency(amount) {
    if (amount === null || amount === undefined) {
        return "-";
    }

    return new Intl.NumberFormat("vi-VN", {
        maximumFractionDigits: 0
    }).format(amount) + " đ";
}


/* ==========================================
   3. LẤY CÁC PHẦN TỬ HTML
========================================== */

const specialtySelect = document.getElementById("specialty");
const doctorSelect = document.getElementById("doctor");

const doctorPreview = document.getElementById("doctor-preview");
const doctorAvatar = document.getElementById("doctor-avatar");
const doctorName = document.getElementById("doctor-name");
const doctorSpecialty = document.getElementById("doctor-specialty");
const doctorStatus = document.getElementById("doctor-status");

const dateInput = document.getElementById("date");
const timeList = document.getElementById("time-list");

const patientNameInput = document.getElementById("patient-name");
const patientPhoneInput = document.getElementById("patient-phone");
const reasonInput = document.getElementById("reason");

const confirmSpecialty = document.getElementById("confirm-specialty");
const confirmDoctor = document.getElementById("confirm-doctor");
const confirmDate = document.getElementById("confirm-date");
const confirmTime = document.getElementById("confirm-time");
const confirmPrice = document.getElementById("confirm-price");

const summarySpecialty = document.getElementById("summary-specialty");
const summaryDoctor = document.getElementById("summary-doctor");
const summaryDate = document.getElementById("summary-date");
const summaryTime = document.getElementById("summary-time");
const summaryPrice = document.getElementById("summary-price");

const bookingButton = document.getElementById("booking-btn");
const successBox = document.getElementById("success-box");
const bookingCode = document.getElementById("booking-code");


/* ==========================================
   4. THIẾT LẬP NGÀY KHÁM
========================================== */

function getTodayString() {
    const now = new Date();

    const year = now.getFullYear();
    const month = String(now.getMonth() + 1).padStart(2, "0");
    const day = String(now.getDate()).padStart(2, "0");

    return `${year}-${month}-${day}`;
}

dateInput.min = getTodayString();


/* ==========================================
   5. CÁC HÀM HỖ TRỢ
========================================== */

function getSelectedDoctor() {
    const doctorId = Number(doctorSelect.value);

    if (!doctorId) {
        return null;
    }

    return doctorsFromAPI.find(
        doctor => Number(doctor.id) === doctorId
    ) || null;
}


function formatDate(dateValue) {
    if (!dateValue) {
        return "-";
    }

    const parts = dateValue.split("-");

    if (parts.length !== 3) {
        return dateValue;
    }

    return `${parts[2]}/${parts[1]}/${parts[0]}`;
}


function clearSuccessMessage() {
    successBox.classList.add("hidden");

    if (bookingButton) {
        bookingButton.disabled = false;
        bookingButton.textContent = "Xác nhận đặt lịch";
    }
}


function isValidPhone(phone) {
    return /^(0\d{9}|\+84\d{9})$/.test(phone);
}


function resetSelectedTime() {
    confirmTime.textContent = "-";
    summaryTime.textContent = "-";
}


function resetTimeSlots() {
    availableTimeSlots = [];

    timeList.innerHTML = `
        <p class="time-empty">
            Vui lòng chọn bác sĩ và ngày khám trước.
        </p>
    `;

    resetSelectedTime();
}


/* ==========================================
   6. LẤY DANH SÁCH BÁC SĨ TỪ BACKEND
========================================== */

async function loadDoctors() {
    doctorSelect.disabled = true;

    doctorSelect.innerHTML = `
        <option value="">Đang tải danh sách bác sĩ...</option>
    `;

    try {
        const response = await fetch(`${API_BASE}/bac-si`);
        const result = await response.json();

        if (!response.ok || result.status !== "success") {
            throw new Error(
                result.message || "Không thể tải danh sách bác sĩ."
            );
        }

        doctorsFromAPI = result.data || [];

        doctorSelect.innerHTML = `
            <option value="">-- Chọn bác sĩ --</option>
        `;

        doctorSelect.disabled = true;

    } catch (error) {
        console.error("Lỗi tải danh sách bác sĩ:", error);

        doctorSelect.innerHTML = `
            <option value="">Không thể tải danh sách bác sĩ</option>
        `;

        doctorSelect.disabled = true;

        alert(
            "Không thể tải danh sách bác sĩ từ hệ thống.\n" +
            "Vui lòng kiểm tra backend và SQL Server."
        );
    }
}


/* ==========================================
   7. HIỂN THỊ BÁC SĨ THEO CHUYÊN KHOA
========================================== */

function updateDoctors() {
    const specialty = specialtySelect.value;

    doctorSelect.innerHTML = `
        <option value="">-- Chọn bác sĩ --</option>
    `;

    clearSuccessMessage();
    selectedDoctorId = null;

    if (!specialty) {
        doctorSelect.disabled = true;
        doctorPreview.classList.add("hidden");

        resetTimeSlots();
        updateSummary();

        return;
    }

    const doctors = doctorsFromAPI.filter(
        doctor => doctor.specialty === specialty
    );

    if (doctors.length === 0) {
        doctorSelect.innerHTML = `
            <option value="">Chưa có bác sĩ thuộc chuyên khoa này</option>
        `;

        doctorSelect.disabled = true;
        doctorPreview.classList.add("hidden");

        resetTimeSlots();
        updateSummary();

        return;
    }

    doctors.forEach(doctor => {
        const option = document.createElement("option");

        // Dùng ID bác sĩ làm value để liên kết chính xác với SQL.
        option.value = doctor.id;

        option.textContent = doctor.room
            ? `${doctor.name} - ${doctor.room}`
            : doctor.name;

        doctorSelect.appendChild(option);
    });

    doctorSelect.disabled = false;
    doctorPreview.classList.add("hidden");

    resetTimeSlots();
    updateSummary();
}


/* ==========================================
   8. HIỂN THỊ THÔNG TIN BÁC SĨ
========================================== */

function updateDoctorPreview() {
    const doctor = getSelectedDoctor();

    clearSuccessMessage();
    selectedDoctorId = null;

    if (!doctor) {
        doctorPreview.classList.add("hidden");

        resetTimeSlots();
        updateSummary();

        return;
    }

    selectedDoctorId = doctor.id;

    doctorPreview.classList.remove("hidden");

    doctorName.textContent = doctor.name;

    doctorSpecialty.textContent =
        `${doctor.specialty} • ${doctor.room || "Chưa cập nhật phòng"}`;

    doctorStatus.textContent = "Đang hoạt động";

    doctorAvatar.textContent = doctor.name
        .replace("BS. ", "")
        .split(" ")
        .map(word => word[0])
        .slice(-2)
        .join("")
        .toUpperCase();

    resetTimeSlots();

    if (dateInput.value) {
        loadAvailableTimeSlots();
    }

    updateSummary();
}


/* ==========================================
   9. LẤY KHUNG GIỜ LÀM VIỆC TỪ BACKEND
========================================== */

async function loadAvailableTimeSlots() {
    const doctor = getSelectedDoctor();
    const date = dateInput.value;

    resetSelectedTime();
    availableTimeSlots = [];

    if (!doctor || !date) {
        resetTimeSlots();
        return;
    }

    selectedDoctorId = doctor.id;

    timeList.innerHTML = `
        <p class="time-empty">
            Đang tải khung giờ làm việc...
        </p>
    `;

    try {
        const url =
            `${API_BASE}/lich-lam-viec` +
            `?bac_si_id=${encodeURIComponent(doctor.id)}` +
            `&ngay_kham=${encodeURIComponent(date)}`;

        const response = await fetch(url);
        const result = await response.json();

        // Tránh hiển thị kết quả cũ nếu người dùng vừa đổi bác sĩ/ngày.
        if (
            doctorSelect.value != doctor.id ||
            dateInput.value !== date
        ) {
            return;
        }

        if (!response.ok || result.status !== "success") {
            throw new Error(
                result.message || "Không thể tải khung giờ."
            );
        }

        availableTimeSlots = result.data || [];

        renderTimeSlots();

    } catch (error) {
        console.error("Lỗi tải khung giờ:", error);

        timeList.innerHTML = `
            <p class="time-empty">
                Không thể tải khung giờ. Vui lòng thử lại.
            </p>
        `;

        resetSelectedTime();
    }
}


/* ==========================================
   10. HIỂN THỊ KHUNG GIỜ KHÁM
========================================== */

function renderTimeSlots() {
    const doctor = getSelectedDoctor();
    const date = dateInput.value;

    resetSelectedTime();

    if (!doctor || !date) {
        resetTimeSlots();
        updateSummary();
        return;
    }

    timeList.innerHTML = "";

    if (availableTimeSlots.length === 0) {
        timeList.innerHTML = `
            <p class="time-empty">
                Bác sĩ không có ca làm việc trong ngày này.
            </p>
        `;

        updateSummary();
        return;
    }

    availableTimeSlots.forEach(slot => {
        const button = document.createElement("button");

        button.type = "button";
        button.className = "time-btn";

        button.textContent = slot.time;
        button.dataset.time = slot.time;
        button.dataset.start = slot.start;
        button.dataset.shiftId = slot.shift_id;
if (slot.available) {
    button.dataset.status = "available";
    button.classList.add("available");

    button.addEventListener("click", function () {
        selectTimeSlot(
            button,
            doctor.name,
            date,
            slot.time
        );
    });

} else {
    button.dataset.status = "full";
    button.classList.add("unavailable");
    button.disabled = true;

    button.title =
        "Khung giờ này đã có người đặt.";
}

        timeList.appendChild(button);
    });

    updateSummary();
}


/* ==========================================
   11. CHỌN KHUNG GIỜ
========================================== */

function selectTimeSlot(button, doctor, date, time) {
    if (
        button.disabled ||
        button.dataset.status !== "available"
    ) {
        alert(
            "Khung giờ này hiện không còn chỗ. " +
            "Vui lòng chọn khung giờ khác."
        );

        return;
    }

    document.querySelectorAll(".time-btn").forEach(btn => {
        btn.classList.remove("selected");
    });

    button.classList.add("selected");

    confirmTime.textContent = time;
    summaryTime.textContent = time;

    updateSummary();
}


/* ==========================================
   12. CẬP NHẬT TÓM TẮT VÀ GIÁ KHÁM
========================================== */

function updateSummary() {
    const specialty = specialtySelect.value;
    const doctor = getSelectedDoctor();
    const date = dateInput.value;

    const fee = getConsultationFee(specialty);
    const feeText = formatCurrency(fee);

    summarySpecialty.textContent = specialty || "-";
    summaryDoctor.textContent = doctor ? doctor.name : "-";
    summaryDate.textContent = date ? formatDate(date) : "-";

    confirmSpecialty.textContent = specialty || "-";
    confirmDoctor.textContent = doctor ? doctor.name : "-";
    confirmDate.textContent = date ? formatDate(date) : "-";

    if (confirmPrice) {
        confirmPrice.textContent = specialty ? feeText : "-";
    }

    if (summaryPrice) {
        summaryPrice.textContent = specialty ? feeText : "-";
    }
}


/* ==========================================
   13. GỬI LỊCH KHÁM LÊN BACKEND
========================================== */

async function handleBooking() {
    const specialty = specialtySelect.value;
    const doctor = getSelectedDoctor();
    const date = dateInput.value;
    const time = confirmTime.textContent;

    const patientName = patientNameInput.value.trim();

    const patientPhone = patientPhoneInput.value
        .trim()
        .replace(/\s/g, "");

    const reason = reasonInput.value.trim();

    if (!specialty) {
        alert("Vui lòng chọn chuyên khoa.");
        specialtySelect.focus();
        return;
    }

    if (!doctor) {
        alert("Vui lòng chọn bác sĩ.");
        doctorSelect.focus();
        return;
    }

    if (!date) {
        alert("Vui lòng chọn ngày khám.");
        dateInput.focus();
        return;
    }

    if (date < getTodayString()) {
        alert("Không thể đặt lịch cho ngày đã qua.");
        dateInput.focus();
        return;
    }

    if (!time || time === "-") {
        alert("Vui lòng chọn khung giờ khám.");
        return;
    }

    if (!patientName) {
        alert("Vui lòng nhập họ và tên.");
        patientNameInput.focus();
        return;
    }

    if (!patientPhone || !isValidPhone(patientPhone)) {
        alert(
            "Số điện thoại chưa hợp lệ. " +
            "Vui lòng nhập số điện thoại Việt Nam gồm 10 chữ số."
        );

        patientPhoneInput.focus();
        return;
    }

    // Kiểm tra khung giờ đã chọn còn trong dữ liệu vừa tải không.
    const selectedSlot = availableTimeSlots.find(
        slot => slot.time === time && slot.available
    );

    if (!selectedSlot) {
        alert(
            "Khung giờ này không còn khả dụng. " +
            "Vui lòng tải lại danh sách giờ khám."
        );

        await loadAvailableTimeSlots();
        return;
    }

    bookingButton.disabled = true;
    bookingButton.textContent = "Đang lưu lịch khám...";

    try {
        // Chỉ gửi giờ bắt đầu cho backend.
        const startTime = selectedSlot.start;

        const payload = {
            ho_ten: patientName,
            so_dien_thoai: patientPhone,
            bac_si: doctor.name,
            bac_si_id: doctor.id,
            ngay_kham: date,
            gio_kham: startTime,
            ly_do: reason
        };

        const response = await fetch(API_URL, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(payload)
        });

        let result;

        try {
            result = await response.json();
        } catch (parseError) {
            throw new Error(
                "API không trả về dữ liệu JSON hợp lệ."
            );
        }

        if (
            !response.ok ||
            !result ||
            result.status !== "success"
        ) {
            throw new Error(
                (result && result.message) ||
                "Không thể lưu lịch khám."
            );
        }

        // Lưu thông tin lịch vừa đặt vào trình duyệt.
        const booking = {
            id: result.id,

            code: result.code || `LH-${String(result.id).padStart(6, "0")}`,
            
            specialty: specialty,
            doctor: doctor.name,
            doctorId: doctor.id,
            date: date,
            time: time,
            patientName: patientName,
            patientPhone: patientPhone,
            reason: reason,
            consultationFee: getConsultationFee(specialty),
            createdAt: new Date().toISOString()
        };

        localStorage.setItem(
            "medicareLatestBooking",
            JSON.stringify(booking)
        );

        // Hiển thị thông báo thành công.
        bookingCode.textContent = booking.code;
        successBox.classList.remove("hidden");

        bookingButton.disabled = true;
        bookingButton.textContent = "Đã đặt lịch";

        alert(
            "Đặt lịch thành công!\n" +
            "Mã lịch khám: " + booking.code
        );

        // Tải lại số lượng chỗ sau khi đặt lịch.
        await loadAvailableTimeSlots();

        // Giữ thông báo thành công.
        bookingCode.textContent = booking.code;
        successBox.classList.remove("hidden");

        bookingButton.disabled = true;
        bookingButton.textContent = "Đã đặt lịch";

    } catch (error) {
        console.error("Lỗi đặt lịch:", error);

        alert(
            "Chưa thể lưu lịch khám vào hệ thống.\n\n" +
            "Chi tiết: " + error.message
        );

        bookingButton.disabled = false;
        bookingButton.textContent = "Xác nhận đặt lịch";

        // Nếu ca vừa bị tắt hoặc đã đủ chỗ, tải lại dữ liệu.
        await loadAvailableTimeSlots();
    }
}


/* ==========================================
   14. GẮN SỰ KIỆN
========================================== */

specialtySelect.addEventListener("change", updateDoctors);

doctorSelect.addEventListener("change", updateDoctorPreview);

dateInput.addEventListener("change", function () {
    clearSuccessMessage();

    const date = dateInput.value;

    if (date && date < getTodayString()) {
        alert(
            "Vui lòng chọn ngày hôm nay hoặc ngày trong tương lai."
        );

        dateInput.value = "";

        resetTimeSlots();
        updateSummary();

        return;
    }

    loadAvailableTimeSlots();
    updateSummary();
});

bookingButton.addEventListener("click", handleBooking);


/* ==========================================
   15. NHẬN DỮ LIỆU TỪ TRANG BÁC SĨ
========================================== */

async function restoreSelectedDoctor() {
    const selectedSpecialty =
        localStorage.getItem("selectedSpecialty");

    const selectedDoctor =
        localStorage.getItem("selectedDoctor");

    if (
        selectedSpecialty &&
        specialtySelect.querySelector(
            `option[value="${CSS.escape(selectedSpecialty)}"]`
        )
    ) {
        specialtySelect.value = selectedSpecialty;

        updateDoctors();

        const doctor = doctorsFromAPI.find(item =>
            item.name === selectedDoctor &&
            item.specialty === selectedSpecialty
        );

        if (doctor) {
            doctorSelect.value = String(doctor.id);
            updateDoctorPreview();
        }
    }

    localStorage.removeItem("selectedSpecialty");
    localStorage.removeItem("selectedDoctor");
    localStorage.removeItem("selectedRoom");
}


/* ==========================================
   16. KHỞI TẠO
========================================== */

async function initializeBookingPage() {
    doctorSelect.disabled = true;

    resetTimeSlots();
    updateSummary();

    await loadDoctors();

    if (doctorsFromAPI.length > 0) {
        await restoreSelectedDoctor();
    }
}

initializeBookingPage();