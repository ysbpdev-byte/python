# Skema Database ERP Hasta (Modul HRD)

> File ini mendeskripsikan skema tabel PostgreSQL yang boleh di-query oleh chatbot (SELECT only).
> Konvensi penamaan kolom: `c_` = string/varchar, `d_` = date/datetime, `n_` = numeric/FK, `l_` = boolean.

---

## Tabel: employees (Karyawan)

| Kolom | Tipe | Keterangan |
|---|---|---|
| id | bigint | Primary key |
| c_uuid | varchar | UUID unik karyawan |
| c_code | varchar | Kode karyawan |
| c_name | varchar | Nama lengkap |
| c_shortname | varchar | Nama singkat |
| c_email | varchar | Email |
| c_phone | varchar | Nomor telepon |
| c_office_phone | varchar | Telepon kantor |
| c_gender | varchar | Jenis kelamin |
| c_religion | varchar | Agama |
| c_marital_status | varchar | Status pernikahan |
| c_blood_type | varchar | Golongan darah |
| c_nik | varchar | NIK KTP |
| c_npwp | varchar | Nomor NPWP |
| c_bpjs_tk | varchar | Nomor BPJS Ketenagakerjaan |
| c_no_bpjs | varchar | Nomor BPJS Kesehatan |
| c_kk_number | varchar | Nomor kartu keluarga |
| c_birth_place | varchar | Tempat lahir |
| c_address | varchar | Alamat domisili |
| c_ktp_address | varchar | Alamat KTP |
| c_city | varchar | Kota |
| c_last_education | varchar | Pendidikan terakhir |
| c_contract | varchar | Jenis kontrak |
| c_no_fingerprint | varchar | ID fingerprint mesin absensi |
| c_month_year | varchar | Referensi bulan-tahun |
| c_illness | json | Riwayat penyakit (array) |
| c_status | varchar | Status karyawan (active, resigned, dll) |
| d_birth_date | date | Tanggal lahir |
| d_join_date | date | Tanggal bergabung |
| d_leave_date | date | Tanggal keluar |
| n_company_id | bigint | FK → companies.id |
| n_department_id | bigint | FK → departments.id |
| n_sub_department_id | bigint | FK → departments.id (sub-departemen) |
| n_position_id | bigint | FK → positions.id |
| n_title_id | bigint | FK → titles.c_code |
| n_location_id | bigint | FK → locations.id |
| n_group_id | bigint | FK → groups.id (grup shift) |
| n_employment_type_id | bigint | FK → employment_types.id |
| n_color_id | bigint | FK → colors.id |
| n_user_id | bigint | FK → users.id |
| n_child_count | int | Jumlah anak |
| n_shift_times | int | Jumlah shift |
| n_order_fingerprint | int | Urutan fingerprint |
| n_weight_kg | int | Berat badan (kg) |
| n_height_cm | int | Tinggi badan (cm) |
| l_status | boolean | Status aktif (true = aktif) |
| l_receiver_pic | boolean | Apakah sebagai PIC penerima |
| l_from_recruitment | boolean | Berasal dari proses rekrutmen |
| created_at | timestamp | Waktu dibuat |
| updated_at | timestamp | Waktu diperbarui |

**Relasi:**
- `n_department_id` → `departments.id`
- `n_position_id` → `positions.id`
- `n_title_id` → `titles.c_code`
- `n_company_id` → `companies.id`
- `n_employment_type_id` → `employment_types.id`

---

## Tabel: departments (Departemen)

| Kolom | Tipe | Keterangan |
|---|---|---|
| id | bigint | Primary key |
| c_uuid | varchar | UUID unik |
| c_name | varchar | Nama departemen |
| c_code | varchar | Kode departemen |
| n_company_id | bigint | FK → companies.id |
| n_manager_id | bigint | FK → employees.id (kepala departemen) |
| l_status | boolean | Status aktif |
| created_at | timestamp | Waktu dibuat |
| updated_at | timestamp | Waktu diperbarui |

---

## Tabel: titles (Jabatan/Golongan)

