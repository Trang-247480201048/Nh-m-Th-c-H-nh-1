
document.addEventListener("DOMContentLoaded", async function () {
    const API_BASE = "http://127.0.0.1:5000/api";

    let savedUser = null;

    const getElement = (id) => document.getElementById(id);

    function showMessage(id, text, isError = false) {
        const element = getElement(id);
        if (!element) return;

        element.textContent = text;
        element.classList.add("show");
        element.style.background = isError ? "#ffebee" : "#e8f5e9";
        element.style.color = isError ? "#c62828" : "#2e7d32";

        setTimeout(() => element.classList.remove("show"), 3000);
    }

    function setValue(id, value) {
        const element = getElement(id);
        if (element) element.value = value ?? "";
    }

    function displayUser(user) {
        savedUser = {
            id: user.id ?? user.Id,
            fullname: user.fullname ?? user.HoTen ?? "",
            phone: user.phone ?? user.SoDienThoai ?? "",
            email: user.email ?? user.Email ?? "",
            birthday: user.birthday ?? user.NgaySinh ?? ""
        };

        getElement("displayName").textContent =
            savedUser.fullname || "Chưa cập nhật";

        getElement("avatar").textContent =
            savedUser.fullname.trim()
                ? savedUser.fullname.trim().charAt(0).toUpperCase()
                : "?";

        setValue("username", savedUser.email || savedUser.phone);
        setValue("accountEmail", savedUser.email);
        setValue("accountPhone", savedUser.phone);

        setValue("patientName", savedUser.fullname);
        setValue("patientBirthday", savedUser.birthday);
        setValue("patientPhone", savedUser.phone);
    }

    // 1. Lấy tài khoản đang đăng nhập từ backend
    try {
        const response = await fetch(`${API_BASE}/auth/me`, {
            method: "GET",
            credentials: "include"
        });

        const result = await response.json();

        if (response.ok && result.success && result.user) {
            displayUser(result.user);
        } else {
            getElement("displayName").textContent = "Chưa đăng nhập";
            getElement("avatar").textContent = "?";

            showMessage(
                "accountMessage",
                "Không tìm thấy phiên đăng nhập. Bạn hãy đăng nhập lại.",
                true
            );
        }
    } catch (error) {
        console.error("Lỗi lấy thông tin tài khoản:", error);

        getElement("displayName").textContent = "Không tải được hồ sơ";

        showMessage(
            "accountMessage",
            "Không kết nối được backend. Hãy kiểm tra Flask tại cổng 5000.",
            true
        );
    }

    // 2. Nạp hồ sơ bổ sung đã lưu trên trình duyệt
    const savedProfile = JSON.parse(
        localStorage.getItem("medicareProfile") || "null"
    );

    if (savedProfile) {
        setValue("patientName", savedProfile.name || savedUser?.fullname);
        setValue("patientBirthday", savedProfile.birthday || savedUser?.birthday);
        setValue("gender", savedProfile.gender);
        setValue("patientPhone", savedProfile.phone || savedUser?.phone);
        setValue("address", savedProfile.address);
        setValue("medicalHistory", savedProfile.medicalHistory);
    }

    // 3. Cập nhật thông tin tài khoản
    getElement("updateAccountBtn").addEventListener("click", function () {
        if (!savedUser) {
            alert("Chưa tải được tài khoản. Vui lòng đăng nhập lại.");
            return;
        }

        const email = getElement("accountEmail").value.trim();
        const phone = getElement("accountPhone").value.trim();

        if (!email || !phone) {
            alert("Vui lòng nhập email và số điện thoại.");
            return;
        }

        // Chỉ cập nhật dữ liệu giao diện tạm thời.
        // Muốn lưu vào SQL Server cần API cập nhật tài khoản riêng.
        savedUser.email = email;
        savedUser.phone = phone;

        setValue("username", email);

        showMessage(
            "accountMessage",
            "Đã cập nhật trên giao diện. Thông tin SQL Server chưa thay đổi."
        );
    });

    // 4. Cập nhật hồ sơ bệnh nhân
    getElement("updateProfileBtn").addEventListener("click", function () {
        const name = getElement("patientName").value.trim();
        const birthday = getElement("patientBirthday").value;

        if (!name || !birthday) {
            alert("Vui lòng nhập họ tên và ngày sinh.");
            return;
        }

        const profile = {
            name,
            birthday,
            gender: getElement("gender").value,
            phone: getElement("patientPhone").value.trim(),
            address: getElement("address").value.trim(),
            medicalHistory: getElement("medicalHistory").value.trim()
        };

        localStorage.setItem("medicareProfile", JSON.stringify(profile));

        // Cập nhật phần hiển thị của trang.
        getElement("displayName").textContent = name;
        getElement("avatar").textContent =
            name.charAt(0).toUpperCase();

        showMessage(
            "profileMessage",
            "Đã lưu hồ sơ trên trình duyệt. Dữ liệu bổ sung chưa lưu vào SQL Server."
        );
    });

    // 5. Đăng xuất qua backend để hủy phiên đăng nhập
    getElement("logoutBtn").addEventListener("click", async function (event) {
        event.preventDefault();

        try {
            await fetch(`${API_BASE}/auth/logout`, {
                method: "POST",
                credentials: "include"
            });
        } catch (error) {
            console.error("Lỗi đăng xuất:", error);
        }

        localStorage.removeItem("medicareUser");
        localStorage.removeItem("medicareLogin");

        window.location.href = "trang-chu.html";
    });
});
