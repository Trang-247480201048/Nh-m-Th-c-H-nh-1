
document.addEventListener("DOMContentLoaded", function () {
    // ==========================================
    // CẤU HÌNH API
    // ==========================================
    const API_URL = "/api/bac-si";

    let allDoctors = [];
    let selectedDoctor = null;

    const $ = id => document.getElementById(id);

    const doctorGrid = $("doctorGrid");
    const doctorSearch = $("doctorSearch");
    const specialtyFilter = $("specialtyFilter");
    const searchDoctorBtn = $("searchDoctorBtn");
    const doctorCount = $("doctorCount");
    const noDoctor = $("noDoctor");

    const modal = $("doctorModal");
    const closeModal = $("closeModal");
    const modalAvatar = $("modalAvatar");
    const modalDoctorName = $("modalDoctorName");
    const modalSpecialty = $("modalSpecialty");
    const modalDegree = $("modalDegree");
    const modalExperience = $("modalExperience");
    const modalSkills = $("modalSkills");
    const modalDescription = $("modalDescription");
    const modalBookBtn = $("modalBookBtn");

    // ==========================================
    // HÀM HỖ TRỢ
    // ==========================================

    function getAvatar(name) {
        const cleanName = String(name || "")
            .replace(/^BS\.?\s*/i, "")
            .trim();

        const words = cleanName.split(/\s+/).filter(Boolean);

        if (words.length >= 2) {
            return (
                words[0].charAt(0) +
                words[words.length - 1].charAt(0)
            ).toUpperCase();
        }

        return cleanName.substring(0, 2).toUpperCase() || "BS";
    }

    function getValue(doctor, keys, fallback = "") {
        if (!doctor || typeof doctor !== "object") {
            return fallback;
        }

        for (const key of keys) {
            const value = doctor[key];

            if (
                value !== null &&
                value !== undefined &&
                String(value).trim() !== ""
            ) {
                return String(value).trim();
            }
        }

        return fallback;
    }

    // ==========================================
    // CHUẨN HÓA DỮ LIỆU BÁC SĨ TỪ API
    // HỖ TRỢ CẢ TÊN CỘT SQL SERVER
    // ==========================================

    function normalizeDoctor(doctor) {
        const name = getValue(
            doctor,
            [
                "name",
                "fullname",
                "full_name",
                "ho_ten",
                "HoTen"
            ],
            "Chưa cập nhật tên"
        );

        const specialty = getValue(
            doctor,
            [
                "specialty",
                "specialtyName",
                "chuyen_khoa",
                "ten_chuyen_khoa",
                "TenChuyenKhoa"
            ],
            "Chưa phân loại"
        );

        const degree = getValue(
            doctor,
            [
                "degree",
                "hoc_vi",
                "hocVi",
                "HocVi"
            ],
            "Chưa cập nhật"
        );

        const experience = getValue(
            doctor,
            [
                "experience",
                "kinh_nghiem",
                "kinhNghiem",
                "KinhNghiem"
            ],
            "Chưa cập nhật"
        );

        const skills = getValue(
            doctor,
            [
                "skills",
                "chuyen_mon",
                "chuyenMon",
                "ChuyenMon"
            ],
            "Chưa cập nhật"
        );

        const workplace = getValue(
            doctor,
            [
                "workplace",
                "noi_cong_tac",
                "noiCongTac",
                "NoiCongTac"
            ],
            ""
        );

        const description = getValue(
            doctor,
            [
                "description",
                "gioi_thieu",
                "gioiThieu",
                "GioiThieu"
            ],
            ""
        );

        return {
            id: getValue(
                doctor,
                [
                    "id",
                    "Id",
                    "IdBacSi",
                    "MaBacSi"
                ],
                ""
            ),

            name: name,
            specialty: specialty,

            room: getValue(
                doctor,
                [
                    "room",
                    "phong_kham",
                    "phongKham",
                    "PhongKham"
                ],
                "Chưa cập nhật phòng khám"
            ),

            degree: degree,
            experience: experience,
            skills: skills,
            workplace: workplace,

            phone: getValue(
                doctor,
                [
                    "phone",
                    "so_dien_thoai",
                    "soDienThoai",
                    "SoDienThoai"
                ],
                ""
            ),

            email: getValue(
                doctor,
                [
                    "email",
                    "Email"
                ],
                ""
            ),

            fee: getValue(
                doctor,
                [
                    "fee",
                    "phi_kham",
                    "phiKham",
                    "PhiKham"
                ],
                ""
            ),

            description: description ||
                (
                    skills !== "Chưa cập nhật"
                        ? skills +
                          (workplace
                            ? "\nNơi công tác: " + workplace
                            : "")
                        : "Thông tin chi tiết của bác sĩ chưa được cập nhật."
                )
        };
    }

    // ==========================================
    // LẤY DANH SÁCH BÁC SĨ TỪ BACKEND
    // ==========================================

    async function loadDoctors() {
        if (!doctorGrid) return;

        doctorGrid.innerHTML =
            '<p class="doctor-loading">Đang tải danh sách bác sĩ...</p>';

        if (doctorCount) {
            doctorCount.textContent = "Đang tải...";
        }

        if (noDoctor) {
            noDoctor.style.display = "none";
        }

        try {
            const response = await fetch(API_URL, {
                method: "GET",
                headers: {
                    "Accept": "application/json"
                },
                cache: "no-store"
            });

            if (!response.ok) {
                throw new Error(
                    "API trả về mã lỗi " + response.status
                );
            }

            const result = await response.json();

            if (
                result.status !== "success" ||
                !Array.isArray(result.data)
            ) {
                throw new Error(
                    "Dữ liệu trả về từ API không hợp lệ."
                );
            }

            console.log(
                "Dữ liệu bác sĩ API trả về:",
                result.data
            );

            // Giữ nguyên điều kiện bác sĩ hoạt động
            allDoctors = result.data
                .filter(doctor => doctor.active === true)
                .map(normalizeDoctor);

            console.log(
                "Danh sách bác sĩ sau chuẩn hóa:",
                allDoctors
            );

            updateSpecialtyOptions();
            renderDoctors();

        } catch (error) {
            console.error(
                "Lỗi tải danh sách bác sĩ:",
                error
            );

            doctorGrid.innerHTML = "";

            if (doctorCount) {
                doctorCount.textContent =
                    "Không tải được dữ liệu";
            }

            if (noDoctor) {
                noDoctor.innerHTML = "";

                const title = document.createElement("h3");
                title.textContent =
                    "Không thể tải danh sách bác sĩ";

                const message = document.createElement("p");
                message.textContent =
                    "Hãy kiểm tra backend Flask và kết nối API.";

                noDoctor.append(title, message);
                noDoctor.style.display = "block";
            }
        }
    }

    // ==========================================
    // CẬP NHẬT DANH SÁCH CHUYÊN KHOA
    // ==========================================

    function updateSpecialtyOptions() {
        if (!specialtyFilter) return;

        const previousValue = specialtyFilter.value;

        const specialties = [
            ...new Set(
                allDoctors.map(doctor => doctor.specialty)
            )
        ].sort((a, b) => a.localeCompare(b, "vi"));

        specialtyFilter.innerHTML =
            '<option value="">Tất cả chuyên khoa</option>';

        specialties.forEach(specialty => {
            const option = document.createElement("option");

            option.value = specialty;
            option.textContent = specialty;

            specialtyFilter.appendChild(option);
        });

        if (specialties.includes(previousValue)) {
            specialtyFilter.value = previousValue;
        }
    }

    // ==========================================
    // HIỂN THỊ DANH SÁCH BÁC SĨ
    // ==========================================

    function renderDoctors() {
        if (!doctorGrid) return;

        const keyword = doctorSearch
            ? doctorSearch.value.trim().toLocaleLowerCase("vi")
            : "";

        const selectedSpecialty = specialtyFilter
            ? specialtyFilter.value
            : "";

        const filteredDoctors = allDoctors.filter(doctor => {
            const matchName = doctor.name
                .toLocaleLowerCase("vi")
                .includes(keyword);

            const matchSpecialty =
                !selectedSpecialty ||
                doctor.specialty === selectedSpecialty;

            return matchName && matchSpecialty;
        });

        doctorGrid.innerHTML = "";

        filteredDoctors.forEach(doctor => {
            const card = document.createElement("article");
            card.className = "doctor-card";

            card.innerHTML = `
                <div class="doctor-avatar"></div>

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
                            type="button"
                            class="outline-btn view-doctor"
                        >
                            Xem thông tin
                        </button>

                        <button
                            type="button"
                            class="primary-btn book-doctor"
                        >
                            Đặt lịch
                        </button>
                    </div>
                </div>
            `;

            card.querySelector(".doctor-avatar").textContent =
                getAvatar(doctor.name);

            card.querySelector(".doctor-name").textContent =
                doctor.name;

            card.querySelector(".doctor-specialty").textContent =
                doctor.specialty;

            card.querySelector(".doctor-room").textContent =
                doctor.room;

            card.querySelector(".doctor-experience").textContent =
                doctor.experience === "Chưa cập nhật"
                    ? "Kinh nghiệm: Chưa cập nhật"
                    : "Kinh nghiệm: " + doctor.experience;

            card.querySelector(".view-doctor")
                .addEventListener("click", () => {
                    openDoctorModal(doctor.id);
                });

            card.querySelector(".book-doctor")
                .addEventListener("click", () => {
                    bookDoctor(doctor.id);
                });

            doctorGrid.appendChild(card);
        });

        if (doctorCount) {
            doctorCount.textContent =
                filteredDoctors.length + " bác sĩ";
        }

        if (noDoctor) {
            noDoctor.style.display =
                filteredDoctors.length === 0
                    ? "block"
                    : "none";
        }
    }

    // ==========================================
    // XEM CHI TIẾT HỒ SƠ BÁC SĨ
    // ==========================================

    function openDoctorModal(doctorId) {
        const doctor = allDoctors.find(
            item => String(item.id) === String(doctorId)
        );

        if (!doctor || !modal) return;

        selectedDoctor = doctor;

        if (modalAvatar) {
            modalAvatar.textContent =
                getAvatar(doctor.name);
        }

        if (modalDoctorName) {
            modalDoctorName.textContent =
                doctor.name;
        }

        if (modalSpecialty) {
            modalSpecialty.textContent =
                doctor.specialty;
        }

        if (modalDegree) {
            modalDegree.textContent =
                doctor.degree;
        }

        if (modalExperience) {
            modalExperience.textContent =
                doctor.experience;
        }

        if (modalSkills) {
            modalSkills.textContent =
                doctor.skills;
        }

        if (modalDescription) {
            modalDescription.textContent =
                doctor.description;

            modalDescription.style.whiteSpace =
                "pre-line";
        }

        // Thông tin bổ sung nếu HTML có các ID này
        if ($("modalWorkplace")) {
            $("modalWorkplace").textContent =
                doctor.workplace || "Chưa cập nhật";
        }

        if ($("modalPhone")) {
            $("modalPhone").textContent =
                doctor.phone || "Chưa cập nhật";
        }

        if ($("modalEmail")) {
            $("modalEmail").textContent =
                doctor.email || "Chưa cập nhật";
        }

        if ($("modalFee")) {
            const amount = Number(doctor.fee);

            $("modalFee").textContent =
                doctor.fee && Number.isFinite(amount)
                    ? amount.toLocaleString("vi-VN") + " đ"
                    : "Chưa cập nhật";
        }

        modal.classList.add("show");

        document.body.classList.add(
            "doctor-modal-open"
        );
    }

    // ==========================================
    // ĐÓNG HỒ SƠ BÁC SĨ
    // ==========================================

    function closeDoctorModal() {
        if (!modal) return;

        modal.classList.remove("show");

        document.body.classList.remove(
            "doctor-modal-open"
        );
    }

    // ==========================================
    // CHUYỂN SANG TRANG ĐẶT LỊCH
    // ==========================================

    function bookDoctor(doctorId) {
        const doctor = allDoctors.find(
            item => String(item.id) === String(doctorId)
        );

        if (!doctor) {
            alert("Không tìm thấy thông tin bác sĩ.");
            return;
        }

        // Giữ nguyên các khóa trang đặt lịch đang dùng
        localStorage.setItem(
            "selectedDoctor",
            doctor.name
        );

        localStorage.setItem(
            "selectedSpecialty",
            doctor.specialty
        );

        localStorage.setItem(
            "selectedRoom",
            doctor.room
        );

        localStorage.setItem(
            "selectedDoctorId",
            String(doctor.id)
        );

        window.location.href = "dat-lich.html";
    }

    // ==========================================
    // SỰ KIỆN TÌM KIẾM BÁC SĨ
    // ==========================================

    if (searchDoctorBtn) {
        searchDoctorBtn.addEventListener(
            "click",
            renderDoctors
        );
    }

    if (doctorSearch) {
        doctorSearch.addEventListener(
            "keydown",
            function (event) {
                if (event.key === "Enter") {
                    event.preventDefault();
                    renderDoctors();
                }
            }
        );
    }

    if (specialtyFilter) {
        specialtyFilter.addEventListener(
            "change",
            renderDoctors
        );
    }

    // ==========================================
    // LỌC NHANH BẰNG THẺ CHUYÊN KHOA
    // ==========================================

    document.querySelectorAll(".specialty-card")
        .forEach(card => {
            card.addEventListener("click", function () {
                const specialty = card.dataset.specialty;

                const exists = allDoctors.some(
                    doctor => doctor.specialty === specialty
                );

                if (!exists) {
                    alert(
                        "Chuyên khoa này hiện chưa có bác sĩ đang hoạt động."
                    );
                    return;
                }

                if (specialtyFilter) {
                    specialtyFilter.value = specialty;
                }

                if (doctorSearch) {
                    doctorSearch.value = "";
                }

                renderDoctors();

                document.getElementById("doctor-list")
                    ?.scrollIntoView({
                        behavior: "smooth"
                    });
            });
        });

    // ==========================================
    // SỰ KIỆN ĐÓNG MODAL
    // ==========================================

    if (closeModal) {
        closeModal.addEventListener(
            "click",
            closeDoctorModal
        );
    }

    if (modal) {
        modal.addEventListener("click", function (event) {
            if (event.target === modal) {
                closeDoctorModal();
            }
        });
    }

    document.addEventListener(
        "keydown",
        function (event) {
            if (event.key === "Escape") {
                closeDoctorModal();
            }
        }
    );

    // ==========================================
    // ĐẶT LỊCH TỪ MODAL
    // ==========================================

    if (modalBookBtn) {
        modalBookBtn.addEventListener("click", function () {
            if (selectedDoctor) {
                bookDoctor(selectedDoctor.id);
            }
        });
    }

    // ==========================================
    // KHỞI TẠO
    // ==========================================

    loadDoctors();
});