| Kolom | Tipe | Keterangan |
|---|---|---|
| id | bigint | Primary key |
| c_uuid | varchar | UUID unik |
| c_name | varchar | Nama jabatan |
| c_code | varchar | Kode jabatan (digunakan sebagai FK dari employees) |
| c_rank | varchar | Ranking/tingkat jabatan |
| created_at | timestamp | Waktu dibuat |
| updated_at | timestamp | Waktu diperbarui |

---

## Tabel: hr_contracts (Kontrak Karyawan)

| Kolom | Tipe | Keterangan |
|---|---|---|
| id | bigint | Primary key |
| c_uuid | varchar | UUID kontrak |
| c_code | varchar | Kode kontrak (format: CTR/YYYY/MM/###) |
| c_notes | text | Catatan tambahan |
| c_address | varchar | Alamat domisili saat kontrak |
| c_ktp_address | varchar | Alamat KTP saat kontrak |
| d_start_date | date | Tanggal mulai kontrak |
| d_end_date | date | Tanggal berakhir kontrak (null = PKWTT) |
| n_employee_id | bigint | FK → employees.id |
| n_company_id | bigint | FK → companies.id |
| n_department_id | bigint | FK → departments.id |
| n_title_id | bigint | FK → titles.id |
| n_employment_type_id | bigint | FK → employment_types.id |
| n_parent_contract_id | bigint | FK → hr_contracts.id (kontrak induk jika perpanjangan) |
| n_created_by | bigint | FK → users.id |
| n_extension_count | int | Jumlah kali diperpanjang |
| l_extended | boolean | Apakah kontrak ini merupakan perpanjangan |
| deleted_at | timestamp | Soft delete |
| created_at | timestamp | Waktu dibuat |
| updated_at | timestamp | Waktu diperbarui |

**Relasi:**
- `n_employee_id` → `employees.id`
- `n_parent_contract_id` → `hr_contracts.id` (self-referential untuk perpanjangan)

**Status kontrak** (computed dari approval + tanggal):
- `pending` — belum disetujui
- `rejected` — ditolak
- `active` — disetujui dan masih berlaku
- `expiring` — akan habis dalam 30 hari
- `expired` — sudah habis masa berlakunya

---

## Tabel: hr_contract_evaluations (Evaluasi Kontrak)

| Kolom | Tipe | Keterangan |
|---|---|---|
| id | bigint | Primary key |
| n_contract_id | bigint | FK → hr_contracts.id |
| n_employee_id | bigint | FK → employees.id |
| c_evaluator_name | varchar | Nama evaluator |
| c_evaluator_title | varchar | Jabatan evaluator |
| c_evaluator_department | varchar | Departemen evaluator |
| n_teamwork_q1 | int | Skor teamwork pertanyaan 1 |
| n_teamwork_q2 | int | Skor teamwork pertanyaan 2 |
| n_teamwork_q3 | int | Skor teamwork pertanyaan 3 |
| n_teamwork_q4 | int | Skor teamwork pertanyaan 4 |
| n_teamwork_q5 | int | Skor teamwork pertanyaan 5 |
| c_teamwork_comment | text | Komentar teamwork |
| n_quality_q1 | int | Skor kualitas kerja pertanyaan 1 |
| n_quality_q2 | int | Skor kualitas kerja pertanyaan 2 |
| n_quality_q3 | int | Skor kualitas kerja pertanyaan 3 |
| n_quality_q4 | int | Skor kualitas kerja pertanyaan 4 |
| n_quality_q5 | int | Skor kualitas kerja pertanyaan 5 |
| c_quality_comment | text | Komentar kualitas kerja |
| n_speed_q1 | int | Skor kecepatan kerja pertanyaan 1 |
| n_speed_q2 | int | Skor kecepatan kerja pertanyaan 2 |
| n_speed_q3 | int | Skor kecepatan kerja pertanyaan 3 |
| n_speed_q4 | int | Skor kecepatan kerja pertanyaan 4 |
| n_speed_q5 | int | Skor kecepatan kerja pertanyaan 5 |
| c_speed_comment | text | Komentar kecepatan kerja |
| created_at | timestamp | Waktu dibuat |
| updated_at | timestamp | Waktu diperbarui |

---

## Tabel: mutations (Mutasi Karyawan)

| Kolom | Tipe | Keterangan |
|---|---|---|
| id | bigint | Primary key |
| c_uuid | varchar | UUID mutasi |
| c_code | varchar | Kode mutasi (format: MUT-YYYYMMDD-###) |
| c_reason | text | Alasan mutasi |
| c_status | varchar | Status mutasi |
| c_reject_reason | text | Alasan penolakan |
| d_mutation_date | date | Tanggal efektif mutasi |
| n_employee_id | bigint | FK → employees.id |
| n_company_from_id | bigint | FK → companies.id (perusahaan asal) |
| n_company_to_id | bigint | FK → companies.id (perusahaan tujuan) |
| n_department_from_id | bigint | FK → departments.id (departemen asal) |
| n_department_to_id | bigint | FK → departments.id (departemen tujuan) |
| n_title_from_id | bigint | FK → titles.id (jabatan asal) |
| n_title_to_id | bigint | FK → titles.id (jabatan tujuan) |
| n_created_by | bigint | FK → users.id |
| deleted_at | timestamp | Soft delete |
| created_at | timestamp | Waktu dibuat |
| updated_at | timestamp | Waktu diperbarui |

---

## Tabel: attendance_requests (Permintaan Koreksi Absensi)

| Kolom | Tipe | Keterangan |
|---|---|---|
| id | bigint | Primary key |
| c_uuid | varchar | UUID permintaan |
| c_no | varchar | Nomor permintaan |
| c_employee_code | varchar | Kode karyawan (FK → employees.c_code) |
| c_employee_name | varchar | Nama karyawan (denormalisasi) |
| c_code | varchar | Kode referensi |
| c_name | varchar | Nama referensi |
| c_month_year | varchar | Bulan-tahun referensi |
| c_description | text | Deskripsi/keterangan koreksi |
| c_hour_in | varchar | Jam masuk yang dikoreksi |
| c_hour_out | varchar | Jam keluar yang dikoreksi |
| c_attachment_file | varchar | Path lampiran 1 |
| c_attachment_file2 | varchar | Path lampiran 2 |
| c_attachment_file3 | varchar | Path lampiran 3 |
| c_attachment_file4 | varchar | Path lampiran 4 |
| c_clinic_phone | varchar | Nomor telepon klinik (untuk izin sakit) |
| c_clinic_map_url | varchar | URL peta klinik |
| d_date | date | Tanggal absensi yang dikoreksi |
| d_request_date | date | Tanggal pengajuan |
| l_confirmed | boolean | Sudah dikonfirmasi |
| l_rejected | boolean | Ditolak |
| l_done | boolean | Selesai diproses |
| l_app | boolean | Diajukan melalui aplikasi mobile |
| created_at | timestamp | Waktu dibuat |
| updated_at | timestamp | Waktu diperbarui |

**Relasi:** `c_employee_code` → `employees.c_code`

---

## Tabel: schedule_overrides (Override Jadwal Kerja)

| Kolom | Tipe | Keterangan |
|---|---|---|
| id | bigint | Primary key |
| c_uuid | varchar | UUID override |
| c_forced_check_in | varchar | Jam masuk yang dipaksakan |
| c_forced_check_out | varchar | Jam keluar yang dipaksakan |
| c_forced_status | varchar | Status yang dipaksakan (hadir/izin/sakit/dll) |
| c_reason | text | Alasan override |
| c_status | varchar | Status persetujuan (pending/approved/rejected) |
| c_attachment_path | varchar | Path lampiran dokumen |
| c_rejection_reason | text | Alasan penolakan |
| d_override_date | date | Tanggal yang di-override |
| d_approved_at | datetime | Waktu persetujuan |
| n_employee_id | bigint | FK → employees.id |
| n_shift_id | bigint | FK → shifts.id |
| n_submitted_by | bigint | FK → employees.id (pengaju) |
| n_approved_by | bigint | FK → employees.id (penyetuju) |
| l_applied | boolean | Sudah diterapkan ke data absensi |
| deleted_at | timestamp | Soft delete |
| created_at | timestamp | Waktu dibuat |
| updated_at | timestamp | Waktu diperbarui |

---

## Tabel: holidays (Hari Libur)

| Kolom | Tipe | Keterangan |
|---|---|---|
| id | bigint | Primary key |
| c_uuid | varchar | UUID |
| c_name | varchar | Nama hari libur |
| c_marketing_location_code | varchar | Kode lokasi marketing |
| d_date | date | Tanggal hari libur |
| d_period | date | Periode referensi |
| l_sunday | boolean | Apakah hari Minggu |
| l_factory | boolean | Libur untuk pabrik |
| l_marketing | boolean | Libur untuk marketing |
| l_shift | boolean | Libur untuk karyawan shift |
| l_national_holiday | boolean | Libur nasional |
| created_at | timestamp | Waktu dibuat |
| updated_at | timestamp | Waktu diperbarui |

---

## Tabel: trainings (Jadwal Pelatihan)

| Kolom | Tipe | Keterangan |
|---|---|---|
| id | bigint | Primary key |
| c_uuid | varchar | UUID pelatihan |
| c_training_code | varchar | Kode pelatihan (TRN-001, dst) |
| c_name | varchar | Nama pelatihan |
| c_training_type | varchar | Jenis: Internal / Eksternal |
| c_code | varchar | Kode karyawan PIC (FK → employees.c_code) |
| c_trainer_1 | varchar | Nama trainer utama |
| c_trainer_2 | varchar | Nama trainer kedua |
| c_note | text | Catatan |
| d_start | date | Tanggal mulai rencana |
| d_actual_start | date | Tanggal mulai aktual |
| d_end | date | Tanggal selesai rencana |
| d_actual_end | date | Tanggal selesai aktual |
| d_hrd_confirm | datetime | Waktu konfirmasi HRD |
| d_section_head_confirm | datetime | Waktu konfirmasi kepala seksi |
| d_factory_manager_confirm | datetime | Waktu konfirmasi manajer pabrik |
| n_department_id | bigint | FK → departments.id |
| n_participant | int | Jumlah peserta |
| n_kkm | float | Nilai KKM (kriteria ketuntasan minimum) |
| l_hrd_confirm | boolean | Sudah dikonfirmasi HRD |
| l_section_head_confirm | boolean | Sudah dikonfirmasi kepala seksi |
| l_factory_manager_confirm | boolean | Sudah dikonfirmasi manajer pabrik |
| created_at | timestamp | Waktu dibuat |
| updated_at | timestamp | Waktu diperbarui |

**Relasi:**
- `n_department_id` → `departments.id`
- Many-to-Many dengan `competencies` via tabel pivot `training_competencies`

---

## Tabel: training_participants (Peserta Pelatihan)

| Kolom | Tipe | Keterangan |
|---|---|---|
| id | bigint | Primary key |
| n_training_id | bigint | FK → trainings.id |
| n_employee_id | bigint | FK → employees.id |
| n_grade | float | Nilai yang diperoleh peserta |
| c_status | varchar | Status keikutsertaan |
| created_at | timestamp | Waktu dibuat |
| updated_at | timestamp | Waktu diperbarui |

---

## Tabel: competencies (Kompetensi)

| Kolom | Tipe | Keterangan |
|---|---|---|
| id | bigint | Primary key |
| c_uuid | varchar | UUID kompetensi |
| c_code | varchar | Kode kompetensi (KMP-PPO, KMP-CAD, dll) |
| c_name | varchar | Nama kompetensi |
| c_note | varchar | Catatan |
| created_at | timestamp | Waktu dibuat |
| updated_at | timestamp | Waktu diperbarui |

---

## Tabel: grades (Nilai Pelatihan per Kompetensi)

| Kolom | Tipe | Keterangan |
|---|---|---|
| id | bigint | Primary key |
| n_training_id | bigint | FK → trainings.id |
| n_competency_id | bigint | FK → competencies.id |
| n_department_id | bigint | FK → departments.id |
| c_code | varchar | Kode karyawan (FK → employees.c_code) |
| d_start | date | Tanggal mulai |
| d_end | date | Tanggal selesai |
| l_passed | boolean | Apakah lulus |
| created_at | timestamp | Waktu dibuat |
| updated_at | timestamp | Waktu diperbarui |

---

## Tabel: recruitment_requests (Permintaan Rekrutmen)

| Kolom | Tipe | Keterangan |
|---|---|---|
| id | bigint | Primary key |
| c_uuid | varchar | UUID permintaan |
| c_position_title | varchar | Judul posisi yang dibutuhkan |
| c_employment_status | varchar | Status kepegawaian yang diinginkan |
| c_min_education | varchar | Pendidikan minimum |
| c_gender | varchar | Persyaratan jenis kelamin |
| c_experience | text | Deskripsi pengalaman yang dibutuhkan |
| c_health_condition | text | Kondisi kesehatan yang disyaratkan |
| c_job_description | text | Deskripsi pekerjaan |
| c_status | varchar | Status permintaan |
| c_benefits | text | Benefit yang ditawarkan |
| d_needed_date | date | Tanggal target karyawan dibutuhkan |
| j_skills | json | Keahlian yang dibutuhkan (array) |
| j_tk_breakdown | json | Rincian kebutuhan tenaga kerja (array) |
| j_requirements | json | Persyaratan tambahan (array) |
| j_locations | json | Lokasi penempatan (array) |
| n_requester_id | bigint | FK → users.id (pengaju) |
| n_company_id | bigint | FK → companies.id |
| n_department_id | bigint | FK → departments.id |
| n_position_id | bigint | FK → positions.id |
| n_location_id | bigint | FK → locations.id |
| n_headcount | int | Jumlah karyawan yang dibutuhkan |
| n_experience_years | int | Tahun pengalaman minimum |
| n_age_min | int | Usia minimum |
| n_age_max | int | Usia maksimum |
| created_at | timestamp | Waktu dibuat |
| updated_at | timestamp | Waktu diperbarui |

---

## Tabel: candidates (Kandidat Rekrutmen)

> Kolom yang terenkripsi (salary, rekening) tidak disertakan karena tidak bisa di-query langsung.

| Kolom | Tipe | Keterangan |
|---|---|---|
| id | bigint | Primary key |
| uuid | varchar | UUID kandidat |
| c_name | varchar | Nama lengkap |
| c_email | varchar | Email |
| c_phone | varchar | Nomor telepon |
| c_gender | varchar | Jenis kelamin |
| c_religion | varchar | Agama |
| c_marital_status | varchar | Status pernikahan |
| c_blood_type | varchar | Golongan darah |
| c_nik | varchar | NIK KTP |
| c_birth_place | varchar | Tempat lahir |
| c_address | varchar | Alamat domisili |
| c_domicile | varchar | Domisili |
| c_ktp_address | varchar | Alamat KTP |
| c_ktp_city | varchar | Kota KTP |
| c_address_city | varchar | Kota domisili |
| c_last_education | varchar | Pendidikan terakhir |
| c_final_location | varchar | Lokasi penempatan akhir |
| c_status | varchar | Status kandidat (active, hired, rejected, dll) |
| c_cv_status | varchar | Status analisis CV (pending/analyzed/failed) |
| c_notice_period | varchar | Periode notice untuk resign dari pekerjaan sebelumnya |
| c_linkedin | varchar | URL profil LinkedIn |
| c_portfolio | varchar | URL portfolio |
| c_experience_years | varchar | Pengalaman dalam teks |
| c_placements | json | Lokasi penempatan yang dilamar (array) |
| c_notes | text | Catatan internal HRD |
| d_birth_date | date | Tanggal lahir |
| d_join_date | date | Tanggal bergabung (jika diterima) |
| d_signed_date | date | Tanggal tanda tangan persetujuan |
| d_cv_analyzed_at | datetime | Waktu analisis CV oleh AI |
| n_experience_years | int | Tahun pengalaman |
| n_height_cm | int | Tinggi badan (cm) |
| n_weight_kg | int | Berat badan (kg) |
| n_position_id | bigint | FK → positions.id (posisi lamaran utama) |
| n_position_id_2 | bigint | FK → positions.id (posisi lamaran ke-2) |
| n_position_id_3 | bigint | FK → positions.id (posisi lamaran ke-3) |
| n_company_id | bigint | FK → companies.id |
| n_pic_hrd_id | bigint | FK → users.id (PIC HRD yang menangani) |
| n_final_company_id | bigint | FK → companies.id (perusahaan penempatan akhir) |
| n_final_position_id | bigint | FK → positions.id (posisi penempatan akhir) |
| n_employee_id | bigint | FK → employees.id (jika sudah diterima jadi karyawan) |
| n_hrd_reject_id | bigint | FK → users.id (HRD yang menolak) |
| user_id | bigint | FK → users.id (akun kandidat) |
| l_willing_relocate | boolean | Bersedia relokasi |
| l_willing_business_trip | boolean | Bersedia perjalanan dinas |
| l_smoker | boolean | Perokok |
| l_declaration_agreed | boolean | Sudah menyetujui deklarasi |
| created_at | timestamp | Waktu dibuat |
| updated_at | timestamp | Waktu diperbarui |

**Relasi:**
- `n_employee_id` → `employees.id` (kandidat yang sudah direkrut)
- `n_position_id` → `positions.id`

---

## Tabel: recruitment_processes (Proses/Tahap Rekrutmen)

| Kolom | Tipe | Keterangan |
|---|---|---|
| id | bigint | Primary key |
| c_uuid | varchar | UUID proses |
| c_stage | varchar | Tahap rekrutmen (screening_cv, interview_hrd, interview_user, mcu, offering, dll) |
| c_status | varchar | Status tahap (pending, passed, failed, scheduled, dll) |
| c_location_or_link | varchar | Lokasi atau link video call |
| c_notes | json | Catatan per tahap (array) |
| d_scheduled_at | datetime | Jadwal pelaksanaan tahap |
| n_candidate_id | bigint | FK → candidates.id |
| created_at | timestamp | Waktu dibuat |
| updated_at | timestamp | Waktu diperbarui |

---

## Tabel: family_members (Anggota Keluarga)

| Kolom | Tipe | Keterangan |
|---|---|---|
| id | bigint | Primary key |
| uuid | varchar | UUID anggota keluarga |
| candidate_id | bigint | FK → candidates.id (jika dari rekrutmen) |
| n_employee_id | bigint | FK → employees.id (jika karyawan aktif) |
| c_relationship | varchar | Hubungan keluarga (suami/istri/anak/ayah/ibu/dll) |
| c_name | varchar | Nama anggota keluarga |
| c_birth_place | varchar | Tempat lahir |
| c_last_education | varchar | Pendidikan terakhir |
| c_occupation | varchar | Pekerjaan |
| c_company_name | varchar | Nama perusahaan tempat bekerja |
| d_birth_date | date | Tanggal lahir |
| n_order | int | Urutan (untuk anak ke-1, ke-2, dst) |
| n_age | int | Usia |
| l_alive | boolean | Masih hidup |
| created_at | timestamp | Waktu dibuat |
| updated_at | timestamp | Waktu diperbarui |

---

## Tabel: emergency_contacts (Kontak Darurat)

| Kolom | Tipe | Keterangan |
|---|---|---|
| id | bigint | Primary key |
| uuid | varchar | UUID kontak |
| candidate_id | bigint | FK → candidates.id (jika dari rekrutmen) |
| n_employee_id | bigint | FK → employees.id (jika karyawan aktif) |
| c_name | varchar | Nama kontak darurat |
| c_relationship | varchar | Hubungan dengan karyawan |
| c_phone | varchar | Nomor telepon |
| c_address | varchar | Alamat |
| created_at | timestamp | Waktu dibuat |
| updated_at | timestamp | Waktu diperbarui |

---

## Tabel: educations (Riwayat Pendidikan)

| Kolom | Tipe | Keterangan |
|---|---|---|
| id | bigint | Primary key |
| candidate_id | bigint | FK → candidates.id (jika dari rekrutmen) |
| n_employee_id | bigint | FK → employees.id (jika karyawan aktif) |
| c_level | varchar | Jenjang pendidikan (SD/SMP/SMA/D3/S1/S2/S3) |
| c_institution | varchar | Nama institusi/sekolah |
| c_major | varchar | Jurusan/program studi |
| c_city | varchar | Kota institusi |
| n_score | decimal | Nilai/IPK |
| n_score_max | decimal | Nilai maksimum skala |
| n_year_start | int | Tahun masuk |
| n_year_end | int | Tahun lulus |
| created_at | timestamp | Waktu dibuat |
| updated_at | timestamp | Waktu diperbarui |

---

## Tabel: work_experiences (Riwayat Pekerjaan)

| Kolom | Tipe | Keterangan |
|---|---|---|
| id | bigint | Primary key |
| candidate_id | bigint | FK → candidates.id (jika dari rekrutmen) |
| n_employee_id | bigint | FK → employees.id (jika karyawan aktif) |
| c_company | varchar | Nama perusahaan |
| c_position | varchar | Posisi/jabatan |
| c_department | varchar | Departemen |
| c_type | varchar | Jenis pekerjaan (full-time/part-time/kontrak/dll) |
| c_city | varchar | Kota |
| c_description | text | Deskripsi pekerjaan |
| c_reasons_leaving | text | Alasan keluar |
| c_company_address | varchar | Alamat perusahaan |
| c_company_phone | varchar | Telepon perusahaan |
| c_company_industry | varchar | Industri perusahaan |
| c_incentive_scheme | varchar | Skema insentif |
| c_org_position_desc | text | Deskripsi posisi dalam organisasi |
| d_start | date | Tanggal mulai bekerja |
| d_end | date | Tanggal selesai bekerja |
| n_subordinates | int | Jumlah bawahan |
| l_operational_car | boolean | Dapat fasilitas mobil operasional |
| l_car_ownership_program | boolean | Mengikuti program kepemilikan mobil |
| created_at | timestamp | Waktu dibuat |
| updated_at | timestamp | Waktu diperbarui |

> Kolom kompensasi (n_basic_salary, n_meal_allowance, dll) terenkripsi — tidak bisa di-query langsung.

---

## Tabel: certifications (Sertifikasi)

| Kolom | Tipe | Keterangan |
|---|---|---|
| id | bigint | Primary key |
| candidate_id | bigint | FK → candidates.id (jika dari rekrutmen) |
| n_employee_id | bigint | FK → employees.id (jika karyawan aktif) |
| c_name | varchar | Nama sertifikasi |
| c_issuer | varchar | Lembaga penerbit |
| c_expiry | varchar | Tanggal kedaluwarsa (dalam teks) |
| n_year | int | Tahun diperoleh |
| created_at | timestamp | Waktu dibuat |
| updated_at | timestamp | Waktu diperbarui |

---

## Tabel: job_desks (Uraian Tugas / Job Description)

| Kolom | Tipe | Keterangan |
|---|---|---|
| id | bigint | Primary key |
| c_uuid | varchar | UUID job desk |
| c_name | varchar | Nama/judul job desk |
| c_description | text | Uraian tugas lengkap |
| n_department_id | bigint | FK → departments.id |
| n_pic1_employee_id | bigint | FK → employees.id (PIC utama) |
| n_pic2_employee_id | bigint | FK → employees.id (PIC kedua) |
| l_status | boolean | Status aktif |
| created_at | timestamp | Waktu dibuat |
| updated_at | timestamp | Waktu diperbarui |

---

## Tabel: employee_discipline_summaries (Ringkasan Disiplin Karyawan)

| Kolom | Tipe | Keterangan |
|---|---|---|
| id | bigint | Primary key |
| n_employee_id | bigint | FK → employees.id |
| n_year | int | Tahun |
| n_month | int | Bulan (1–12) |
| n_work_days | int | Jumlah hari kerja dalam bulan tersebut |
| n_t1 | int | Jumlah pelanggaran tingkat 1 |
| n_t2 | int | Jumlah pelanggaran tingkat 2 |
| n_t3 | int | Jumlah pelanggaran tingkat 3 |
| n_alpha | int | Jumlah alpha (tidak hadir tanpa keterangan) |
| n_sd_sdi | int | Jumlah SD/SDI |
| n_kk | int | Jumlah KK |
| n_score | decimal | Skor disiplin total |
| c_category | varchar | Kategori disiplin (Baik / Cukup / Kurang) |
| created_at | timestamp | Waktu dibuat |
| updated_at | timestamp | Waktu diperbarui |

---

## Konvensi Penamaan Kolom

| Prefix | Tipe Data | Contoh |
|---|---|---|
| `c_` | varchar / string / text | `c_name`, `c_code`, `c_status` |
| `d_` | date | `d_start_date`, `d_birth_date` |
| `dt_` / `d_` | datetime/timestamp | `d_approved_at`, `d_confirmed_at` |
| `n_` | integer / bigint / FK | `n_employee_id`, `n_score` |
| `l_` | boolean | `l_status`, `l_extended` |
| `j_` | json | `j_skills`, `j_requirements` |
