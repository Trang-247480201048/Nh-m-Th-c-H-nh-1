USE MediCare;
GO

MERGE dbo.HoSoBacSi AS target
USING (
    VALUES
    -- ID, HocVi, BangCap, KinhNghiem, DaoTao, ChuyenMon,
    -- NoiCongTac, SoDienThoai, Email, PhiKham, GioiThieu

    (1, N'Thạc sĩ', N'Bác sĩ đa khoa, Thạc sĩ Nội khoa',
     N'12 năm', N'Đào tạo chuyên sâu về Nội khoa và quản lý bệnh mạn tính',
     N'Khám và điều trị các bệnh lý nội khoa, tăng huyết áp, rối loạn chuyển hóa',
     N'Phòng khám MediCare', N'0901000001', N'nguyenhaphuong@medicare.vn', 250000,
     N'Bác sĩ có kinh nghiệm trong khám, chẩn đoán và điều trị các bệnh lý nội khoa. Tập trung theo dõi sức khỏe tổng quát và quản lý bệnh mạn tính.'),

    (2, N'Thạc sĩ', N'Bác sĩ đa khoa, Thạc sĩ Nội khoa',
     N'10 năm', N'Đào tạo về chẩn đoán và điều trị bệnh lý nội khoa',
     N'Bệnh lý tiêu hóa, hô hấp và các bệnh nội khoa thường gặp',
     N'Phòng khám MediCare', N'0901000002', N'tranminhanh@medicare.vn', 250000,
     N'Bác sĩ chuyên khám và điều trị các bệnh lý nội khoa thường gặp, chú trọng đánh giá triệu chứng và theo dõi tiến triển bệnh.'),

    (3, N'Tiến sĩ', N'Bác sĩ đa khoa, Tiến sĩ Nội khoa',
     N'15 năm', N'Đào tạo chuyên sâu về bệnh lý nội khoa và chẩn đoán lâm sàng',
     N'Bệnh lý hô hấp, tiêu hóa và bệnh chuyển hóa',
     N'Phòng khám MediCare', N'0901000003', N'lehoangnam@medicare.vn', 250000,
     N'Bác sĩ có kinh nghiệm trong chẩn đoán và điều trị nhiều bệnh lý nội khoa, chú trọng xây dựng phác đồ điều trị phù hợp với từng người bệnh.'),

    (4, N'Thạc sĩ', N'Bác sĩ đa khoa, Thạc sĩ Nội khoa',
     N'9 năm', N'Đào tạo về nội khoa tổng quát và chăm sóc sức khỏe người trưởng thành',
     N'Khám sức khỏe tổng quát, bệnh lý nội tiết và tiêu hóa',
     N'Phòng khám MediCare', N'0901000004', N'phamthuha@medicare.vn', 250000,
     N'Bác sĩ chuyên khám sức khỏe tổng quát và điều trị các bệnh lý nội khoa, quan tâm đến việc tư vấn phòng bệnh và chăm sóc sức khỏe lâu dài.'),

    (5, N'Thạc sĩ', N'Bác sĩ đa khoa, Thạc sĩ Ngoại khoa',
     N'13 năm', N'Đào tạo chuyên sâu về ngoại khoa và phẫu thuật tổng quát',
     N'Khám ngoại khoa, đánh giá tổn thương và tư vấn phẫu thuật',
     N'Phòng khám MediCare', N'0901000005', N'nguyenvanan@medicare.vn', 250000,
     N'Bác sĩ chuyên khám và đánh giá các bệnh lý ngoại khoa, tư vấn phương pháp điều trị và theo dõi chăm sóc sau phẫu thuật.'),

    (6, N'Thạc sĩ', N'Bác sĩ đa khoa, Thạc sĩ Ngoại khoa',
     N'11 năm', N'Đào tạo về ngoại khoa tổng quát và xử trí vết thương',
     N'Ngoại khoa tổng quát, vết thương phần mềm và bệnh lý cần can thiệp ngoại khoa',
     N'Phòng khám MediCare', N'0901000006', N'tranquocviet@medicare.vn', 250000,
     N'Bác sĩ có kinh nghiệm trong thăm khám ngoại khoa, đánh giá tình trạng tổn thương và lựa chọn hướng điều trị phù hợp.'),

    (7, N'Bác sĩ chuyên khoa I', N'Bác sĩ đa khoa, Chuyên khoa I Ngoại khoa',
     N'8 năm', N'Đào tạo chuyên khoa về ngoại khoa tổng quát',
     N'Khám ngoại khoa, bệnh lý ổ bụng và xử trí vết thương',
     N'Phòng khám MediCare', N'0901000007', N'levanminh@medicare.vn', 250000,
     N'Bác sĩ chuyên khám các bệnh lý ngoại khoa, tư vấn điều trị và hướng dẫn người bệnh chăm sóc sau can thiệp.'),

    (8, N'Thạc sĩ', N'Bác sĩ đa khoa, Thạc sĩ Ngoại khoa',
     N'14 năm', N'Đào tạo nâng cao về phẫu thuật tổng quát',
     N'Ngoại khoa tổng quát và đánh giá bệnh lý cần phẫu thuật',
     N'Phòng khám MediCare', N'0901000008', N'hoangduclong@medicare.vn', 250000,
     N'Bác sĩ có kinh nghiệm trong thăm khám và điều trị ngoại khoa, chú trọng đánh giá toàn diện trước khi lựa chọn phương pháp can thiệp.'),

    (9, N'Thạc sĩ', N'Bác sĩ đa khoa, Thạc sĩ Nhi khoa',
     N'12 năm', N'Đào tạo chuyên sâu về nhi khoa và chăm sóc trẻ em',
     N'Khám và điều trị bệnh lý hô hấp, tiêu hóa ở trẻ em',
     N'Phòng khám MediCare', N'0901000009', N'nguyenthilan@medicare.vn', 250000,
     N'Bác sĩ chuyên khám và chăm sóc sức khỏe trẻ em, tư vấn dinh dưỡng và theo dõi sự phát triển theo từng độ tuổi.'),

    (10, N'Bác sĩ chuyên khoa I', N'Bác sĩ đa khoa, Chuyên khoa I Nhi khoa',
     N'9 năm', N'Đào tạo chuyên khoa về bệnh lý trẻ em',
     N'Nhi khoa tổng quát, bệnh lý hô hấp và tiêu hóa',
     N'Phòng khám MediCare', N'0901000010', N'phamminhhuong@medicare.vn', 250000,
     N'Bác sĩ có kinh nghiệm khám và điều trị các bệnh lý thường gặp ở trẻ em, đồng thời tư vấn chăm sóc sức khỏe cho gia đình.'),

    (11, N'Thạc sĩ', N'Bác sĩ đa khoa, Thạc sĩ Nhi khoa',
     N'11 năm', N'Đào tạo về chẩn đoán và điều trị bệnh lý nhi khoa',
     N'Bệnh lý nhi khoa, theo dõi phát triển thể chất và dinh dưỡng',
     N'Phòng khám MediCare', N'0901000011', N'tranthutrang@medicare.vn', 250000,
     N'Bác sĩ chuyên chăm sóc sức khỏe trẻ em, chú trọng phát hiện sớm các vấn đề sức khỏe và tư vấn dinh dưỡng.'),

    (12, N'Bác sĩ chuyên khoa I', N'Bác sĩ đa khoa, Chuyên khoa I Nhi khoa',
     N'7 năm', N'Đào tạo chuyên sâu về nhi khoa tổng quát',
     N'Khám bệnh trẻ em, bệnh lý đường hô hấp và chăm sóc trẻ nhỏ',
     N'Phòng khám MediCare', N'0901000012', N'dongoanh@medicare.vn', 250000,
     N'Bác sĩ chuyên khám các bệnh lý thường gặp ở trẻ nhỏ, tư vấn chăm sóc và theo dõi sức khỏe trẻ theo từng giai đoạn phát triển.'),

    (13, N'Tiến sĩ', N'Bác sĩ đa khoa, Tiến sĩ Tim mạch',
     N'16 năm', N'Đào tạo chuyên sâu về tim mạch và chẩn đoán bệnh lý tim',
     N'Tăng huyết áp, bệnh mạch vành và rối loạn nhịp tim',
     N'Phòng khám MediCare', N'0901000013', N'nguyenvanbinh@medicare.vn', 350000,
     N'Bác sĩ chuyên khám, chẩn đoán và theo dõi các bệnh lý tim mạch, tư vấn kiểm soát các yếu tố nguy cơ tim mạch.'),

    (14, N'Thạc sĩ', N'Bác sĩ đa khoa, Thạc sĩ Tim mạch',
     N'12 năm', N'Đào tạo nâng cao về chẩn đoán và điều trị bệnh tim mạch',
     N'Tăng huyết áp, suy tim và bệnh lý mạch máu',
     N'Phòng khám MediCare', N'0901000014', N'tranthimai@medicare.vn', 350000,
     N'Bác sĩ có kinh nghiệm trong theo dõi và điều trị bệnh lý tim mạch, chú trọng quản lý huyết áp và phòng ngừa biến chứng.'),

    (15, N'Bác sĩ chuyên khoa II', N'Bác sĩ đa khoa, Chuyên khoa II Tim mạch',
     N'14 năm', N'Đào tạo chuyên sâu về bệnh lý tim mạch',
     N'Bệnh mạch vành, rối loạn nhịp tim và bệnh lý tim mạch ở người trưởng thành',
     N'Phòng khám MediCare', N'0901000015', N'lequochuy@medicare.vn', 350000,
     N'Bác sĩ chuyên đánh giá và điều trị các bệnh lý tim mạch, tư vấn theo dõi sức khỏe tim và kiểm soát nguy cơ biến chứng.'),

    (16, N'Thạc sĩ', N'Bác sĩ đa khoa, Thạc sĩ Tim mạch',
     N'10 năm', N'Đào tạo về tim mạch lâm sàng và quản lý bệnh mạn tính',
     N'Tăng huyết áp, rối loạn lipid máu và bệnh lý tim mạch',
     N'Phòng khám MediCare', N'0901000016', N'phamvanson@medicare.vn', 350000,
     N'Bác sĩ chuyên khám và theo dõi các bệnh lý tim mạch, tư vấn điều chỉnh lối sống và kiểm soát các yếu tố nguy cơ.'),

    (17, N'Thạc sĩ', N'Bác sĩ đa khoa, Thạc sĩ Da liễu',
     N'11 năm', N'Đào tạo chuyên sâu về da liễu và bệnh lý da',
     N'Mụn trứng cá, viêm da, dị ứng da và bệnh lý da thường gặp',
     N'Phòng khám MediCare', N'0901000017', N'nguyenthuha@medicare.vn', 200000,
     N'Bác sĩ chuyên khám và điều trị các bệnh lý da liễu, tư vấn chăm sóc và bảo vệ da phù hợp với từng tình trạng.'),

    (18, N'Bác sĩ chuyên khoa I', N'Bác sĩ đa khoa, Chuyên khoa I Da liễu',
     N'8 năm', N'Đào tạo chuyên khoa về chẩn đoán và điều trị bệnh da',
     N'Viêm da cơ địa, dị ứng da và các bệnh viêm nhiễm ngoài da',
     N'Phòng khám MediCare', N'0901000018', N'tranngocmai@medicare.vn', 200000,
     N'Bác sĩ có kinh nghiệm thăm khám các bệnh lý da liễu, tư vấn chăm sóc da và theo dõi đáp ứng điều trị.'),

    (19, N'Thạc sĩ', N'Bác sĩ đa khoa, Thạc sĩ Da liễu',
     N'10 năm', N'Đào tạo nâng cao về bệnh lý da và điều trị da liễu',
     N'Mụn, nám, viêm da và rối loạn sắc tố da',
     N'Phòng khám MediCare', N'0901000019', N'lethanhhang@medicare.vn', 200000,
     N'Bác sĩ chuyên khám và tư vấn điều trị các vấn đề da liễu, chú trọng xác định nguyên nhân và hướng chăm sóc phù hợp.'),

    (20, N'Bác sĩ chuyên khoa I', N'Bác sĩ đa khoa, Chuyên khoa I Da liễu',
     N'7 năm', N'Đào tạo chuyên khoa về da liễu tổng quát',
     N'Bệnh lý viêm da, dị ứng và chăm sóc sức khỏe làn da',
     N'Phòng khám MediCare', N'0901000020', N'phamquynhanh@medicare.vn', 200000,
     N'Bác sĩ chuyên thăm khám các bệnh lý da liễu thường gặp, tư vấn phòng ngừa tái phát và chăm sóc da khoa học.'),

    (21, N'Thạc sĩ', N'Bác sĩ đa khoa, Thạc sĩ Tai Mũi Họng',
     N'12 năm', N'Đào tạo chuyên sâu về bệnh lý tai, mũi và họng',
     N'Viêm xoang, viêm mũi dị ứng, viêm họng và bệnh lý tai',
     N'Phòng khám MediCare', N'0901000021', N'nguyenducanh@medicare.vn', 250000,
     N'Bác sĩ chuyên khám và điều trị các bệnh lý tai mũi họng, tư vấn chăm sóc và phòng ngừa bệnh đường hô hấp trên.'),

    (22, N'Bác sĩ chuyên khoa I', N'Bác sĩ đa khoa, Chuyên khoa I Tai Mũi Họng',
     N'9 năm', N'Đào tạo chuyên khoa về chẩn đoán và điều trị tai mũi họng',
     N'Viêm tai giữa, viêm xoang và các bệnh lý vùng họng',
     N'Phòng khám MediCare', N'0901000022', N'tranminhduc@medicare.vn', 250000,
     N'Bác sĩ có kinh nghiệm trong thăm khám các bệnh lý tai mũi họng, đánh giá triệu chứng và tư vấn điều trị phù hợp.'),

    (23, N'Thạc sĩ', N'Bác sĩ đa khoa, Thạc sĩ Tai Mũi Họng',
     N'10 năm', N'Đào tạo nâng cao về bệnh lý tai mũi họng',
     N'Viêm mũi dị ứng, bệnh lý xoang và rối loạn giọng nói',
     N'Phòng khám MediCare', N'0901000023', N'lethihuong@medicare.vn', 250000,
     N'Bác sĩ chuyên khám và điều trị các bệnh lý tai mũi họng, chú trọng phát hiện nguyên nhân và tư vấn chăm sóc lâu dài.'),

    (24, N'Bác sĩ chuyên khoa I', N'Bác sĩ đa khoa, Chuyên khoa I Tai Mũi Họng',
     N'8 năm', N'Đào tạo chuyên khoa về tai mũi họng tổng quát',
     N'Bệnh lý tai, mũi, họng và các bệnh lý đường hô hấp trên',
     N'Phòng khám MediCare', N'0901000024', N'hoangminhchau@medicare.vn', 250000,
     N'Bác sĩ chuyên thăm khám các bệnh lý tai mũi họng thường gặp, tư vấn điều trị và hướng dẫn phòng ngừa tái phát.')
) AS source (
    BacSiId, HocVi, BangCap, KinhNghiem, DaoTao, ChuyenMon,
    NoiCongTac, SoDienThoai, Email, PhiKham, GioiThieu
)
ON target.BacSiId = source.BacSiId

