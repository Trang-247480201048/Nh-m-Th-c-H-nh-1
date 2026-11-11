document.addEventListener("DOMContentLoaded", function () {

    /* =========================
       1. NÚT ĐẶT LỊCH KHÁM
    ========================= */

    const bookingButtons = document.querySelectorAll(
        ".hero-actions a, .booking-btn, .specialty-card a"
    );

    bookingButtons.forEach(function (button) {
        const text = button.textContent.trim().toLowerCase();

        if (text.includes("đặt lịch") || text.includes("khám ngay")) {
            button.addEventListener("click", function (event) {
                const href = button.getAttribute("href");

                if (!href || href === "#") {
                    event.preventDefault();
                    window.location.href = "dat-lich.html";
                }
            });
        }
    });


    /* =========================
       2. NÚT XEM BÁC SĨ
    ========================= */

    const doctorButtons = document.querySelectorAll(
        ".hero-actions a, .doctor-btn"
    );

    doctorButtons.forEach(function (button) {
        const text = button.textContent.trim().toLowerCase();

        if (text.includes("bác sĩ")) {
            button.addEventListener("click", function (event) {
                const href = button.getAttribute("href");

                if (!href || href === "#") {
                    event.preventDefault();
                    window.location.href = "bac-si.html";
                }
            });
        }
    });


    /* =========================
       3. CHỌN CHUYÊN KHOA
    ========================= */

    const specialtyCards = document.querySelectorAll(".specialty-card");

    specialtyCards.forEach(function (card) {
        card.style.cursor = "pointer";

        card.addEventListener("click", function (event) {

            // Nếu người dùng nhấn vào liên kết bên trong thẻ,
            // không xử lý chuyển trang hai lần.
            if (event.target.closest("a")) {
                return;
            }

            const title = card.querySelector(
                "h3, h2, .specialty-name"
            );

            if (title) {
                localStorage.setItem(
                    "selectedSpecialty",
                    title.textContent.trim()
                );
            }

            window.location.href = "dat-lich.html";
        });
    });


    /* =========================
       4. LẤY THÔNG TIN BỆNH NHÂN
    ========================= */

    const authButtons = document.querySelector(".auth-buttons");

    function getPatientAccount() {

        if (localStorage.getItem("medicareLoggedIn") !== "true") {
            return null;
        }

        // Các khóa lưu thông tin tài khoản.
        const possibleKeys = [
            "medicareUser",
            "medicareLogin",
            "medicareUserInfo",
            "medicarePatient",
            "currentUser",
            "user"
        ];

        for (const key of possibleKeys) {

            const savedData = localStorage.getItem(key);

            if (!savedData) {
                continue;
            }

            try {
                const parsed = JSON.parse(savedData);

                if (!parsed || typeof parsed !== "object") {
                    continue;
                }

                // Một số hệ thống lưu thông tin trong thuộc tính user.
                const userData =
                    parsed.user && typeof parsed.user === "object"
                        ? parsed.user
                        : parsed;

                const name =
                    userData.fullname ||
                    userData.full_name ||
                    userData.fullName ||
                    userData.ho_ten ||
                    userData.hoTen ||
                    userData.name ||
                    "";

                const phone =
                    userData.phone ||
                    userData.so_dien_thoai ||
                    userData.soDienThoai ||
                    "";

                if (String(name).trim()) {
                    return {
                        name: String(name).trim(),
                        phone: String(phone).trim()
                    };
                }

            } catch (error) {
                // Bỏ qua dữ liệu không đúng định dạng JSON.
            }
        }

        return null;
    }


    /* =========================
       5. TẠO CHỮ VIẾT TẮT AVATAR
    ========================= */

    function getInitials(name) {

        const words = name.trim().split(/\s+/);

        if (words.length === 1) {
            return words[0].substring(0, 2).toUpperCase();
        }

        // Ví dụ: Nguyễn Nhật Linh -> NL.
        return (
            words[0].charAt(0) +
            words[words.length - 1].charAt(0)
        ).toUpperCase();
    }


    /* =========================
       6. TRÁNH CHÈN HTML TỪ DỮ LIỆU NGƯỜI DÙNG
    ========================= */

    function escapeHTML(value) {

        const element = document.createElement("span");

        element.textContent = String(value);

        return element.innerHTML;
    }


    /* =========================
       7. HIỂN THỊ TÀI KHOẢN TRÊN HEADER
    ========================= */

    function renderAccount() {

        if (!authButtons) {
            return;
        }

        const patient = getPatientAccount();

        // Trường hợp chưa đăng nhập hoặc chưa có tên.
        if (!patient) {

            authButtons.innerHTML = `
                <a href="dang-nhap.html" class="login-btn">
                    Đăng nhập
                </a>

                <a href="dang-ky.html" class="register-btn">
                    Đăng ký
                </a>
            `;

            return;
        }

        const initials = getInitials(patient.name);

        // ĐÃ SỬA: Thêm dấu đóng backtick (`) và dấu ngoặc nhọn kết thúc chuỗi HTML ở đây
        authButtons.innerHTML = `
            <div class="patient-account" id="patientAccount">

                <button
                    type="button"
                    class="patient-account-toggle"
                    id="patientAccountToggle"
                    aria-expanded="false"
                    aria-controls="patientDropdown"
                >
                    <span class="patient-avatar">
                        ${escapeHTML(initials)}
                    </span>

                    <span class="patient-account-info">
                        <span class="patient-account-name">
                            ${escapeHTML(patient.name)}
                        </span>

                    </span>

                </button>

                <div
                    class="patient-dropdown hidden"
                    id="patientDropdown"
                >
                    <a href="ho-so.html">
                        Thông tin hồ sơ
                    </a>

                    <a href="lich-su-kham.html">
                        Lịch sử khám bệnh
                    </a>

                    <button type="button" id="patientLogout">
                        Đăng xuất
                    </button>
                </div>

            </div>
        `; 

        const toggle = document.getElementById(
            "patientAccountToggle"
        );

        const dropdown = document.getElementById(
            "patientDropdown"
        );

        const account = document.getElementById(
            "patientAccount"
        );

        const logoutButton = document.getElementById(
            "patientLogout"
        );


        // Mở hoặc đóng menu tài khoản.
        toggle.addEventListener("click", function () {

            const isOpen = !dropdown.classList.contains("hidden");

            dropdown.classList.toggle("hidden", isOpen);

            toggle.setAttribute(
                "aria-expanded",
                String(!isOpen)
            );
        });


        // Nhấn ra ngoài thì đóng menu.
        document.addEventListener("click", function (event) {

            if (account && !account.contains(event.target)) {

                dropdown.classList.add("hidden");

                toggle.setAttribute("aria-expanded", "false");
            }
        });


        /* =========================
           8. ĐĂNG XUẤT
        ========================= */

        logoutButton.addEventListener("click", function () {

            const confirmed = confirm(
                "Bạn có chắc chắn muốn đăng xuất?"
            );

            if (!confirmed) {
                return;
            }

            // Xóa trạng thái đăng nhập.
            localStorage.removeItem("medicareLoggedIn");

            // Xóa các khóa thông tin tài khoản.
            [
                "medicareUser",
                "medicareLogin",
                "medicareUserInfo",
                "medicarePatient",
                "currentUser",
                "user"
            ].forEach(function (key) {
                localStorage.removeItem(key);
            });

            // Không xóa lịch sử đặt khám hoặc lịch mới nhất.
            window.location.href = "trang-chu.html";
        });
    }


    /* =========================
       9. KHỞI TẠO
    ========================= */

    renderAccount();

});