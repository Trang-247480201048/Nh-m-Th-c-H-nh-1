
/* ==========================================
   1. DỮ LIỆU BÁC SĨ
========================================== */

const doctorsBySpecialty = {
    "Nội khoa": [
        { name: "BS. Nguyễn Hà Phương", room: "Phòng 101" },
        { name: "BS. Trần Minh Anh", room: "Phòng 102" },
        { name: "BS. Lê Hoàng Nam", room: "Phòng 103" },
        { name: "BS. Phạm Thu Hà", room: "Phòng 104" }
    ],

    "Ngoại khoa": [
        { name: "BS. Nguyễn Văn An", room: "Phòng 201" },
        { name: "BS. Trần Quốc Việt", room: "Phòng 202" },
        { name: "BS. Lê Văn Minh", room: "Phòng 203" },
        { name: "BS. Hoàng Đức Long", room: "Phòng 204" }
    ],

    "Nhi khoa": [
        { name: "BS. Nguyễn Thị Lan", room: "Phòng 301" },
        { name: "BS. Phạm Minh Hương", room: "Phòng 302" },
        { name: "BS. Trần Thu Trang", room: "Phòng 303" },
        { name: "BS. Đỗ Ngọc Anh", room: "Phòng 304" }
    ],

    "Tim mạch": [
        { name: "BS. Nguyễn Văn Bình", room: "Phòng 401" },
        { name: "BS. Trần Thị Mai", room: "Phòng 402" },
        { name: "BS. Lê Quốc Huy", room: "Phòng 403" },
        { name: "BS. Phạm Văn Sơn", room: "Phòng 404" }
    ],

    "Da liễu": [
        { name: "BS. Nguyễn Thu Hà", room: "Phòng 501" },
        { name: "BS. Trần Ngọc Mai", room: "Phòng 502" },
        { name: "BS. Lê Thanh Hằng", room: "Phòng 503" },
        { name: "BS. Phạm Quỳnh Anh", room: "Phòng 504" }
    ],

    "Tai - Mũi - Họng": [
        { name: "BS. Nguyễn Đức Anh", room: "Phòng 601" },
        { name: "BS. Trần Minh Đức", room: "Phòng 602" },
        { name: "BS. Lê Thị Hương", room: "Phòng 603" },
        { name: "BS. Hoàng Minh Châu", room: "Phòng 604" }
    ]
};


/* ==========================================
   2. DANH SÁCH KHUNG GIỜ
========================================== */

const timeSlots = [
    "08:00 - 08:30",
    "08:30 - 09:00",
    "09:00 - 09:30",
    "09:30 - 10:00",
    "10:00 - 10:30",
    "10:30 - 11:00",
    "13:30 - 14:00",
    "14:00 - 14:30",
    "14:30 - 15:00",
    "15:00 - 15:30",
    "15:30 - 16:00",
    "16:00 - 16:30"
];


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

const summarySpecialty = document.getElementById("summary-specialty");
const summaryDoctor = document.getElementById("summary-doctor");
const summaryDate = document.getElementById("summary-date");
const summaryTime = document.getElementById("summary-time");

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
    const specialty = specialtySelect.value;
    const selectedName = doctorSelect.value;

    if (!specialty || !selectedName) {
        return null;
    }

    const doctors = doctorsBySpecialty[specialty] || [];

    return doctors.find(doctor => doctor.name === selectedName) || null;
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
    bookingButton.disabled = false;
    bookingButton.textContent = "Xác nhận đặt lịch";
}


function getBookedSlots() {
    try {
        const data = JSON.parse(
            localStorage.getItem("medicareBookedSlots") || "[]"
        );

        return Array.isArray(data) ? data : [];
    } catch (error) {
        return [];
    }
}


function isSlotBooked(doctor, date, time) {
    return getBookedSlots().some(booking =>
        booking.doctor === doctor &&
        booking.date === date &&
        booking.time === time
    );
}


