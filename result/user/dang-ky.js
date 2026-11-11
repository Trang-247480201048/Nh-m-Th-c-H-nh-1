
document.addEventListener("DOMContentLoaded", function () {
    const API_BASE = "http://127.0.0.1:5000/api";

    const form = document.getElementById("registerForm");
    const fullname = document.getElementById("fullname");
    const birthday = document.getElementById("birthday");
    const phone = document.getElementById("phone");
    const email = document.getElementById("email");
    const password = document.getElementById("password");
    const confirmPassword = document.getElementById("confirmPassword");
    const terms = document.getElementById("terms");
    const message = document.getElementById("registerMessage");

    function clearErrors() {
        [
            "fullnameError",
            "birthdayError",
            "phoneError",
            "emailError",
            "passwordError",
            "confirmPasswordError",
            "termsError"
        ].forEach(function (id) {
            const element = document.getElementById(id);
            if (element) element.textContent = "";
        });

        message.className = "register-message";
        message.textContent = "";
    }

    function showMessage(text, type) {
        message.className = "register-message " + type;
        message.textContent = text;
    }

    function showError(id, text) {
        const element = document.getElementById(id);
        if (element) element.textContent = text;
    }

    form.addEventListener("submit", async function (event) {
        event.preventDefault();
        clearErrors();

        let valid = true;

        const fullNameValue = fullname.value.trim();
        const birthdayValue = birthday.value;
        const phoneValue = phone.value.replace(/\s/g, "");
        const emailValue = email.value.trim().toLowerCase();
        const passwordValue = password.value;

        function isValidEmail(value) {
        return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value);
    }

function isValidPhone(value) {
    return /^(0[0-9]{9,10}|\+84[0-9]{9,10})$/.test(
        value.replace(/\s/g, "")
    );
}
        if (!fullNameValue) {
            showError("fullnameError", "Vui lòng nhập họ và tên.");
            valid = false;
        }

        if (!birthdayValue) {
            showError("birthdayError", "Vui lòng chọn ngày sinh.");
            valid = false;
        } else if (birthdayValue > new Date().toISOString().slice(0, 10)) {
            showError("birthdayError", "Ngày sinh không được ở tương lai.");
            valid = false;
        }

        if (!phoneValue) {
            showError("phoneError", "Vui lòng nhập số điện thoại.");
            valid = false;
        } else if (!phoneRegex.test(phoneValue)) {
            showError("phoneError", "Số điện thoại không hợp lệ.");
            valid = false;
        }

        if (!emailValue) {
            showError("emailError", "Vui lòng nhập email.");
            valid = false;
        } else if (!emailRegex.test(emailValue)) {
            showError("emailError", "Email không hợp lệ.");
            valid = false;
        }

        if (passwordValue.length < 8) {
            showError("passwordError", "Mật khẩu phải có ít nhất 8 ký tự.");
            valid = false;
        }

        if (confirmPassword.value !== passwordValue) {
            showError(
                "confirmPasswordError",
                "Mật khẩu nhập lại không khớp."
            );
            valid = false;
        }

        if (!terms.checked) {
            showError(
                "termsError",
                "Vui lòng đồng ý với điều khoản sử dụng."
            );
            valid = false;
        }

        if (!valid) return;

        const submitButton = form.querySelector('[type="submit"]');
        if (submitButton) submitButton.disabled = true;

        try {
            const response = await fetch(`${API_BASE}/auth/register`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                credentials: "include",
                body: JSON.stringify({
                    fullname: fullNameValue,
                    birthday: birthdayValue,
                    phone: phoneValue,
                    email: emailValue,
                    password: passwordValue
                })
            });

            const result = await response.json();

            if (!response.ok || !result.success) {
                showMessage(
                    result.message || "Đăng ký không thành công.",
                    "error"
                );
                return;
            }

            // Không lưu mật khẩu vào localStorage.
            showMessage(
                "Đăng ký tài khoản thành công! Đang chuyển đến trang đăng nhập...",
                "success"
            );

            form.reset();

            setTimeout(function () {
                window.location.href = "dang-nhap.html";
            }, 1200);

        } catch (error) {
            console.error("Lỗi đăng ký:", error);
            showMessage(
                "Không thể kết nối backend. Hãy kiểm tra Flask và kết nối mạng.",
                "error"
            );
        } finally {
            if (submitButton) submitButton.disabled = false;
        }
    });

    const termsLink = document.getElementById("termsLink");

    if (termsLink) {
        termsLink.addEventListener("click", function (event) {
            event.preventDefault();

            alert(
                "Điều khoản sử dụng MediCare sẽ được hoàn thiện trong phiên bản chính thức."
            );
        });
    }
});
