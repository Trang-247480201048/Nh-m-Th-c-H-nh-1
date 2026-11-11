
document.addEventListener("DOMContentLoaded", function () {
    const API_BASE = "http://127.0.0.1:5000/api";

    const loginForm = document.getElementById("loginForm");
    const usernameInput = document.getElementById("username");
    const passwordInput = document.getElementById("password");

    const usernameError = document.getElementById("usernameError");
    const passwordError = document.getElementById("passwordError");
    const loginMessage = document.getElementById("loginMessage");

    const rememberCheckbox = document.getElementById("remember");
    const forgotPassword = document.getElementById("forgotPassword");

    function isValidEmail(value) {
        return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value);
    }

    function isValidPhone(value) {
        return /^(0[0-9]{9,10}|\+84[0-9]{9,10})$/.test(
            value.replace(/\s/g, "")
        );
    }

    function showMessage(text, type) {
        loginMessage.textContent = text;
        loginMessage.className = "login-message " + type;
    }

    function clearErrors() {
        usernameError.textContent = "";
        passwordError.textContent = "";

        usernameInput.style.borderColor = "";
        passwordInput.style.borderColor = "";

        loginMessage.textContent = "";
        loginMessage.className = "login-message";
    }

    function showFieldError(input, errorElement, text) {
        errorElement.textContent = text;
        input.style.borderColor = "#d32f2f";
    }

    loginForm.addEventListener("submit", async function (event) {
        event.preventDefault();
        clearErrors();

        const username = usernameInput.value.trim();
        const password = passwordInput.value;
        const normalizedPhone = username.replace(/\s/g, "");

        let hasError = false;

        if (!username) {
            showFieldError(
                usernameInput,
                usernameError,
                "Vui lòng nhập số điện thoại hoặc email."
            );
            hasError = true;
        } else if (
            !isValidEmail(username) &&
            !isValidPhone(username)
        ) {
            showFieldError(
                usernameInput,
                usernameError,
                "Email hoặc số điện thoại chưa đúng định dạng."
            );
            hasError = true;
        }

        if (!password.trim()) {
            showFieldError(
                passwordInput,
                passwordError,
                "Vui lòng nhập mật khẩu."
            );
            hasError = true;
        }

        if (hasError) return;

        const submitButton =
            loginForm.querySelector('[type="submit"]');

        if (submitButton) submitButton.disabled = true;

        try {
            const response = await fetch(
                `${API_BASE}/auth/login`,
                {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    credentials: "include",
                    body: JSON.stringify({
                        username: isValidEmail(username)
                            ? username.toLowerCase()
                            : normalizedPhone,
                        password: password
                    })
                }
            );

            let result;

            try {
                result = await response.json();
            } catch (error) {
                throw new Error("Backend không trả về JSON hợp lệ.");
            }

            if (!response.ok || !result.success) {
                showMessage(
                    result.message || "Đăng nhập không thành công.",
                    "error"
                );
                return;
            }

            // Lấy thông tin do backend trả về.
            const user = result.user || {};

            const patient = {
                phone: user.phone || normalizedPhone,
                fullname:
                    user.fullname ||
                    user.full_name ||
                    user.name ||
                    "",
                username: username
            };

            /*
             * Đồng bộ khóa đăng nhập cho trang chủ và các trang khác.
             * Không thay đổi API hoặc dữ liệu trong SQL Server.
             */
            localStorage.setItem("medicareLoggedIn", "true");
            localStorage.setItem(
                "medicareUser",
                JSON.stringify(patient)
            );
            localStorage.setItem(
                "medicareLogin",
                JSON.stringify(patient)
            );

            // Chỉ dùng để điền lại tên đăng nhập khi người dùng chọn ghi nhớ.
            if (rememberCheckbox && rememberCheckbox.checked) {
                localStorage.setItem(
                    "medicareRememberedLogin",
                    JSON.stringify({
                        username: username
                    })
                );
            } else {
                localStorage.removeItem("medicareRememberedLogin");
            }

            showMessage(
                "Đăng nhập thành công! Đang chuyển đến trang chủ...",
                "success"
            );

            setTimeout(function () {
                window.location.href = "trang-chu.html";
            }, 800);

        } catch (error) {
            console.error("Lỗi đăng nhập:", error);

            showMessage(
                error.message ||
                "Không thể kết nối backend. Hãy kiểm tra Flask và kết nối mạng.",
                "error"
            );
        } finally {
            if (submitButton) submitButton.disabled = false;
        }
    });

    usernameInput.addEventListener("input", function () {
        usernameError.textContent = "";
        usernameInput.style.borderColor = "";
    });

    passwordInput.addEventListener("input", function () {
        passwordError.textContent = "";
        passwordInput.style.borderColor = "";
    });

    if (forgotPassword) {
        forgotPassword.addEventListener("click", function (event) {
            event.preventDefault();
            clearErrors();

            const username = usernameInput.value.trim();

            if (!username) {
                showMessage(
                    "Vui lòng nhập email hoặc số điện thoại trước.",
                    "error"
                );
                usernameInput.focus();
                return;
            }

            if (!isValidEmail(username) && !isValidPhone(username)) {
                showMessage(
                    "Email hoặc số điện thoại chưa đúng định dạng.",
                    "error"
                );
                usernameInput.focus();
                return;
            }

            showMessage(
                "Chức năng khôi phục mật khẩu chưa được triển khai.",
                "error"
            );
        });
    }
});
