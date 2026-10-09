document.addEventListener("DOMContentLoaded", function () {

    const form = document.getElementById("registerForm");

    const fullname = document.getElementById("fullname");
    const birthday = document.getElementById("birthday");
    const phone = document.getElementById("phone");
    const email = document.getElementById("email");
    const password = document.getElementById("password");
    const confirmPassword =
        document.getElementById("confirmPassword");

    const terms = document.getElementById("terms");

    const message =
        document.getElementById("registerMessage");


    function clearErrors() {

        document.querySelectorAll(
            ".register-card small"
        ).forEach(function (element) {

            element.textContent = "";

        });

        message.className =
            "register-message";

        message.textContent = "";
    }


    form.addEventListener("submit", function (event) {

        event.preventDefault();

        clearErrors();

        let valid = true;


        if (fullname.value.trim() === "") {

            document.getElementById(
                "fullnameError"
            ).textContent =
                "Vui lòng nhập họ và tên.";

            valid = false;
        }


        if (birthday.value === "") {

            document.getElementById(
                "birthdayError"
            ).textContent =
                "Vui lòng chọn ngày sinh.";

            valid = false;
        }


        const phoneRegex =
            /^(0|\+84)[0-9]{9,10}$/;

        const cleanPhone =
            phone.value.replace(/\s/g, "");


        if (cleanPhone === "") {

            document.getElementById(
                "phoneError"
            ).textContent =
                "Vui lòng nhập số điện thoại.";

            valid = false;

        } else if (!phoneRegex.test(cleanPhone)) {

            document.getElementById(
                "phoneError"
            ).textContent =
                "Số điện thoại không hợp lệ.";

            valid = false;
        }


        const emailRegex =
            /^[^\s@]+@[^\s@]+\.[^\s@]+$/;


        if (email.value.trim() === "") {

            document.getElementById(
                "emailError"
            ).textContent =
                "Vui lòng nhập email.";

            valid = false;

        } else if (
            !emailRegex.test(email.value.trim())
        ) {

            document.getElementById(
                "emailError"
            ).textContent =
                "Email không hợp lệ.";

            valid = false;
        }


        if (password.value.length < 6) {

            document.getElementById(
                "passwordError"
            ).textContent =
                "Mật khẩu phải có ít nhất 6 ký tự.";

            valid = false;
        }


        if (
            confirmPassword.value !==
            password.value
        ) {

            document.getElementById(
                "confirmPasswordError"
            ).textContent =
                "Mật khẩu nhập lại không khớp.";

            valid = false;
        }


        if (!terms.checked) {

            document.getElementById(
                "termsError"
            ).textContent =
                "Vui lòng đồng ý với điều khoản sử dụng.";

            valid = false;
        }


        if (!valid) {
            return;
        }


        /*
            LƯU TÀI KHOẢN DEMO
        */

        const user = {

            fullname:
                fullname.value.trim(),

            birthday:
                birthday.value,

            phone:
                cleanPhone,

            email:
                email.value.trim(),

            password:
                password.value

        };


        localStorage.setItem(
            "medicareUser",
            JSON.stringify(user)
        );


        message.className =
            "register-message success";

        message.textContent =
            "Đăng ký tài khoản thành công!";


        setTimeout(function () {

            window.location.href =
                "dang-nhap.html";

        }, 1200);

    });


    document
        .getElementById("termsLink")
        .addEventListener("click", function (event) {

            event.preventDefault();

            alert(
                "Điều khoản sử dụng MediCare sẽ được hoàn thiện trong phiên bản chính thức."
            );

        });

});