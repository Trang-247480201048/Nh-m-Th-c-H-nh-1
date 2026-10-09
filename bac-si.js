document.addEventListener("DOMContentLoaded", function () {

    /* =========================================================
       1. DỮ LIỆU BÁC SĨ
       Khớp 100% với dữ liệu trong dat-lich.js
       ========================================================= */

    const doctorsBySpecialty = {

        "Nội khoa": [

            {
                id: "noi-1",
                name: "BS. Nguyễn Hà Phương",
                room: "Phòng 101",
                degree: "Bác sĩ chuyên khoa I",
                experience: "8 năm",
                skills: "Nội khoa tổng quát",
                description:
                    "Bác sĩ Nguyễn Hà Phương có kinh nghiệm khám và tư vấn các bệnh lý nội khoa thường gặp, đồng thời theo dõi sức khỏe tổng quát cho người bệnh."
            },

            {
                id: "noi-2",
                name: "BS. Trần Minh Anh",
                room: "Phòng 102",
                degree: "Bác sĩ chuyên khoa I",
                experience: "7 năm",
                skills: "Nội khoa tổng quát",
                description:
                    "Bác sĩ Trần Minh Anh chuyên khám, tư vấn và theo dõi các bệnh lý nội khoa, chú trọng tư vấn phương pháp điều trị phù hợp cho từng người bệnh."
            },

            {
                id: "noi-3",
                name: "BS. Lê Hoàng Nam",
                room: "Phòng 103",
                degree: "Thạc sĩ Y khoa",
                experience: "9 năm",
                skills: "Nội khoa tổng quát",
                description:
                    "Bác sĩ Lê Hoàng Nam có nhiều năm kinh nghiệm trong lĩnh vực nội khoa và tư vấn chăm sóc sức khỏe tổng quát."
            },

            {
                id: "noi-4",
                name: "BS. Phạm Thu Hà",
                room: "Phòng 104",
                degree: "Bác sĩ chuyên khoa I",
                experience: "6 năm",
                skills: "Nội khoa tổng quát",
                description:
                    "Bác sĩ Phạm Thu Hà có kinh nghiệm khám và theo dõi các bệnh lý nội khoa thường gặp ở người trưởng thành."
            }

        ],


        "Ngoại khoa": [

            {
                id: "ngoai-1",
                name: "BS. Nguyễn Văn An",
                room: "Phòng 201",
                degree: "Thạc sĩ Y khoa",
                experience: "10 năm",
                skills: "Ngoại khoa tổng quát",
                description:
                    "Bác sĩ Nguyễn Văn An có kinh nghiệm trong khám và tư vấn các bệnh lý ngoại khoa, đồng thời hỗ trợ người bệnh trong quá trình điều trị."
            },

            {
                id: "ngoai-2",
                name: "BS. Trần Quốc Việt",
                room: "Phòng 202",
                degree: "Bác sĩ chuyên khoa I",
                experience: "8 năm",
                skills: "Ngoại khoa tổng quát",
                description:
                    "Bác sĩ Trần Quốc Việt chuyên khám và tư vấn các vấn đề ngoại khoa thường gặp, hướng dẫn người bệnh lựa chọn phương pháp điều trị phù hợp."
            },

            {
                id: "ngoai-3",
                name: "BS. Lê Văn Minh",
                room: "Phòng 203",
                degree: "Thạc sĩ Y khoa",
                experience: "12 năm",
                skills: "Ngoại khoa tổng quát",
                description:
                    "Bác sĩ Lê Văn Minh có nhiều năm kinh nghiệm trong lĩnh vực ngoại khoa và tư vấn điều trị các bệnh lý cần can thiệp ngoại khoa."
            },

            {
                id: "ngoai-4",
                name: "BS. Hoàng Đức Long",
                room: "Phòng 204",
                degree: "Bác sĩ chuyên khoa I",
                experience: "9 năm",
                skills: "Ngoại khoa tổng quát",
                description:
                    "Bác sĩ Hoàng Đức Long có kinh nghiệm trong khám và tư vấn ngoại khoa, đồng thời theo dõi tình trạng người bệnh trong quá trình điều trị."
            }

        ],


        "Nhi khoa": [

            {
                id: "nhi-1",
                name: "BS. Nguyễn Thị Lan",
                room: "Phòng 301",
                degree: "Bác sĩ chuyên khoa I",
                experience: "8 năm",
                skills: "Nhi khoa tổng quát",
                description:
                    "Bác sĩ Nguyễn Thị Lan chuyên khám và theo dõi sức khỏe trẻ em, tư vấn các bệnh lý thường gặp ở trẻ nhỏ."
            },

            {
                id: "nhi-2",
                name: "BS. Phạm Minh Hương",
                room: "Phòng 302",
                degree: "Bác sĩ chuyên khoa I",
                experience: "7 năm",
                skills: "Nhi khoa tổng quát",
                description:
                    "Bác sĩ Phạm Minh Hương có kinh nghiệm khám và tư vấn sức khỏe cho trẻ em, đặc biệt là các bệnh lý thường gặp trong độ tuổi học đường."
            },

            {
                id: "nhi-3",
                name: "BS. Trần Thu Trang",
                room: "Phòng 303",
                degree: "Thạc sĩ Y khoa",
                experience: "9 năm",
                skills: "Nhi khoa tổng quát",
                description:
                    "Bác sĩ Trần Thu Trang chuyên khám, theo dõi và tư vấn chăm sóc sức khỏe cho trẻ em."
            },

            {
                id: "nhi-4",
                name: "BS. Đỗ Ngọc Anh",
                room: "Phòng 304",
                degree: "Bác sĩ chuyên khoa I",
                experience: "6 năm",
                skills: "Nhi khoa tổng quát",
                description:
                    "Bác sĩ Đỗ Ngọc Anh có kinh nghiệm khám và tư vấn các vấn đề sức khỏe thường gặp ở trẻ em."
            }

        ],


        "Tim mạch": [

            {
                id: "tim-1",
                name: "BS. Nguyễn Văn Bình",
                room: "Phòng 401",
                degree: "Bác sĩ chuyên khoa II",
                experience: "11 năm",
                skills: "Tim mạch tổng quát",
                description:
                    "Bác sĩ Nguyễn Văn Bình có kinh nghiệm khám, tư vấn và theo dõi các bệnh lý tim mạch thường gặp."
            },

            {
                id: "tim-2",
                name: "BS. Trần Thị Mai",
                room: "Phòng 402",
                degree: "Bác sĩ chuyên khoa I",
                experience: "9 năm",
                skills: "Tim mạch tổng quát",
                description:
                    "Bác sĩ Trần Thị Mai chuyên khám và tư vấn các vấn đề liên quan đến tim mạch và sức khỏe tuần hoàn."
            },

            {
                id: "tim-3",
                name: "BS. Lê Quốc Huy",
                room: "Phòng 403",
                degree: "Thạc sĩ Y khoa",
                experience: "10 năm",
                skills: "Tim mạch tổng quát",
                description:
                    "Bác sĩ Lê Quốc Huy có kinh nghiệm trong khám và theo dõi các bệnh lý tim mạch, tư vấn chăm sóc sức khỏe tim mạch."
            },

            {
                id: "tim-4",
                name: "BS. Phạm Văn Sơn",
                room: "Phòng 404",
                degree: "Bác sĩ chuyên khoa I",
                experience: "8 năm",
                skills: "Tim mạch tổng quát",
                description:
                    "Bác sĩ Phạm Văn Sơn chuyên khám và tư vấn các bệnh lý tim mạch thường gặp."
            }

        ],


        "Da liễu": [

            {
                id: "da-1",
                name: "BS. Nguyễn Thu Hà",
                room: "Phòng 501",
                degree: "Bác sĩ chuyên khoa I",
                experience: "7 năm",
                skills: "Da liễu tổng quát",
                description:
                    "Bác sĩ Nguyễn Thu Hà chuyên khám và tư vấn các bệnh lý về da, đồng thời hướng dẫn chăm sóc da phù hợp."
            },

            {
                id: "da-2",
                name: "BS. Trần Ngọc Mai",
                room: "Phòng 502",
                degree: "Thạc sĩ Y khoa",
                experience: "8 năm",
                skills: "Da liễu tổng quát",
                description:
                    "Bác sĩ Trần Ngọc Mai có kinh nghiệm khám và điều trị các vấn đề da liễu thường gặp."
            },

            {
                id: "da-3",
                name: "BS. Lê Thanh Hằng",
                room: "Phòng 503",
                degree: "Bác sĩ chuyên khoa I",
                experience: "6 năm",
                skills: "Da liễu tổng quát",
                description:
                    "Bác sĩ Lê Thanh Hằng chuyên khám và tư vấn các bệnh lý về da, đồng thời hướng dẫn chăm sóc da."
            },

            {
                id: "da-4",
                name: "BS. Phạm Quỳnh Anh",
                room: "Phòng 504",
                degree: "Bác sĩ chuyên khoa I",
                experience: "7 năm",
                skills: "Da liễu tổng quát",
                description:
                    "Bác sĩ Phạm Quỳnh Anh có kinh nghiệm trong khám và tư vấn các vấn đề da liễu thường gặp."
            }

        ],


        "Tai - Mũi - Họng": [

            {
                id: "tmh-1",
                name: "BS. Nguyễn Đức Anh",
                room: "Phòng 601",
                degree: "Bác sĩ chuyên khoa I",
                experience: "9 năm",
                skills: "Tai - Mũi - Họng",
                description:
                    "Bác sĩ Nguyễn Đức Anh chuyên khám và tư vấn các bệnh lý tai, mũi, họng thường gặp ở trẻ em và người lớn."
            },

            {
                id: "tmh-2",
                name: "BS. Trần Minh Đức",
                room: "Phòng 602",
                degree: "Thạc sĩ Y khoa",
                experience: "10 năm",
                skills: "Tai - Mũi - Họng",
                description:
                    "Bác sĩ Trần Minh Đức có kinh nghiệm trong khám và điều trị các bệnh lý liên quan đến tai, mũi và họng."
            },

            {
                id: "tmh-3",
                name: "BS. Lê Thị Hương",
                room: "Phòng 603",
                degree: "Bác sĩ chuyên khoa I",
                experience: "8 năm",
                skills: "Tai - Mũi - Họng",
                description:
                    "Bác sĩ Lê Thị Hương chuyên khám và tư vấn các bệnh lý tai, mũi, họng thường gặp."
            },

            {
                id: "tmh-4",
                name: "BS. Hoàng Minh Châu",
                room: "Phòng 604",
                degree: "Bác sĩ chuyên khoa I",
                experience: "7 năm",
                skills: "Tai - Mũi - Họng",
                description:
                    "Bác sĩ Hoàng Minh Châu có kinh nghiệm khám và tư vấn các bệnh lý tai, mũi, họng cho nhiều nhóm bệnh nhân."
            }

        ]

    };


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

    let selectedDoctor = null;


    /* =========================================================
       3. LẤY TOÀN BỘ BÁC SĨ
       ========================================================= */

    const allDoctors = [];

    Object.keys(doctorsBySpecialty).forEach(function (specialty) {

        doctorsBySpecialty[specialty].forEach(function (doctor) {

            allDoctors.push({
                ...doctor,
                specialty: specialty
            });

        });

    });


    /* =========================================================
       4. TẠO CHỮ VIẾT TẮT
       ========================================================= */

    function getAvatar(name) {

        const cleanName = name
            .replace("BS. ", "")
            .trim();

        const words = cleanName.split(" ");

        if (words.length >= 2) {

            return (
                words[0].charAt(0) +
                words[words.length - 1].charAt(0)
            ).toUpperCase();

        }

        return cleanName.substring(0, 2).toUpperCase();
    }


    /* =========================================================
       5. HIỂN THỊ DANH SÁCH BÁC SĨ
       ========================================================= */

    function renderDoctors() {

        const keyword =
            doctorSearch.value.trim().toLowerCase();

        const selectedSpecialty =
            specialtyFilter.value;

        const filteredDoctors =
            allDoctors.filter(function (doctor) {

                const matchName =
                    doctor.name.toLowerCase().includes(keyword);

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

                    <h3>${doctor.name}</h3>

                    <p class="doctor-specialty">
                        ${doctor.specialty}
                    </p>

                    <p class="doctor-room">
                        ${doctor.room}
                    </p>

                    <p class="doctor-experience">
                        ${doctor.experience} kinh nghiệm
                    </p>

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


            doctorGrid.appendChild(card);

        });


        doctorCount.textContent =
            filteredDoctors.length + " bác sĩ";


        if (filteredDoctors.length === 0) {

            noDoctor.style.display = "block";

        } else {

            noDoctor.style.display = "none";

        }


        addDoctorEvents();

    }


    /* =========================================================
       6. XỬ LÝ NÚT TRÊN CARD
       ========================================================= */

    function addDoctorEvents() {

        document
            .querySelectorAll(".view-doctor")
            .forEach(function (button) {

                button.addEventListener("click", function () {

                    const doctorId =
                        button.dataset.id;

                    openDoctorModal(doctorId);

                });

            });


        document
            .querySelectorAll(".book-doctor")
            .forEach(function (button) {

                button.addEventListener("click", function () {

                    const doctorId =
                        button.dataset.id;

                    bookDoctor(doctorId);

                });

            });

    }


    /* =========================================================
       7. HIỆN THÔNG TIN BÁC SĨ
       ========================================================= */

    function openDoctorModal(doctorId) {

        const doctor =
            allDoctors.find(function (item) {
                return item.id === doctorId;
            });


        if (!doctor) return;


        selectedDoctor = doctor;


        modalAvatar.textContent =
            getAvatar(doctor.name);

        modalDoctorName.textContent =
            doctor.name;

        modalSpecialty.textContent =
            doctor.specialty;

        modalDegree.textContent =
            doctor.degree;

        modalExperience.textContent =
            doctor.experience;

        modalSkills.textContent =
            doctor.skills;

        modalDescription.textContent =
            doctor.description;


        modal.classList.add("show");

    }


    /* =========================================================
       8. ĐẶT LỊCH
       ========================================================= */

    function bookDoctor(doctorId) {

        const doctor =
            allDoctors.find(function (item) {
                return item.id === doctorId;
            });


        if (!doctor) return;


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


        window.location.href =
            "dat-lich.html";

    }


    /* =========================================================
       9. TÌM KIẾM
       ========================================================= */

    searchDoctorBtn.addEventListener(
        "click",
        function () {
            renderDoctors();
        }
    );


    doctorSearch.addEventListener(
        "keydown",
        function (event) {

            if (event.key === "Enter") {

                event.preventDefault();

                renderDoctors();

            }

        }
    );


    specialtyFilter.addEventListener(
        "change",
        function () {

            doctorSearch.value = "";

            renderDoctors();

        }
    );


    /* =========================================================
       10. BẤM VÀO THẺ CHUYÊN KHOA
       ========================================================= */

    document
        .querySelectorAll(".specialty-card")
        .forEach(function (card) {

            card.addEventListener(
                "click",
                function () {

                    const specialty =
                        card.dataset.specialty;

                    specialtyFilter.value =
                        specialty;

                    doctorSearch.value = "";

                    renderDoctors();


                    document
                        .querySelector(".doctor-list-section")
                        .scrollIntoView({
                            behavior: "smooth"
                        });

                }
            );

        });


    /* =========================================================
       11. ĐÓNG MODAL
       ========================================================= */

    closeModal.addEventListener(
        "click",
        function () {

            modal.classList.remove("show");

        }
    );


    modal.addEventListener(
        "click",
        function (event) {

            if (event.target === modal) {

                modal.classList.remove("show");

            }

        }
    );


    document.addEventListener(
        "keydown",
        function (event) {

            if (event.key === "Escape") {

                modal.classList.remove("show");

            }

        }
    );


    /* =========================================================
       12. ĐẶT LỊCH TRONG MODAL
       ========================================================= */

    modalBookBtn.addEventListener(
        "click",
        function () {

            if (!selectedDoctor) return;

            bookDoctor(selectedDoctor.id);

        }
    );


    /* =========================================================
       13. KHỞI TẠO
       ========================================================= */

    renderDoctors();

});
