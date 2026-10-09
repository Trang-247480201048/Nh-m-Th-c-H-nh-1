
// ================================
// XỬ LÝ TRANG ĐĂNG NHẬP MEDICARE
// ================================

const loginForm = document.getElementById("loginForm");
const usernameInput = document.getElementById("username");
const passwordInput = document.getElementById("password");

const usernameError = document.getElementById("usernameError");
const passwordError = document.getElementById("passwordError");
const loginMessage = document.getElementById("loginMessage");

const rememberCheckbox = document.getElementById("remember");
const forgotPassword = document.getElementById("forgotPassword");

// Kiểm tra định dạng email
function isValidEmail(value) {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value);
}

// Kiểm tra định dạng số điện thoại Việt Nam
function isValidPhone(value) {
    return /^(0|\+84)(3|5|7|8|9)[0-9]{8}$/.test(value);
}

// Hiển thị thông báo chung
function showMessage(message, type) {
    loginMessage.textContent = message;
    loginMessage.className = "login-message " + type;
}

// Xóa thông báo lỗi
function clearErrors() {
    usernameError.textContent = "";
    passwordError.textContent = "";

    usernameInput.style.borderColor = "";
    passwordInput.style.borderColor = "";

    loginMessage.textContent = "";
    loginMessage.className = "login-message";
}

// Hiển thị lỗi bên dưới ô nhập
function showFieldError(input, errorElement, message) {
    errorElement.textContent = message;
    input.style.borderColor = "#d32f2f";
}

// Xử lý đăng nhập
loginForm.addEventListener("submit", function (event) {
    event.preventDefault();

    clearErrors();

    const username = usernameInput.value.trim();
    const password = passwordInput.value;

    let hasError = false;

    // Kiểm tra tài khoản
    if (username === "") {
        showFieldError(
            usernameInput,
            usernameError,
            "Vui lòng nhập số điện thoại hoặc email."
        );
        hasError = true;
    } else if (!isValidEmail(username) && !isValidPhone(username)) {
        showFieldError(
            usernameInput,
            usernameError,
            "Email hoặc số điện thoại chưa đúng định dạng."
        );
        hasError = true;
    }

    // Kiểm tra mật khẩu
    if (password.trim() === "") {
        showFieldError(
            passwordInput,
            passwordError,
            "Vui lòng nhập mật khẩu."
        );
        hasError = true;
    }

    // Nếu có lỗi thì không chuyển trang
    if (hasError) {
        return;
    }

    // MÔ PHỎNG ĐĂNG NHẬP THÀNH CÔNG
    // Chưa xác thực tài khoản bằng cơ sở dữ liệu

    const loginInfo = {
        username: username,
        isLoggedIn: true
    };

    // Lưu trạng thái đăng nhập để demo
    try {
        if (rememberCheckbox.checked) {
            localStorage.setItem(
                "medicareLogin",
                JSON.stringify(loginInfo)
            );
        } else {
            sessionStorage.setItem(
                "medicareLogin",
                JSON.stringify(loginInfo)
            );
        }
    } catch (error) {
        console.warn("Không thể lưu trạng thái đăng nhập:", error);
    }

    showMessage(
        "Đăng nhập thành công! Đang chuyển đến trang đặt lịch khám...",
        "success"
    );

    // Chuyển sang trang đặt lịch khám
    setTimeout(function () {
        window.location.href = "dat-lich.html";
    }, 800);
});

// Xóa lỗi khi người dùng nhập lại
usernameInput.addEventListener("input", function () {
    usernameError.textContent = "";
    usernameInput.style.borderColor = "";
});

passwordInput.addEventListener("input", function () {
    passwordError.textContent = "";
    passwordInput.style.borderColor = "";
});

// Xử lý quên mật khẩu
forgotPassword.addEventListener("click", function (event) {
    event.preventDefault();

    clearErrors();

    const username = usernameInput.value.trim();

    if (username === "") {
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
        "Chức năng khôi phục mật khẩu chưa được triển khai. Vui lòng liên hệ bộ phận hỗ trợ MediCare.",
        "error"
    );
});