/* ==========================================
   6. TẠO DỮ LIỆU GIỜ KHÁM MẪU
   Mỗi bác sĩ mỗi ngày:
   - 1 khung giờ đã kín
   - 1 khung giờ chỉ còn một suất
========================================== */

function getDoctorIndex(doctorName) {
    let index = 0;

    for (const specialty in doctorsBySpecialty) {
        const doctors = doctorsBySpecialty[specialty];

        const foundIndex = doctors.findIndex(
            doctor => doctor.name === doctorName
        );

        if (foundIndex !== -1) {
            return index + foundIndex;
        }

        index += doctors.length;
    }

    return 0;
}


function getInitialSlotStatus(doctorName, date, slotIndex) {
    const day = Number(date.split("-")[2]);
    const doctorIndex = getDoctorIndex(doctorName);

    const fullIndex =
        (day + doctorIndex) % timeSlots.length;

    const lastIndex =
        (day + doctorIndex + 5) % timeSlots.length;

    if (slotIndex === fullIndex) {
        return "full";
    }

    if (slotIndex === lastIndex) {
        return "last";
    }

    return "available";
}


function getSlotStatus(doctorName, date, time, slotIndex) {
    if (isSlotBooked(doctorName, date, time)) {
        return "full";
    }

    return getInitialSlotStatus(doctorName, date, slotIndex);
}


/* ==========================================
   7. HIỂN THỊ BÁC SĨ THEO CHUYÊN KHOA
========================================== */

