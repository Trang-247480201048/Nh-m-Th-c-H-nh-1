
'use strict';

// Dữ liệu giao diện tạm thời, chưa đồng bộ SQL Server.
const KEY = 'medicare_ck_layout_v3';

const defaults = [
  {id:1,name:'Nội khoa',fee:250000,doctorCount:4,services:[]},
  {id:2,name:'Ngoại khoa',fee:250000,doctorCount:4,services:[]},
  {id:3,name:'Nhi khoa',fee:250000,doctorCount:4,services:[]},
  {id:4,name:'Tim mạch',fee:350000,doctorCount:4,services:[]},
  {id:5,name:'Da liễu',fee:200000,doctorCount:4,services:[]},
  {id:6,name:'Tai - Mũi - Họng',fee:250000,doctorCount:4,services:[]}
];

const $ = id => document.getElementById(id);

const esc = s => String(s ?? '').replace(
  /[&<>"']/g,
  c => ({
    '&':'&amp;',
    '<':'&lt;',
    '>':'&gt;',
    '"':'&quot;',
    "'":'&#39;'
  }[c])
);

const money = n =>
  Number(n || 0).toLocaleString('vi-VN') + ' ₫';

const norm = s =>
  String(s || '')
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g,'')
    .toLowerCase();

let data;

try {
  data = JSON.parse(localStorage.getItem(KEY)) ||
    structuredClone(defaults);

  if (!Array.isArray(data)) throw Error();
} catch(e) {
  data = JSON.parse(JSON.stringify(defaults));
}

let selected = 4;
let editing = null;

function save() {
  try {
    localStorage.setItem(KEY, JSON.stringify(data));
  } catch(e) {
    toast('Không lưu được dữ liệu trình duyệt');
  }
}

function toast(t) {
  const el = $('toast');
  if (!el) return;

  el.textContent = t;
  el.classList.add('show');

  clearTimeout(window._ckToast);

  window._ckToast = setTimeout(
    () => el.classList.remove('show'),
    2600
  );
}

function current() {
  return data.find(s => s.id === selected);
}

function stats() {
  const services = data.flatMap(s => s.services);

  $('statSpec').textContent = data.length;
  $('statSvc').textContent = services.length;

  const fees = data.map(s => s.fee).filter(x => x > 0);

  $('statFee').textContent = money(
    fees.length ? Math.min(...fees) : 0
  );

  $('statSpecSub').textContent =
    data.reduce((n,s) => n + s.doctorCount, 0) +
    ' bác sĩ thuộc các chuyên khoa';

  $('statSvcSub').textContent =
    services.filter(s => s.status === 'active').length +
    ' đang hoạt động';
}

function renderSpecs() {
  const q = norm($('specSearch').value);
  const arr = data.filter(s => norm(s.name).includes(q));

  $('specList').innerHTML = arr.length
    ? arr.map(s => `
      <div class="ck-spec-item ${s.id === selected ? 'active' : ''}"
           data-id="${s.id}"
           role="button"
           tabindex="0">
        <div>
          <strong>${esc(s.name)}</strong>
          <small>${s.services.length} dịch vụ · ${s.doctorCount} bác sĩ</small>
          <small>Phí khám: ${money(s.fee)}</small>
        </div>
        <span class="ck-arrow">›</span>
      </div>
    `).join('')
    : '<p class="ck-hint">Không tìm thấy chuyên khoa.</p>';
}

function renderServices() {
  const s = current();
  if (!s) return;

  $('svcTitle').textContent = 'Dịch vụ ' + s.name;

  $('svcSub').textContent =
    s.services.length + ' dịch vụ · ' +
    s.services.filter(v => v.status === 'active').length +
    ' đang hoạt động · ' + s.doctorCount + ' bác sĩ';

  const q = norm($('svcSearch').value);
  const st = $('svcStatus').value;

  const arr = s.services.filter(v =>
    norm(v.name + ' ' + v.code).includes(q) &&
    (!st || st === v.status)
  );

  $('svcBody').innerHTML = arr.length
    ? arr.map(v => `
      <tr>
        <td>
          <strong>${esc(v.name)}</strong>
          <small>${esc(v.code)}</small>
        </td>
        <td>${v.duration} phút</td>
        <td>${money(v.fee)}</td>
        <td>
          <span class="status-pill ${v.status}">
            ${v.status === 'active'
              ? '● Hoạt động'
              : '● Tạm ngưng'}
          </span>
        </td>
        <td>
          <button class="btn-detail"
                  data-edit="${v.id}"
                  type="button">
            Chỉnh sửa
          </button>
        </td>
      </tr>
    `).join('')
    : `<tr>
        <td colspan="5"
            style="text-align:center;padding:28px;color:#87969b">
          Chưa có dịch vụ. Nhấn “Thêm dịch vụ” để tạo mới.
        </td>
      </tr>`;

  $('svcFoot').textContent =
    `Hiển thị ${arr.length} / ${s.services.length} dịch vụ thuộc chuyên khoa ${s.name}.`;
}

function render() {
  stats();
  renderSpecs();
  renderServices();
}

function reset() {
  editing = null;
  $('cfgForm').reset();
  $('cfgName').value = '';

  $('cfgFee').value = money(
    current()?.fee || 0
  ).replace(/[^\d]/g,'');

  $('cfgSub').textContent =
    'Thêm dịch vụ mới cho ' +
    (current()?.name || 'chuyên khoa');
}

