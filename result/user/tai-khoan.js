
document.addEventListener("DOMContentLoaded", function () {
    const authButtons = document.querySelector(".auth-buttons");

    if (!authButtons) return;

    // Lấy thông tin người dùng đã đăng nhập.
    function getPatient() {
        if (localStorage.getItem("medicareLoggedIn") !== "true") {
            return null;
        }

        const keys = ["medicareUser", "medicareLogin"];

        for (const key of keys) {
            try {
                const data = JSON.parse(
                    localStorage.getItem(key) || "null"
                );

                if (!data) continue;

                const user = data.user || data;
                const name =
                    user.fullname ||
                    user.full_name ||
                    user.fullName ||
                    user.name ||
                    "";

                if (String(name).trim()) {
                    return { name: String(name).trim() };
                }
            } catch (error) {
                console.warn("Không đọc được thông tin:", key);
            }
        }

        return null;
    }

    // Tạo chữ viết tắt: Nguyễn Nhật Linh -> NL.
    function getInitials(name) {
        const words = name.trim().split(/\s+/);

        if (words.length === 1) {
            return words[0].slice(0, 2).toUpperCase();
        }

        return (
            words[0][0] +
            words[words.length - 1][0]
        ).toUpperCase();
    }

    // Hiển thị an toàn dữ liệu dạng chữ.
    function escapeHTML(value) {
        const span = document.createElement("span");
        span.textContent = value;
        return span.innerHTML;
    }

    function renderAccount() {
        const patient = getPatient();

        // Chưa đăng nhập.
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

        // Đã đăng nhập.
        authButtons.innerHTML = `
            <div class="patient-account" id="patientAccount">
                <button
                    type="button"
                    class="patient-account-toggle"
                    id="patientAccountToggle"
                    aria-expanded="false"
                >
                    <span class="patient-avatar">
                        ${escapeHTML(getInitials(patient.name))}
                    </span>

                    <span class="patient-account-info">
                        <span class="patient-account-name">
                            ${escapeHTML(patient.name)}
                        </span>
                    </span>

                    
                </button>

                <div class="patient-dropdown hidden" id="patientDropdown">
                    <a href="ho-so.html">Thông tin hồ sơ</a>
                    <a href="lich-su-kham.html">Lịch sử khám bệnh</a>
                    <button type="button" id="patientLogout">
                        Đăng xuất
                    </button>
                </div>
            </div>
        `;

        const toggle = document.getElementById("patientAccountToggle");
        const dropdown = document.getElementById("patientDropdown");
        const account = document.getElementById("patientAccount");
        const logout = document.getElementById("patientLogout");

        // Đóng/mở menu.
        toggle.addEventListener("click", function () {
            const shouldOpen = dropdown.classList.contains("hidden");

            dropdown.classList.toggle("hidden", !shouldOpen);
            toggle.setAttribute("aria-expanded", String(shouldOpen));
        });

        // Nhấn bên ngoài để đóng menu.
        document.addEventListener("click", function (event) {
            if (!account.contains(event.target)) {
                dropdown.classList.add("hidden");
                toggle.setAttribute("aria-expanded", "false");
            }
        });

        // Đăng xuất.
        logout.addEventListener("click", function () {
            if (!confirm("Bạn có chắc chắn muốn đăng xuất?")) {
                return;
            }

            [
                "medicareLoggedIn",
                "medicareUser",
                "medicareLogin",
                "medicareUserInfo",
                "medicarePatient",
                "currentUser",
                "user"
            ].forEach(function (key) {
                localStorage.removeItem(key);
            });

            // Giữ lại dữ liệu lịch sử khám.
            window.location.href = "trang-chu.html";
        });
    }

    renderAccount();
});
