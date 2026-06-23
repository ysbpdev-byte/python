# Skema Database ERP Hasta (Modul HRD)

PENTING: Gunakan nama tabel dan kolom PERSIS seperti yang tertulis di bawah ini. Jangan menerjemahkan nama tabel ke bahasa Indonesia (contoh: gunakan `employees` bukan `karyawan`, `departments` bukan `departemen`).

Konvensi prefix kolom: `c_` = varchar/text, `d_` = date/datetime, `n_` = integer/FK, `l_` = boolean, `j_` = json.

---

```sql
-- Karyawan
CREATE TABLE employees (
    id bigint PRIMARY KEY,
    c_code varchar,         -- kode karyawan
    c_name varchar,         -- nama lengkap
    c_shortname varchar,    -- nama singkat
    c_email varchar,
    c_phone varchar,
    c_gender varchar,       -- L = Laki-laki, P = Perempuan
    c_religion varchar,     -- ISLAM / KRISTEN / BUDHA / KATHOLIK / HINDU / KONG HU CU
    c_marital_status varchar, -- B = Bujang, K = Kawin, D = Duda, J = Janda
    c_blood_type varchar,   -- A / B / AB / O (dan varian rhesus: A+, O+, dll)
    c_nik varchar,          -- NIK KTP
    c_npwp varchar,
    c_birth_place varchar,
    c_address varchar,      -- alamat domisili
    c_city varchar,
    c_last_education varchar, -- free-text: SD, SMP/SLTP, SMA/SMK/STM/SLTA, D3, S1, S2
    c_contract varchar,     -- T = Tetap, B = Bulanan, BR = Borongan, H = Harian
    c_status varchar,       -- kode PTKP/PPh21: TK/0, TK/1, TK/2, TK/3 (tidak kawin), K/0, K/1, K/2, K/3 (kawin)
    d_birth_date date,
    d_join_date date,       -- tanggal bergabung
    d_leave_date date,      -- tanggal keluar
    n_company_id bigint,    -- FK -> companies.id
    n_department_id bigint, -- FK -> departments.id
    n_position_id bigint,   -- FK -> positions.id
    n_title_id bigint,      -- FK -> titles.c_code
    n_employment_type_id bigint,
    n_child_count int,
    l_status boolean,       -- true = aktif, false = non-aktif (resign/pensiun/dll)
    created_at timestamp,
    updated_at timestamp
);

-- Departemen
CREATE TABLE departments (
    id bigint PRIMARY KEY,
    c_name varchar,         -- nama departemen
    c_code varchar,
    n_company_id bigint,
    n_manager_id bigint,    -- FK -> employees.id (kepala departemen)
    l_status boolean,
    created_at timestamp,
    updated_at timestamp
);

-- Jabatan/Golongan
CREATE TABLE titles (
    id bigint PRIMARY KEY,
    c_name varchar,         -- nama jabatan
    c_code varchar,         -- kode jabatan (digunakan sebagai FK dari employees.n_title_id)
    c_rank varchar,
    created_at timestamp,
    updated_at timestamp
);

-- Kontrak Karyawan
CREATE TABLE hr_contracts (
    id bigint PRIMARY KEY,
    c_code varchar,         -- format: CTR/YYYY/MM/###
    c_notes text,
    d_start_date date,      -- tanggal mulai kontrak
    d_end_date date,        -- tanggal berakhir (NULL = PKWTT/permanen)
    n_employee_id bigint,   -- FK -> employees.id
    n_department_id bigint,
    n_title_id bigint,
    n_employment_type_id bigint,
    n_parent_contract_id bigint, -- FK -> hr_contracts.id (jika perpanjangan)
    n_extension_count int,
    l_extended boolean,     -- apakah ini perpanjangan kontrak
    deleted_at timestamp,
    created_at timestamp,
    updated_at timestamp
    -- status (via approval_requests): pending | approved; expiring = approved + d_end_date < 30 hari; expired = approved + d_end_date lewat
);

-- Evaluasi Kontrak
CREATE TABLE hr_contract_evaluations (
    id bigint PRIMARY KEY,
    n_contract_id bigint,   -- FK -> hr_contracts.id
    n_employee_id bigint,
    c_evaluator_name varchar,
    n_teamwork_q1 int, n_teamwork_q2 int, n_teamwork_q3 int, n_teamwork_q4 int, n_teamwork_q5 int,
    n_quality_q1 int, n_quality_q2 int, n_quality_q3 int, n_quality_q4 int, n_quality_q5 int,
    n_speed_q1 int, n_speed_q2 int, n_speed_q3 int, n_speed_q4 int, n_speed_q5 int,
    created_at timestamp,
    updated_at timestamp
);

-- Mutasi Karyawan
CREATE TABLE mutations (
    id bigint PRIMARY KEY,
    c_code varchar,         -- format: MUT-YYYYMMDD-###
    c_reason text,
    c_status varchar,       -- confirmed (+ pending/rejected)
    d_mutation_date date,
    n_employee_id bigint,
    n_department_from_id bigint,
    n_department_to_id bigint,
    n_title_from_id bigint,
    n_title_to_id bigint,
    deleted_at timestamp,
    created_at timestamp,
    updated_at timestamp
);

-- Koreksi Absensi
CREATE TABLE attendance_requests (
    id bigint PRIMARY KEY,
    c_no varchar,
    c_employee_code varchar, -- FK -> employees.c_code
    c_employee_name varchar,
    c_description text,
    c_hour_in varchar,
    c_hour_out varchar,
    d_date date,            -- tanggal absensi yang dikoreksi
    d_request_date date,
    l_confirmed boolean,
    l_rejected boolean,
    l_done boolean,
    created_at timestamp,
    updated_at timestamp
);

-- Override Jadwal Kerja
CREATE TABLE schedule_overrides (
    id bigint PRIMARY KEY,
    c_forced_status varchar, -- kode status absensi (lihat legenda di tabel absensi: WFH, SD, SDI, I, CT, CK, CH, CM, CMS, DL, OUT, PH, FK, FT, LM, O, A, ALW, T, T1, T2, T3, TS, TM1, TM2)
    c_reason text,
    c_status varchar,        -- pending | approved | rejected (default: pending)
    d_override_date date,
    n_employee_id bigint,
    n_approved_by bigint,    -- FK -> employees.id
    l_applied boolean,
    deleted_at timestamp,
    created_at timestamp,
    updated_at timestamp
);

-- Hari Libur
CREATE TABLE holidays (
    id bigint PRIMARY KEY,
    c_name varchar,
    d_date date,
    l_national_holiday boolean,
    l_factory boolean,
    l_marketing boolean,
    created_at timestamp,
    updated_at timestamp
);

-- Jadwal Pelatihan
CREATE TABLE trainings (
    id bigint PRIMARY KEY,
    c_training_code varchar, -- format: TRN-001
    c_name varchar,
    c_training_type varchar, -- Internal, Eksternal dari form
    d_start date,
    d_end date,
    d_actual_start date,
    d_actual_end date,
    n_department_id bigint,
    n_participant int,
    n_kkm float,             -- nilai minimum kelulusan
    l_hrd_confirm boolean,
    created_at timestamp,
    updated_at timestamp
);

-- Peserta Pelatihan
CREATE TABLE training_participants (
    id bigint PRIMARY KEY,
    n_training_id bigint,   -- FK -> trainings.id
    n_employee_id bigint,   -- FK -> employees.id
    n_grade float,          -- nilai peserta
    c_status varchar,       -- lulus | tidak_lulus (null = belum dinilai)
    created_at timestamp,
    updated_at timestamp
);

-- Kompetensi
CREATE TABLE competencies (
    id bigint PRIMARY KEY,
    c_code varchar,         -- contoh: KMP-PPO
    c_name varchar,
    created_at timestamp,
    updated_at timestamp
);

-- Permintaan Rekrutmen
CREATE TABLE recruitment_requests (
    id bigint PRIMARY KEY,
    c_position_title varchar,
    c_employment_status varchar, -- kontrak | magang | outsourcing | harian
    c_min_education varchar, -- slta | diploma | sarjana
    c_gender varchar,        -- L | P | bebas
    c_status varchar,        -- approved
    d_needed_date date,
    n_department_id bigint,
    n_headcount int,
    n_age_min int,
    n_age_max int,
    created_at timestamp,
    updated_at timestamp
);

-- Kandidat Rekrutmen
CREATE TABLE candidates (
    id bigint PRIMARY KEY,
    c_name varchar,
    c_email varchar,
    c_phone varchar,
    c_gender varchar,
    c_last_education varchar,
    c_status varchar,        -- applied | in_progress | on_hold | active | accepted | rejected
    d_birth_date date,
    n_employee_id bigint,    -- FK -> employees.id (jika sudah diterima)
    n_position_id bigint,
    created_at timestamp,
    updated_at timestamp
);

-- Tahap Rekrutmen
CREATE TABLE recruitment_processes (
    id bigint PRIMARY KEY,
    c_stage varchar,         -- pre_interview | interview_hrd | interview_user | psikotest | technical_test | medical_checkup
    c_status varchar,        -- ongoing | approved | rejected
    d_scheduled_at timestamp,
    n_candidate_id bigint,   -- FK -> candidates.id
    created_at timestamp,
    updated_at timestamp
);

-- Anggota Keluarga Karyawan
CREATE TABLE family_members (
    id bigint PRIMARY KEY,
    n_employee_id bigint,   -- FK -> employees.id
    c_relationship varchar, -- suami/istri/anak/ayah/ibu/dll
    c_name varchar,
    d_birth_date date,
    l_alive boolean,
    created_at timestamp,
    updated_at timestamp
);

-- Kontak Darurat
CREATE TABLE emergency_contacts (
    id bigint PRIMARY KEY,
    n_employee_id bigint,
    c_name varchar,
    c_relationship varchar,
    c_phone varchar,
    created_at timestamp,
    updated_at timestamp
);

-- Riwayat Pendidikan
CREATE TABLE educations (
    id bigint PRIMARY KEY,
    n_employee_id bigint,
    c_level varchar,        -- SD/SMP/SMA/D3/S1/S2/S3
    c_institution varchar,
    c_major varchar,
    n_year_start int,
    n_year_end int,
    created_at timestamp,
    updated_at timestamp
);

-- Riwayat Pekerjaan
CREATE TABLE work_experiences (
    id bigint PRIMARY KEY,
    n_employee_id bigint,
    c_company varchar,
    c_position varchar,
    d_start date,
    d_end date,
    created_at timestamp,
    updated_at timestamp
);

-- Sertifikasi
CREATE TABLE certifications (
    id bigint PRIMARY KEY,
    n_employee_id bigint,
    c_name varchar,
    c_issuer varchar,
    n_year int,
    created_at timestamp,
    updated_at timestamp
);

-- Uraian Tugas (Job Description)
CREATE TABLE job_desks (
    id bigint PRIMARY KEY,
    c_name varchar,
    c_description text,
    n_department_id bigint,
    n_pic1_employee_id bigint,
    l_status boolean,
    created_at timestamp,
    updated_at timestamp
);

-- Ringkasan Disiplin Karyawan
CREATE TABLE employee_discipline_summaries (
    id bigint PRIMARY KEY,
    n_employee_id bigint,
    n_year int,
    n_month int,
    n_work_days int,
    n_alpha int,            -- tidak hadir tanpa keterangan
    n_t1 int,              -- pelanggaran tingkat 1
    n_t2 int,              -- pelanggaran tingkat 2
    n_t3 int,              -- pelanggaran tingkat 3
    n_score decimal,
    c_category varchar,    -- Baik / Cukup / Kurang
    created_at timestamp,
    updated_at timestamp
);
```

---

## Contoh Query

```sql
-- 5 karyawan aktif terbaru
SELECT id, c_code, c_name, l_status, d_join_date FROM employees WHERE l_status = true ORDER BY d_join_date DESC LIMIT 5;

-- Karyawan per departemen
SELECT d.c_name AS departemen, COUNT(e.id) AS jumlah
FROM employees e JOIN departments d ON e.n_department_id = d.id
WHERE e.l_status = true GROUP BY d.c_name ORDER BY jumlah DESC LIMIT 20;

-- Kontrak yang akan habis dalam 30 hari
SELECT e.c_name, c.d_end_date FROM hr_contracts c
JOIN employees e ON c.n_employee_id = e.id
WHERE c.d_end_date BETWEEN CURRENT_DATE AND CURRENT_DATE + INTERVAL '30 days'
ORDER BY c.d_end_date LIMIT 20;
```