// Chọn chuyên khoa
$('specList').addEventListener('click', e => {
  const node = e.target.closest('[data-id]');
  if (!node) return;

  selected = Number(node.dataset.id);
  reset();
  render();
});

$('specList').addEventListener('keydown', e => {
  if (e.key === 'Enter' || e.key === ' ') {
    const node = e.target.closest('[data-id]');

    if (node) {
      e.preventDefault();
      node.click();
    }
  }
});

// Tìm kiếm
$('specSearch').addEventListener('input', renderSpecs);
$('svcSearch').addEventListener('input', renderServices);
$('svcStatus').addEventListener('change', renderServices);

// Thêm dịch vụ
$('btnAddService').addEventListener('click', () => {
  reset();
  $('cfgName').focus();

  document.querySelector('.ck-config').scrollIntoView({
    behavior:'smooth',
    block:'nearest'
  });
});

// Hủy thay đổi
$('btnReset').addEventListener('click', reset);

// Chọn dịch vụ để chỉnh sửa
$('svcBody').addEventListener('click', e => {
  const b = e.target.closest('[data-edit]');
  if (!b) return;

  const v = current().services.find(
    x => x.id === Number(b.dataset.edit)
  );

  if (!v) return;

  editing = v.id;

  $('cfgName').value = v.name;
  $('cfgFee').value = String(v.fee);
  $('cfgDur').value = String(v.duration);
  $('cfgStatus').value = v.status;

  $('cfgSub').textContent = 'Đang chỉnh sửa ' + v.code;

  document.querySelector('.ck-config').scrollIntoView({
    behavior:'smooth',
    block:'nearest'
  });
});

// Lưu dịch vụ
$('cfgForm').addEventListener('submit', e => {
  e.preventDefault();

  const s = current();
  const name = $('cfgName').value.trim();

  const fee = Number(
    $('cfgFee').value.replace(/[^\d]/g,'')
  );

  const duration = Number($('cfgDur').value);
  const status = $('cfgStatus').value;

  if (!name || fee <= 0 || duration <= 0) {
    toast('Vui lòng nhập tên, phí và thời lượng hợp lệ');
    return;
  }

  if (editing !== null) {
    const v = s.services.find(x => x.id === editing);

    if (v) {
      Object.assign(v, {
        name,
        fee,
        duration,
        status
      });
    }
  } else {
    const all = data.flatMap(x => x.services);
    const id = Math.max(0, ...all.map(x => x.id)) + 1;

    s.services.push({
      id,
      code:'DV-' + String(id).padStart(3,'0'),
      name,
      fee,
      duration,
      status
    });
  }

  save();
  reset();
  render();

  toast('Đã lưu dịch vụ trên trình duyệt');
});

// Thêm chuyên khoa
$('btnAddSpec').addEventListener('click', () => {
  const name = prompt('Tên chuyên khoa mới:');
  if (name === null) return;

  const clean = name.trim();

  if (!clean || data.some(s => norm(s.name) === norm(clean))) {
    toast('Tên chuyên khoa trống hoặc đã tồn tại');
    return;
  }

  const fee = Number(
    prompt('Phí khám (VNĐ):','250000')
  );

  if (!Number.isFinite(fee) || fee <= 0) {
    toast('Phí khám không hợp lệ');
    return;
  }

  const doctors = Number(prompt('Số bác sĩ:','0'));

  if (!Number.isInteger(doctors) || doctors < 0) {
    toast('Số bác sĩ không hợp lệ');
    return;
  }

  selected = Math.max(0, ...data.map(s => s.id)) + 1;

  data.push({
    id:selected,
    name:clean,
    fee,
    doctorCount:doctors,
    services:[]
  });

  save();
  reset();
  render();

  toast('Đã thêm chuyên khoa trên trình duyệt');
});

// Sửa chuyên khoa
$('editSpecLink').addEventListener('click', e => {
  e.preventDefault();

  const s = current();
  if (!s) return;

  const name = prompt('Tên chuyên khoa:',s.name);
  if (name === null) return;

  const clean = name.trim();

  if (!clean || data.some(
    x => x.id !== s.id && norm(x.name) === norm(clean)
  )) {
    toast('Tên không hợp lệ hoặc bị trùng');
    return;
  }

  const fee = Number(
    prompt('Phí khám (VNĐ):',String(s.fee))
  );

  if (!Number.isFinite(fee) || fee <= 0) {
    toast('Phí khám không hợp lệ');
    return;
  }

  s.name = clean;
  s.fee = fee;

  save();
  render();

  toast('Đã cập nhật trên trình duyệt');
});

// Ngày giờ
function updateDate() {
  const now = new Date();

  if ($('topDate')) {
    $('topDate').textContent =
      now.toLocaleDateString('vi-VN');
  }

  if ($('syncTime')) {
    $('syncTime').textContent =
      'Dữ liệu được đồng bộ lúc ' +
      now.toLocaleTimeString('vi-VN', {
        hour:'2-digit',
        minute:'2-digit'
      });
  }
}

// Menu điện thoại
$('menuBtn')?.addEventListener('click', () => {
  $('sidebar')?.classList.toggle('open');
});

// Khởi tạo
if (!current() && data.length) {
  selected = data[0].id;
}

reset();
render();
updateDate();
