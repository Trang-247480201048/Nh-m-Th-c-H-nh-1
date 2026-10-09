document.addEventListener("DOMContentLoaded", function () {

    const savedUser =
        JSON.parse(
            localStorage.getItem("medicareUser")
        ) || null;


    const savedProfile =
        JSON.parse(
            localStorage.getItem("medicareProfile")
        ) || null;


    /* =========================
       HIỂN THỊ TÀI KHOẢN
    ========================= */

    if (savedUser) {

        /* Tên hiển thị */

        document.getElementById("displayName")
            .textContent =
            savedUser.fullname ||
            "Chưa cập nhật";


        /* Tên đăng nhập */

        document.getElementById("username")
            .value =
            savedUser.username ||
            savedUser.email ||
            "";


        /* Email */

        document.getElementById("accountEmail")
            .value =
            savedUser.email ||
            "";


        /* Số điện thoại */

        document.getElementById("accountPhone")
            .value =
            savedUser.phone ||
            "";


        /* Thông tin bệnh nhân */

        document.getElementById("patientName")
            .value =
            savedUser.fullname ||
            "";

        document.getElementById("patientBirthday")
            .value =
            savedUser.birthday ||
            "";

        document.getElementById("patientPhone")
            .value =
            savedUser.phone ||
            "";


        /* Avatar */

        const fullname =
            savedUser.fullname || "";

        const firstLetter =
            fullname.trim()
                ? fullname
                    .trim()
                    .charAt(0)
                    .toUpperCase()
                : "?";

        document.getElementById("avatar")
            .textContent =
            firstLetter;
    }


    /* =========================
       HIỂN THỊ HỒ SƠ ĐÃ LƯU
    ========================= */

    if (savedProfile) {

        document.getElementById("patientName")
            .value =
            savedProfile.name ||
            savedUser?.fullname ||
            "";

        document.getElementById("patientBirthday")
            .value =
            savedProfile.birthday ||
            savedUser?.birthday ||
            "";

        document.getElementById("gender")
            .value =
            savedProfile.gender ||
            "";

        document.getElementById("patientPhone")
            .value =
            savedProfile.phone ||
            savedUser?.phone ||
            "";

        document.getElementById("address")
            .value =
            savedProfile.address ||
            "";

        document.getElementById("medicalHistory")
            .value =
            savedProfile.medicalHistory ||
            "";
    }


    /* =========================
       CẬP NHẬT TÀI KHOẢN
    ========================= */

    document
        .getElementById("updateAccountBtn")
        .addEventListener("click", function () {

            if (!savedUser) {

                alert(
                    "Chưa có tài khoản. Vui lòng đăng ký tài khoản trước."
                );

                return;
            }


            const newEmail =
                document
                    .getElementById("accountEmail")
                    .value
                    .trim();


            const newPhone =
                document
                    .getElementById("accountPhone")
                    .value
                    .trim();


            const newPassword =
                document
                    .getElementById("accountPassword")
                    .value;


            if (
                newEmail === "" ||
                newPhone === ""
            ) {

                alert(
                    "Vui lòng nhập đầy đủ email và số điện thoại."
                );

                return;
            }


            /* Cập nhật email */

            savedUser.email =
                newEmail;


            /*
             * Tên đăng nhập được giữ
             * theo email mới
             */

            savedUser.username =
                newEmail;


            /* Cập nhật số điện thoại */

            savedUser.phone =
                newPhone;


            /* Chỉ đổi mật khẩu
               nếu người dùng nhập mới */

            if (newPassword !== "") {

                savedUser.password =
                    newPassword;
            }


            /* Lưu lại */

            localStorage.setItem(
                "medicareUser",
                JSON.stringify(savedUser)
            );


            /* Cập nhật lại ô tên đăng nhập */

            document.getElementById("username")
                .value =
                savedUser.username;


            showMessage(
                "accountMessage",
                "Cập nhật tài khoản thành công!"
            );

        });


    /* =========================
       CẬP NHẬT HỒ SƠ
    ========================= */

    document
        .getElementById("updateProfileBtn")
        .addEventListener("click", function () {

            const name =
                document
                    .getElementById("patientName")
                    .value
                    .trim();


            const birthday =
                document
                    .getElementById("patientBirthday")
                    .value;


            const gender =
                document
                    .getElementById("gender")
                    .value;


            const phone =
                document
                    .getElementById("patientPhone")
                    .value
                    .trim();


            const address =
                document
                    .getElementById("address")
                    .value
                    .trim();


            const medicalHistory =
                document
                    .getElementById("medicalHistory")
                    .value
                    .trim();


            if (
                name === "" ||
                birthday === ""
            ) {

                alert(
                    "Vui lòng nhập họ tên và ngày sinh."
                );

                return;
            }


            const profile = {

                name:
                    name,

                birthday:
                    birthday,

                gender:
                    gender,

                phone:
                    phone,

                address:
                    address,

                medicalHistory:
                    medicalHistory

            };


            /* Lưu hồ sơ */

            localStorage.setItem(
                "medicareProfile",
                JSON.stringify(profile)
            );


            /* Đồng bộ với tài khoản */

            if (savedUser) {

                savedUser.fullname =
                    name;

                savedUser.birthday =
                    birthday;

                savedUser.phone =
                    phone;


                localStorage.setItem(
                    "medicareUser",
                    JSON.stringify(savedUser)
                );


                /* Cập nhật tên */

                document.getElementById(
                    "displayName"
                ).textContent =
                    name;


                /* Cập nhật avatar */

                document.getElementById(
                    "avatar"
                ).textContent =
                    name
                        .trim()
                        .charAt(0)
                        .toUpperCase();
            }


            showMessage(
                "profileMessage",
                "Cập nhật hồ sơ thành công!"
            );

        });


    /* =========================
       ĐĂNG XUẤT
    ========================= */

    document
        .getElementById("logoutBtn")
        .addEventListener("click", function (event) {

            event.preventDefault();

            localStorage.removeItem(
                "medicareLoggedIn"
            );

            window.location.href =
                "trang-chu.html";

        });


    /* =========================
       HIỂN THỊ THÔNG BÁO
    ========================= */

    function showMessage(
        id,
        text
    ) {

        const element =
            document.getElementById(id);


        element.textContent =
            text;


        element.classList.add(
            "show"
        );


        setTimeout(function () {

            element.classList.remove(
                "show"
            );

        }, 3000);

    }

});
