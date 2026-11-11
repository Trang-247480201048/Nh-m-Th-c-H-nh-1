// =====================================================
// MEDICARE - JAVASCRIPT DÙNG CHUNG CHO CÁC TRANG ADMIN
// =====================================================

const API_URL = "http://127.0.0.1:5000/api";

// =====================================================
// 1. HÀM HIỂN THỊ THÔNG BÁO
// =====================================================

const toast = document.getElementById("toast");
let toastTimer;

function showToast(message) {
    if (!toast) {
        console.log(message);
        return;
    }

    toast.textContent = message;
    toast.classList.add("show");

    clearTimeout(toastTimer);

    toastTimer = setTimeout(() => {
        toast.classList.remove("show");
    }, 2600);
}

// =====================================================
// 2. BIỂU ĐỒ TRANG TỔNG QUAN (chỉ chạy khi trang có biểu đồ)
// =====================================================

const chartCanvas = document.getElementById("appointmentChart");

if (chartCanvas && window.Chart) {
    new Chart(chartCanvas, {
        type: "bar",
        data: {
            labels: ["14/10", "15/10", "16/10", "17/10", "18/10", "19/10", "20/10"],
            datasets: [
                {
                    label: "Đã đặt",
                    data: [82, 108, 96, 132, 115, 116, 134],
                    backgroundColor: "#0f8f80",
                    borderRadius: 3
                },
                {
                    label: "Hoàn tất",
                    data: [62, 86, 75, 106, 91, 94, 31],
                    backgroundColor: "#b9deda",
                    borderRadius: 3
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: {
                x: { grid: { display: false } },
                y: { beginAtZero: true }
            }
        }
    });
}

// =====================================================
// 3. HÀM ĐỊNH DẠNG DỮ LIỆU
// =====================================================

function escapeHTML(value) {
    return String(value ?? "").replace(/[&<>"']/g, char => {
        const entities = {
            "&": "&amp;",
            "<": "&lt;",
            ">": "&gt;",
            '"': "&quot;",
            "'": "&#039;"
        };

        return entities[char];
    });
}

function formatDate(value) {
    if (!value) return "-";

    const date = new Date(value);

    if (isNaN(date.getTime())) {
        return String(value);
    }

    return date.toLocaleDateString("vi-VN");
}

function normalizeText(value) {
    return String(value ?? "").toLocaleLowerCase("vi");
}

// =====================================================
// 4. QUẢN LÝ BỆNH NHÂN - LẤY DỮ LIỆU TỪ BACKEND
// =====================================================

let patientData = [];

const patientTableBody = document.querySelector("#appointmentTable tbody");
const searchInput = document.getElementById("searchInput");
const statusFilter = document.getElementById("statusFilter");
const emptyState = document.getElementById("emptyState");
const patientSummary = document.getElementById("patientSummary");

async function loadPatients() {
    // Chỉ chạy ở trang có bảng bệnh nhân
    if (!patientTableBody) return;

    patientTableBody.innerHTML = `
        <tr>
            <td colspan="6" class="table-empty">
                Đang tải dữ liệu bệnh nhân...
            </td>
        </tr>
    `;

    try {
        const response = await fetch(`${API_URL}/benh-nhan`);

        if (!response.ok) {
            throw new Error("Không thể lấy danh sách bệnh nhân.");
        }

        const result = await response.json();

        if (result.status !== "success") {
            throw new Error(result.message || "Lỗi dữ liệu bệnh nhân.");
        }

        patientData = Array.isArray(result.data) ? result.data : [];

        renderPatients();
        updatePatientStatistics();

    } catch (error) {
        console.error("Lỗi tải bệnh nhân:", error);

        patientTableBody.innerHTML = `
            <tr>
                <td colspan="6" class="table-empty">
                    Không thể tải dữ liệu bệnh nhân.
                    Vui lòng kiểm tra backend và API.
                </td>
            </tr>
        `;

        if (patientSummary) {
            patientSummary.textContent = "Không tải được danh sách bệnh nhân.";
        }

        showToast("Không thể kết nối API bệnh nhân.");
    }
}

// =====================================================
// 5. HIỂN THỊ DANH SÁCH BỆNH NHÂN
// =====================================================

function renderPatients() {
    if (!patientTableBody) return;

    const keyword = normalizeText(searchInput?.value);
    const selectedStatus = statusFilter?.value || "";

    const filteredPatients = patientData.filter(patient => {
        const name = normalizeText(patient.ho_ten);
        const code = normalizeText(patient.ma_benh_nhan);
        const phone = normalizeText(patient.so_dien_thoai);

        const matchesKeyword =
            name.includes(keyword) ||
            code.includes(keyword) ||
            phone.includes(keyword);

        const matchesStatus =
            !selectedStatus || patient.trang_thai === selectedStatus;

        return matchesKeyword && matchesStatus;
    });

    if (filteredPatients.length === 0) {
        patientTableBody.innerHTML = "";
        if (emptyState) emptyState.hidden = false;
    } else {
        if (emptyState) emptyState.hidden = true;

        patientTableBody.innerHTML = filteredPatients.map(patient => {
            const name = escapeHTML(patient.ho_ten || "Chưa có tên");
            const code = escapeHTML(patient.ma_benh_nhan || "Chưa có mã");
            const phone = escapeHTML(patient.so_dien_thoai || "-");

            const age = patient.tuoi !== null && patient.tuoi !== undefined
                ? `${escapeHTML(patient.tuoi)} tuổi`
                : "Chưa cập nhật tuổi";

            const lastVisit = formatDate(patient.lan_kham_gan_nhat);
            const visitCount = Number(patient.so_luot_kham || 0);
            const status = patient.trang_thai || "Đang hoạt động";
            const statusClass = status === "Đã khóa" ? "cancelled" : "confirmed";

            // Vị trí thật của bệnh nhân trong patientData (không đổi khi lọc/tìm kiếm)
            const index = patientData.indexOf(patient);

            return `
                <tr>
                    <td>
                        <strong class="doctor-name">${name}</strong>
                        <small class="subline">${code} · ${age}</small>
                    </td>

                    <td>${phone}</td>
                    <td class="time-cell">${lastVisit}</td>
                    <td>${visitCount}</td>

                    <td>
                        <span class="status-pill ${statusClass}">
                            <i></i>${escapeHTML(status)}
                        </span>
                    </td>

                    <td>
                        <button class="btn-detail" type="button"
                                data-patient-index="${index}">
                            Xem chi tiết
                        </button>
                    </td>
                </tr>
            `;
        }).join("");
    }

    const summary =
        `Hiển thị ${filteredPatients.length} trong tổng số ${patientData.length} bệnh nhân.`;

    if (patientSummary) {
        patientSummary.textContent = summary;
    }

    const footer = document.getElementById("patientFooter");

    if (footer) {
        footer.textContent = summary;
    }
}

// =====================================================
// 6. TÌM KIẾM VÀ LỌC BỆNH NHÂN
// =====================================================

if (searchInput) {
    searchInput.addEventListener("input", renderPatients);
}

if (statusFilter) {
    statusFilter.addEventListener("change", renderPatients);
}

// =====================================================
// 7. CẬP NHẬT THỐNG KÊ BỆNH NHÂN
// =====================================================

function updatePatientStatistics() {
    const totalElement = document.getElementById("statTotal");

    if (totalElement) {
        totalElement.textContent = patientData.length.toLocaleString("vi-VN");
    }
}

// Lấy số lịch hẹn hôm nay từ API lịch hẹn
async function loadTodayAppointments() {
    const todayElement = document.getElementById("statToday");

    if (!todayElement) return;

    try {
        const response = await fetch(`${API_URL}/lich-hen`);

        if (!response.ok) {
            throw new Error("Không thể lấy lịch hẹn.");
        }

        const result = await response.json();

        const appointments = Array.isArray(result)
            ? result
            : (Array.isArray(result.data) ? result.data : []);

        const today = new Date();
        const todayString =
            `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, "0")}-${String(today.getDate()).padStart(2, "0")}`;

        const count = appointments.filter(item => {
            const appointmentDate = item.ngay_kham || item.NgayKham || "";
            return String(appointmentDate).slice(0, 10) === todayString;
        }).length;

        todayElement.textContent = count.toLocaleString("vi-VN");

    } catch (error) {
        console.error("Lỗi thống kê lịch hẹn:", error);
        todayElement.textContent = "—";
    }
}

// =====================================================
// 8. XEM CHI TIẾT BỆNH NHÂN (HỘP THOẠI)
// =====================================================

function setText(id, value) {
    const element = document.getElementById(id);

    if (element) {
        element.textContent = value;
    }
}

function openPatientDetail(patient) {
    const modal = document.getElementById("patientModal");

    if (!modal || !patient) return;

    const name = patient.ho_ten || "Chưa có thông tin";
    const code = patient.ma_benh_nhan || "-";
    const phone = patient.so_dien_thoai || "-";
    const email = patient.email || "-";
    const birthday = patient.ngay_sinh ? formatDate(patient.ngay_sinh) : "-";
    const age = patient.tuoi != null ? patient.tuoi + " tuổi" : "Chưa cập nhật";
    const visits = patient.so_luot_kham ?? 0;
    const lastVisit = patient.lan_kham_gan_nhat
        ? formatDate(patient.lan_kham_gan_nhat)
        : "Chưa có lịch khám";
    const status = patient.trang_thai || "Đang hoạt động";

    setText(
        "detailAvatar",
        name.trim().split(/\s+/).slice(-2).map(w => w[0]).join("").toUpperCase()
    );

    setText("detailName", name);
    setText("detailCode", code);
    setText("detailPhone", phone);

    setText("detailVisits", visits);
    setText("detailLastVisit", lastVisit);
    setText("detailAge", age);

    setText("detailFullName", name);
    setText("detailFullCode", code);
    setText("detailFullPhone", phone);
    setText("detailEmail", email);
    setText("detailBirthday", birthday);

    setText("detailStatus", status);
    setText("detailFullStatus", status);
    setText("detailFullVisits", visits);
    setText("detailFullLastVisit", lastVisit);
    setText("detailFullAge", age);

    setText(
        "detailHistoryNote",
        `Bệnh nhân hiện có ${visits} lịch hẹn trong hệ thống.`
    );

    const statusPill = document.getElementById("detailStatus");

    if (statusPill) {
        statusPill.className =
            "status-pill " + (status === "Đã khóa" ? "cancelled" : "confirmed");
    }

    modal.hidden = false;
    document.body.style.overflow = "hidden";
}

function closePatientDetail() {
    const modal = document.getElementById("patientModal");

    if (modal) {
        modal.hidden = true;
        document.body.style.overflow = "";
    }
}

// Bấm "Xem chi tiết" trong bảng
if (patientTableBody) {
    patientTableBody.addEventListener("click", event => {
        const button = event.target.closest("[data-patient-index]");

        if (!button) return;

        const patient = patientData[Number(button.dataset.patientIndex)];

        if (!patient) {
            showToast("Không tìm thấy thông tin bệnh nhân.");
            return;
        }

        openPatientDetail(patient);
    });
}

// Nút đóng
document.getElementById("closePatientModal")
    ?.addEventListener("click", closePatientDetail);

// Bấm ra ngoài hộp để đóng
document.getElementById("patientModal")
    ?.addEventListener("click", function (event) {
        if (event.target === this) {
            closePatientDetail();
        }
    });

// Nhấn ESC để đóng
document.addEventListener("keydown", event => {
    if (event.key === "Escape") {
        closePatientDetail();
    }
});

// =====================================================
// 9. XUẤT DANH SÁCH BỆNH NHÂN RA CSV
// =====================================================

const exportBtn = document.getElementById("exportBtn");

if (exportBtn) {
    exportBtn.addEventListener("click", () => {
        if (patientData.length === 0) {
            showToast("Chưa có dữ liệu để xuất.");
            return;
        }

        const keyword = normalizeText(searchInput?.value);
        const selectedStatus = statusFilter?.value || "";

        const filteredPatients = patientData.filter(patient => {
            const matchesKeyword =
                normalizeText(patient.ho_ten).includes(keyword) ||
                normalizeText(patient.ma_benh_nhan).includes(keyword) ||
                normalizeText(patient.so_dien_thoai).includes(keyword);

            const matchesStatus =
                !selectedStatus || patient.trang_thai === selectedStatus;

            return matchesKeyword && matchesStatus;
        });

        const rows = [
            [
                "Mã bệnh nhân",
                "Họ tên",
                "Số điện thoại",
                "Email",
                "Ngày sinh",
                "Lần khám gần nhất",
                "Số lượt đặt khám",
                "Trạng thái"
            ],

            ...filteredPatients.map(patient => [
                patient.ma_benh_nhan || "",
                patient.ho_ten || "",
                patient.so_dien_thoai || "",
                patient.email || "",
                patient.ngay_sinh || "",
                patient.lan_kham_gan_nhat || "",
                patient.so_luot_kham || 0,
                patient.trang_thai || ""
            ])
        ];

        const csv = rows.map(row =>
            row.map(value =>
                `"${String(value).replace(/"/g, '""')}"`
            ).join(",")
        ).join("\n");

        const blob = new Blob(
            ["\ufeff" + csv],
            { type: "text/csv;charset=utf-8;" }
        );

        const link = document.createElement("a");
        const url = URL.createObjectURL(blob);

        link.href = url;
        link.download = "danh-sach-benh-nhan-medicare.csv";
        link.click();

        URL.revokeObjectURL(url);

        showToast("Đã xuất danh sách bệnh nhân.");
    });
}

// Nút "Thêm bệnh nhân" (chưa nối chức năng)
document.getElementById("addPatientBtn")
    ?.addEventListener("click", () => {
        alert("Chức năng thêm bệnh nhân sẽ được bổ sung sau.");
    });

// =====================================================
// 10. CÁC CHỨC NĂNG DÙNG Ở TRANG KHÁC
// =====================================================

// Nút ngày
const dateBtn = document.getElementById("dateBtn");

if (dateBtn) {
    dateBtn.addEventListener("click", () => {
        showToast("Đang hiển thị dữ liệu theo ngày hôm nay.");
    });
}

// Nút thông báo
const notificationBtn = document.getElementById("notificationBtn");

if (notificationBtn) {
    notificationBtn.addEventListener("click", () => {
        showToast("Bạn có thông báo mới từ hệ thống MediCare.");
    });
}

// Xem tất cả lịch hẹn
const allAppointments = document.getElementById("allAppointments");

if (allAppointments) {
    allAppointments.addEventListener("click", event => {
        event.preventDefault();
        showToast("Đang mở danh sách lịch hẹn.");
    });
}

// Xác nhận lịch hẹn
document.addEventListener("click", async event => {
    const button = event.target.closest("[data-confirm]");

    if (!button) return;

    const code = button.dataset.confirm;

    try {
        const response = await fetch(
            `/api/appointments/${encodeURIComponent(code)}/confirm`,
            { method: "POST" }
        );

        const result = await response.json();

        if (!response.ok || !result.success) {
            throw new Error(result.message || "Không thể xác nhận.");
        }

        showToast(`Đã xác nhận lịch hẹn ${code}.`);

    } catch (error) {
        console.error(error);
        showToast("Không thể xác nhận lịch hẹn.");
    }
});

// =====================================================
// 11. MENU TRÊN ĐIỆN THOẠI
// =====================================================

const mobileMenu = document.getElementById("mobileMenu");
const sidebar = document.getElementById("sidebar");

if (mobileMenu && sidebar) {
    mobileMenu.addEventListener("click", () => {
        sidebar.classList.toggle("open");
    });
}

// =====================================================
// 12. KHỞI CHẠY CÁC CHỨC NĂNG
// =====================================================

loadPatients();
loadTodayAppointments();