WHEN MATCHED THEN
    UPDATE SET
        HocVi = source.HocVi,
        BangCap = source.BangCap,
        KinhNghiem = source.KinhNghiem,
        DaoTao = source.DaoTao,
        ChuyenMon = source.ChuyenMon,
        NoiCongTac = source.NoiCongTac,
        SoDienThoai = source.SoDienThoai,
        Email = source.Email,
        PhiKham = source.PhiKham,
        GioiThieu = source.GioiThieu

WHEN NOT MATCHED BY TARGET THEN
    INSERT (
        BacSiId, HocVi, BangCap, KinhNghiem, DaoTao,
        ChuyenMon, NoiCongTac, SoDienThoai, Email, PhiKham, GioiThieu
    )
    VALUES (
        source.BacSiId, source.HocVi, source.BangCap, source.KinhNghiem,
        source.DaoTao, source.ChuyenMon, source.NoiCongTac,
        source.SoDienThoai, source.Email, source.PhiKham, source.GioiThieu
    );

GO
SELECT
    bs.Id,
    bs.HoTen,
    ck.TenChuyenKhoa,
    hs.HocVi,
    hs.KinhNghiem,
    hs.ChuyenMon,
    hs.NoiCongTac,
    hs.SoDienThoai,
    hs.Email,
    hs.PhiKham
FROM dbo.BacSi AS bs
INNER JOIN dbo.ChuyenKhoa AS ck
    ON bs.ChuyenKhoaId = ck.Id
LEFT JOIN dbo.HoSoBacSi AS hs
    ON bs.Id = hs.BacSiId
ORDER BY bs.Id ASC;
GO