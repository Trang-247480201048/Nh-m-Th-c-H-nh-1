document.addEventListener("DOMContentLoaded", function () {

    /* =========================
       NÚT ĐẶT LỊCH KHÁM
    ========================= */

    const bookingButtons =
        document.querySelectorAll(
            ".hero-actions a, .booking-btn, .specialty-card a"
        );

    bookingButtons.forEach(function (button) {

        const text =
            button.textContent.trim().toLowerCase();

        if (
            text.includes("đặt lịch") ||
            text.includes("khám ngay")
        ) {

            button.addEventListener("click", function (event) {

                /*
                    Nếu nút đã có href chính xác
                    thì để trình duyệt chuyển trang.
                */

                if (
                    !button.getAttribute("href") ||
                    button.getAttribute("href") === "#"
                ) {

                    event.preventDefault();

                    window.location.href =
                        "dat-lich.html";
                }

            });

        }

    });


    /* =========================
       NÚT XEM BÁC SĨ
    ========================= */

    const doctorButtons =
        document.querySelectorAll(
            ".hero-actions a, .doctor-btn"
        );

    doctorButtons.forEach(function (button) {

        const text =
            button.textContent.trim().toLowerCase();

        if (text.includes("bác sĩ")) {

            button.addEventListener("click", function (event) {

                if (
                    !button.getAttribute("href") ||
                    button.getAttribute("href") === "#"
                ) {

                    event.preventDefault();

                    window.location.href =
                        "bac-si.html";
                }

            });

        }

    });


    /* =========================
       CÁC CHUYÊN KHOA
    ========================= */

    const specialtyCards =
        document.querySelectorAll(
            ".specialty-card"
        );


    specialtyCards.forEach(function (card) {

        card.style.cursor = "pointer";


        card.addEventListener("click", function () {

            const title =
                card.querySelector("h3, h2, .specialty-name");


            if (!title) {

                window.location.href =
                    "dat-lich.html";

                return;
            }


            const specialty =
                title.textContent.trim();


            /*
                Lưu chuyên khoa để trang đặt lịch
                có thể sử dụng sau này.
            */

            localStorage.setItem(
                "selectedSpecialty",
                specialty
            );


            window.location.href =
                "dat-lich.html";

        });

    });


    /* =========================
       KIỂM TRA ĐĂNG NHẬP
    ========================= */

    const loggedIn =
        localStorage.getItem(
            "medicareLoggedIn"
        );


    const authButtons =
        document.querySelector(".auth-buttons");


    if (
        loggedIn === "true" &&
        authButtons
    ) {

        authButtons.innerHTML = `
            <a href="ho-so.html" class="login-btn">
                Hồ sơ
            </a>

            <a href="#" class="register-btn" id="homeLogout">
                Đăng xuất
            </a>
        `;


        const logout =
            document.getElementById(
                "homeLogout"
            );


        if (logout) {

            logout.addEventListener(
                "click",
                function (event) {

                    event.preventDefault();

                    localStorage.removeItem(
                        "medicareLoggedIn"
                    );

                    window.location.reload();

                }
            );

        }

    }

});