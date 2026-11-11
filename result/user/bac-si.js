
document.addEventListener("DOMContentLoaded", function () {

    /* =========================================================
       1. CẤU HÌNH API VÀ DỮ LIỆU
       ========================================================= */

    const API_URL = "http://127.0.0.1:5000/api/bac-si";

    // Danh sách này sẽ được lấy từ API, không viết cứng nữa.
    let allDoctors = [];
    let selectedDoctor = null;

    /* =========================================================
       2. DOM
       ========================================================= */

    const doctorGrid = document.getElementById("doctorGrid");
    const doctorSearch = document.getElementById("doctorSearch");
    const specialtyFilter = document.getElementById("specialtyFilter");
    const searchDoctorBtn = document.getElementById("searchDoctorBtn");
    const doctorCount = document.getElementById("doctorCount");
    const noDoctor = document.getElementById("noDoctor");

    const modal = document.getElementById("doctorModal");
    const closeModal = document.getElementById("closeModal");

    const modalAvatar = document.getElementById("modalAvatar");
    const modalDoctorName = document.getElementById("modalDoctorName");
    const modalSpecialty = document.getElementById("modalSpecialty");
    const modalDegree = document.getElementById("modalDegree");
    const modalExperience = document.getElementById("modalExperience");
    const modalSkills = document.getElementById("modalSkills");
    const modalDescription = document.getElementById("modalDescription");
    const modalBookBtn = document.getElementById("modalBookBtn");

    /* =========================================================
       3. TẠO CHỮ VIẾT TẮT
       ========================================================= */

    function getAvatar(name) {
        const cleanName = (name || "").replace("BS. ", "").trim();
        const words = cleanName.split(/\s+/);

        if (words.length >= 2) {
            return (
                words[0].charAt(0) +
                words[words.length - 1].charAt(0)
            ).toUpperCase();
        }

        return cleanName.substring(0, 2).toUpperCase();
    }

    /* =========================================================
       4. LẤY DANH SÁCH BÁC SĨ TỪ BACKEND
       ========================================================= */

    async function loadDoctors() {
        doctorGrid.innerHTML = "<p>Đang tải danh sách bác sĩ...</p>";
        doctorCount.textContent = "Đang tải...";
        noDoctor.style.display = "none";

        try {
            const response = await fetch(API_URL);

            if (!response.ok) {
                throw new Error("API trả về mã lỗi " + response.status);
            }

            const result = await response.json();

            if (result.status !== "success" || !Array.isArray(result.data)) {
                throw new Error("Dữ liệu trả về từ API không hợp lệ.");
            }

            // Chuyển dữ liệu API sang cấu trúc dùng trên giao diện.
            allDoctors = result.data
                .filter(function (doctor) {
                    return doctor.active === true;
                })
                .map(function (doctor) {
                    return {
                        id: doctor.id,
                        name: doctor.name || "Chưa cập nhật tên",
                        specialty: doctor.specialty || "Chưa phân loại",
                        room: doctor.room || "Chưa cập nhật phòng khám",

                        // API hiện chưa cung cấp các trường này.
                        degree: "Chưa cập nhật",
                        experience: "Chưa cập nhật",
                        skills: "Chưa cập nhật",
                        description: "Thông tin chi tiết của bác sĩ chưa được cập nhật."
                    };
                });

            // Đồng bộ các lựa chọn chuyên khoa với dữ liệu API.
            updateSpecialtyOptions();

            renderDoctors();

        } catch (error) {
            console.error("Lỗi tải danh sách bác sĩ:", error);

            doctorGrid.innerHTML = "";
            doctorCount.textContent = "Không tải được dữ liệu";
            noDoctor.textContent =
                "Không thể tải danh sách bác sĩ. Hãy kiểm tra backend Flask và kết nối API.";
            noDoctor.style.display = "block";
        }
    }

    /* =========================================================
       5. CẬP NHẬT DANH SÁCH LỌC CHUYÊN KHOA
       ========================================================= */

    function updateSpecialtyOptions() {
        const currentValue = specialtyFilter.value;

        const specialties = [
            ...new Set(
                allDoctors.map(function (doctor) {
                    return doctor.specialty;
                })
            )
        ].sort(function (a, b) {
            return a.localeCompare(b, "vi");
        });

        specialtyFilter.innerHTML = '<option value="">Tất cả chuyên khoa</option>';

        specialties.forEach(function (specialty) {
            const option = document.createElement("option");
            option.value = specialty;
            option.textContent = specialty;
            specialtyFilter.appendChild(option);
        });

        // Giữ lựa chọn cũ nếu chuyên khoa đó vẫn tồn tại.
        if (specialties.includes(currentValue)) {
            specialtyFilter.value = currentValue;
        }
    }

    /* =========================================================
       6. HIỂN THỊ DANH SÁCH BÁC SĨ
       ========================================================= */

    function renderDoctors() {
        const keyword = doctorSearch.value.trim().toLowerCase();
        const selectedSpecialty = specialtyFilter.value;

        const filteredDoctors = allDoctors.filter(function (doctor) {
            const matchName = doctor.name.toLowerCase().includes(keyword);

            const matchSpecialty =
                selectedSpecialty === "" ||
                doctor.specialty === selectedSpecialty;

            return matchName && matchSpecialty;
        });

        doctorGrid.innerHTML = "";

        filteredDoctors.forEach(function (doctor) {
            const card = document.createElement("div");
            card.className = "doctor-card";

            card.innerHTML = `
                <div class="doctor-avatar">
                    ${getAvatar(doctor.name)}
                </div>

                <div class="doctor-info">
                    <span class="doctor-status active">
                        Đang làm việc
                    </span>

                    <h3 class="doctor-name"></h3>

                    <p class="doctor-specialty"></p>

                    <p class="doctor-room"></p>

                    <p class="doctor-experience"></p>

                    <div class="doctor-actions">
                        <button
                            class="outline-btn view-doctor"
                            data-id="${doctor.id}"
                        >
                            Xem thông tin
                        </button>

                        <button
                            class="primary-btn book-doctor"
                            data-id="${doctor.id}"
                        >
                            Đặt lịch
                        </button>
                    </div>
                </div>
            `;

            // Dùng textContent để tránh chèn nội dung tên bác sĩ
            // trực tiếp vào HTML.
            card.querySelector(".doctor-name").textContent = doctor.name;
            card.querySelector(".doctor-specialty").textContent =
                doctor.specialty;
            card.querySelector(".doctor-room").textContent =
                doctor.room;
            card.querySelector(".doctor-experience").textContent =
                doctor.experience === "Chưa cập nhật"
                    ? "Kinh nghiệm: Chưa cập nhật"
                    : doctor.experience + " kinh nghiệm";

            doctorGrid.appendChild(card);
        });

        doctorCount.textContent = filteredDoctors.length + " bác sĩ";
        noDoctor.style.display =
            filteredDoctors.length === 0 ? "block" : "none";

        addDoctorEvents();
    }

    /* =========================================================
       7. XỬ LÝ NÚT TRÊN THẺ BÁC SĨ
       ========================================================= */

    function addDoctorEvents() {
        document.querySelectorAll(".view-doctor").forEach(function (button) {
            button.addEventListener("click", function () {
                openDoctorModal(button.dataset.id);
            });
        });

        document.querySelectorAll(".book-doctor").forEach(function (button) {
            button.addEventListener("click", function () {
                bookDoctor(button.dataset.id);
            });
        });
    }

    /* =========================================================
       8. HIỆN THÔNG TIN CHI TIẾT
       ========================================================= */

    function openDoctorModal(doctorId) {
        const doctor = allDoctors.find(function (item) {
            return String(item.id) === String(doctorId);
        });

        if (!doctor) return;

        selectedDoctor = doctor;

        modalAvatar.textContent = getAvatar(doctor.name);
        modalDoctorName.textContent = doctor.name;
        modalSpecialty.textContent = doctor.specialty;
        modalDegree.textContent = doctor.degree;
        modalExperience.textContent = doctor.experience;
        modalSkills.textContent = doctor.skills;
        modalDescription.textContent = doctor.description;

        modal.classList.add("show");
    }

    /* =========================================================
       9. CHUYỂN SANG TRANG ĐẶT LỊCH
       ========================================================= */

    function bookDoctor(doctorId) {
        const doctor = allDoctors.find(function (item) {
            return String(item.id) === String(doctorId);
        });

        if (!doctor) {
            alert("Không tìm thấy thông tin bác sĩ.");
            return;
        }

        localStorage.setItem("selectedDoctor", doctor.name);
        localStorage.setItem("selectedSpecialty", doctor.specialty);
        localStorage.setItem("selectedRoom", doctor.room);

        // Lưu thêm mã bác sĩ để có thể gửi ID lên backend sau này.
        localStorage.setItem("selectedDoctorId", String(doctor.id));

        window.location.href = "dat-lich.html";
    }

    /* =========================================================
       10. TÌM KIẾM VÀ LỌC
       ========================================================= */

    searchDoctorBtn.addEventListener("click", renderDoctors);

    doctorSearch.addEventListener("keydown", function (event) {
        if (event.key === "Enter") {
            event.preventDefault();
            renderDoctors();
        }
    });

    specialtyFilter.addEventListener("change", function () {
        renderDoctors();
    });

    /* =========================================================
       11. BẤM VÀO THẺ CHUYÊN KHOA
       ========================================================= */

    document.querySelectorAll(".specialty-card").forEach(function (card) {
        card.addEventListener("click", function () {
            const specialty = card.dataset.specialty;

            const exists = allDoctors.some(function (doctor) {
                return doctor.specialty === specialty;
            });

            if (!exists) {
                alert("Chuyên khoa này hiện chưa có bác sĩ đang hoạt động.");
                return;
            }

            specialtyFilter.value = specialty;
            doctorSearch.value = "";
            renderDoctors();

            const section = document.querySelector(".doctor-list-section");

            if (section) {
                section.scrollIntoView({ behavior: "smooth" });
            }
        });
    });

    /* =========================================================
       12. ĐÓNG MODAL
       ========================================================= */

    closeModal.addEventListener("click", function () {
        modal.classList.remove("show");
    });

    modal.addEventListener("click", function (event) {
        if (event.target === modal) {
            modal.classList.remove("show");
        }
    });

    document.addEventListener("keydown", function (event) {
        if (event.key === "Escape") {
            modal.classList.remove("show");
        }
    });

    /* =========================================================
       13. NÚT ĐẶT LỊCH TRONG MODAL
       ========================================================= */

    modalBookBtn.addEventListener("click", function () {
        if (!selectedDoctor) return;

        bookDoctor(selectedDoctor.id);
    });

    /* =========================================================
       14. KHỞI TẠO
       ========================================================= */

    loadDoctors();
});