function updateDoctors() {
    const specialty = specialtySelect.value;

    doctorSelect.innerHTML = "";
    clearSuccessMessage();

    if (!specialty) {
        doctorSelect.disabled = true;

        doctorSelect.innerHTML = `
            <option value="">
                -- Vui lòng chọn chuyên khoa trước --
            </option>
        `;

        doctorPreview.classList.add("hidden");

        resetTimeSlots();
        updateSummary();

        return;
    }

    doctorSelect.innerHTML = `
        <option value="">-- Chọn bác sĩ --</option>
    `;

    const doctors = doctorsBySpecialty[specialty] || [];

    doctors.forEach(doctor => {
        const option = document.createElement("option");

        option.value = doctor.name;
        option.textContent = `${doctor.name} - ${doctor.room}`;

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
    const specialty = specialtySelect.value;
    const doctor = getSelectedDoctor();

    clearSuccessMessage();

    if (!specialty || !doctor) {
        doctorPreview.classList.add("hidden");

        resetTimeSlots();
        updateSummary();

        return;
    }

    doctorPreview.classList.remove("hidden");

    doctorName.textContent = doctor.name;
    doctorSpecialty.textContent = `${specialty} • ${doctor.room}`;
    doctorStatus.textContent = "Đang làm việc";

    doctorAvatar.textContent = doctor.name
        .replace("BS. ", "")
        .split(" ")
        .map(word => word[0])
        .slice(-2)
        .join("")
        .toUpperCase();

    resetTimeSlots();

    if (dateInput.value) {
        renderTimeSlots();
    }

    updateSummary();
}


/* ==========================================
   9. HIỂN THỊ KHUNG GIỜ KHÁM
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

    const day = Number(date.split("-")[2]);

    if (day < 1 || day > 19) {
        timeList.innerHTML = `
            <p class="time-empty">
                Vui lòng chọn ngày từ ngày 1 đến ngày 19.
            </p>
        `;

        updateSummary();
        return;
    }

    timeList.innerHTML = "";

    timeSlots.forEach((time, index) => {
        const status = getSlotStatus(
            doctor.name,
            date,
            time,
            index
        );

        const button = document.createElement("button");

        button.type = "button";
        button.className = "time-btn";
        button.textContent = time;
        button.dataset.time = time;
        button.dataset.status = status;

        if (status === "full") {
            button.classList.add("unavailable");
            button.title = "Khung giờ này đã kín.";
        } else if (status === "last") {
            button.classList.add("last-slot");
            button.title = "Chỉ còn 1 suất khám.";
        } else {
            button.classList.add("available");
        }

        // Cho phép bấm giờ đã kín để hiện thông báo.
        button.addEventListener("click", function () {
            selectTimeSlot(button, doctor.name, date, time);
        });

        timeList.appendChild(button);
    });

    updateSummary();
}


/* ==========================================
   10. CHỌN KHUNG GIỜ
========================================== */

function selectTimeSlot(button, doctor, date, time) {
    if (
        button.dataset.status === "full" ||
        isSlotBooked(doctor, date, time)
    ) {
        alert(
            "Không thể chọn khung giờ này vì đã có người đặt.\n" +
            "Vui lòng chọn khung giờ khác!"
        );

        renderTimeSlots();
        return;
    }

    document.querySelectorAll(".time-btn").forEach(btn => {
        btn.classList.remove("selected");
    });

    button.classList.add("selected");

    confirmTime.textContent = time;
    summaryTime.textContent = time;

    if (button.dataset.status === "last") {
        alert("Lưu ý: Khung giờ này chỉ còn 1 suất khám!");
    }

    updateSummary();
}


function resetSelectedTime() {
    confirmTime.textContent = "-";
    summaryTime.textContent = "-";
}


/* ==========================================
   11. RESET KHUNG GIỜ
========================================== */

function resetTimeSlots() {
    timeList.innerHTML = `
        <p class="time-empty">
            Vui lòng chọn bác sĩ và ngày khám trước.
        </p>
    `;

    resetSelectedTime();
}


/* ==========================================
   12. CẬP NHẬT THÔNG TIN TÓM TẮT
========================================== */

function updateSummary() {
    const specialty = specialtySelect.value;
    const doctor = doctorSelect.value;
    const date = dateInput.value;

    summarySpecialty.textContent = specialty || "-";
    summaryDoctor.textContent = doctor || "-";
    summaryDate.textContent = date ? formatDate(date) : "-";

    confirmSpecialty.textContent = specialty || "-";
    confirmDoctor.textContent = doctor || "-";
    confirmDate.textContent = date ? formatDate(date) : "-";
}


/* ==========================================
   13. KIỂM TRA SỐ ĐIỆN THOẠI
========================================== */

function isValidPhone(phone) {
    return /^(0|\+84)[0-9]{9,10}$/.test(phone);
}


/* ==========================================
   14. TẠO MÃ LỊCH KHÁM
========================================== */

function generateBookingCode(dateValue) {
    const cleanDate = dateValue.replace(/-/g, "");
    const randomNumber = Math.floor(Math.random() * 900) + 100;

    return `LK${cleanDate}${randomNumber}`;
}


/* ==========================================
   15. XÁC NHẬN ĐẶT LỊCH
========================================== */

function handleBooking() {
    const specialty = specialtySelect.value;
    const doctor = doctorSelect.value;
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

    const day = Number(date.split("-")[2]);

    if (day < 1 || day > 19) {
        alert("Vui lòng chọn ngày khám từ ngày 1 đến ngày 19.");
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

    if (!patientPhone) {
        alert("Vui lòng nhập số điện thoại.");
        patientPhoneInput.focus();
        return;
    }

    if (!isValidPhone(patientPhone)) {
        alert("Số điện thoại không hợp lệ.");
        patientPhoneInput.focus();
        return;
    }

    // Kiểm tra lại giờ trước khi lưu lịch.
    if (isSlotBooked(doctor, date, time)) {
        alert(
            "Khung giờ này đã được đặt trước.\n" +
            "Vui lòng chọn khung giờ khác!"
        );

        renderTimeSlots();
        return;
    }

    // Kiểm tra giờ đã kín theo dữ liệu giả lập.
    const selectedIndex = timeSlots.indexOf(time);

    if (
        selectedIndex === -1 ||
        getInitialSlotStatus(doctor, date, selectedIndex) === "full"
    ) {
        alert(
            "Không thể đặt khung giờ này vì đã kín.\n" +
            "Vui lòng chọn khung giờ khác!"
        );

        renderTimeSlots();
        return;
    }

    const bookings = getBookedSlots();

    const alreadyBooked = bookings.some(booking =>
        booking.doctor === doctor &&
        booking.date === date &&
        booking.time === time
    );

    if (alreadyBooked) {
        alert(
            "Khung giờ này đã được đặt trước. " +
            "Vui lòng chọn giờ khác."
        );

        renderTimeSlots();
        return;
    }

    const booking = {
        code: generateBookingCode(date),
        specialty: specialty,
        doctor: doctor,
        date: date,
        time: time,
        patientName: patientName,
        patientPhone: patientPhone,
        reason: reason,
        createdAt: new Date().toISOString()
    };

    // Lưu giờ đã đặt để tránh đặt trùng trên trình duyệt.
    bookings.push({
        doctor: doctor,
        date: date,
        time: time
    });

    localStorage.setItem(
        "medicareBookedSlots",
        JSON.stringify(bookings)
    );

    // Lưu thông tin lịch khám gần nhất.
    localStorage.setItem(
        "medicareLatestBooking",
        JSON.stringify(booking)
    );

    // Hiển thị kết quả đặt lịch.
    bookingCode.textContent = booking.code;
    successBox.classList.remove("hidden");

    bookingButton.disabled = true;
    bookingButton.textContent = "Đã đặt lịch";

    alert(
        "Đặt lịch thành công!\n" +
        "Mã lịch khám: " + booking.code
    );

    // Cập nhật trạng thái khung giờ.
    renderTimeSlots();

    // Giữ lại thông báo thành công.
    bookingCode.textContent = booking.code;
    successBox.classList.remove("hidden");

    bookingButton.disabled = true;
    bookingButton.textContent = "Đã đặt lịch";
}


/* ==========================================
   16. SỰ KIỆN
========================================== */

specialtySelect.addEventListener("change", updateDoctors);

doctorSelect.addEventListener("change", updateDoctorPreview);

dateInput.addEventListener("change", function () {
    clearSuccessMessage();

    const date = dateInput.value;

    if (date) {
        const day = Number(date.split("-")[2]);

        if (day < 1 || day > 19) {
            alert("Trong bản demo, vui lòng chọn ngày từ 1 đến 19.");

            dateInput.value = "";

            resetTimeSlots();
            updateSummary();

            return;
        }

        if (date < getTodayString()) {
            alert("Vui lòng chọn ngày hôm nay hoặc ngày trong tương lai.");

            dateInput.value = "";

            resetTimeSlots();
            updateSummary();

            return;
        }
    }

    renderTimeSlots();
    updateSummary();
});

bookingButton.addEventListener("click", handleBooking);


/* ==========================================
   17. CẬP NHẬT KHI TAB KHÁC ĐẶT LỊCH
========================================== */

window.addEventListener("storage", function (event) {
    if (event.key === "medicareBookedSlots") {
        if (dateInput.value && doctorSelect.value) {
            renderTimeSlots();
        }
    }
});


/* ==========================================
   18. NHẬN DỮ LIỆU TỪ TRANG BÁC SĨ
========================================== */

const selectedSpecialty = localStorage.getItem("selectedSpecialty");
const selectedDoctor = localStorage.getItem("selectedDoctor");

if (
    selectedSpecialty &&
    doctorsBySpecialty[selectedSpecialty]
) {
    specialtySelect.value = selectedSpecialty;

    updateDoctors();

    if (selectedDoctor) {
        doctorSelect.value = selectedDoctor;
        updateDoctorPreview();
    }

    localStorage.removeItem("selectedSpecialty");
    localStorage.removeItem("selectedDoctor");
    localStorage.removeItem("selectedRoom");
}


/* ==========================================
   19. KHỞI TẠO
========================================== */

doctorSelect.disabled = true;
updateSummary();
