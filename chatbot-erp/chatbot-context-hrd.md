# Konteks Chatbot: Modul HRD — Hasta ERP

**Base URL:** `http://hasta.crabdance.com:16132`
**Modul:** Human Resource Development (HRD)
**Prefix URL:** `/hr`

---

## 1. Dashboard HRD

| Label | URL | Kegunaan |
|---|---|---|
| Dashboard HRD | `/hr/dashboard` | Halaman utama modul HRD. Menampilkan ringkasan dan statistik keseluruhan aktivitas HR. |

---

## 2. Karyawan (Employees)

| Label | URL | Kegunaan |
|---|---|---|
| Daftar Karyawan | `/hr/employees` | Melihat semua data karyawan yang terdaftar di perusahaan. Bisa filter dan cari. |
| Tambah Karyawan Baru | `/hr/employees/create` | Mendaftarkan karyawan baru ke sistem. |
| Detail Karyawan | `/hr/employees/{id}` | Melihat profil lengkap seorang karyawan: data pribadi, riwayat kontrak, jabatan, dll. |
| Edit Data Karyawan | `/hr/employees/{id}/edit` | Mengubah atau memperbarui data karyawan yang sudah ada. |

**Kapan digunakan:**
- Ingin mencari data karyawan tertentu → Daftar Karyawan
- Ingin onboarding karyawan baru → Tambah Karyawan Baru
- Ingin lihat profil/riwayat lengkap seorang karyawan → Detail Karyawan

---

## 3. Mutasi & Karir

| Label | URL | Kegunaan |
|---|---|---|
| Daftar Mutasi | `/hr/mutation` | Melihat semua pengajuan mutasi atau perpindahan jabatan/departemen karyawan. |
| Buat Mutasi Baru | `/hr/mutation/create` | Membuat surat pengajuan mutasi atau perubahan karir seorang karyawan (pindah divisi, promosi, rotasi). |
| Detail Mutasi | `/hr/mutation/{id}` | Melihat detail pengajuan mutasi tertentu beserta status persetujuannya. |

**Kapan digunakan:**
- Ingin memindahkan karyawan ke departemen/jabatan lain → Buat Mutasi Baru
- Ingin memantau status persetujuan mutasi → Daftar Mutasi
- Ingin menyetujui atau menolak mutasi (untuk atasan/HR) → Detail Mutasi

---

## 4. Absensi (Attendance)

| Label | URL | Kegunaan |
|---|---|---|
| Rekap Absensi | `/hr/attendance` | Melihat rekap kehadiran karyawan per bulan dan per departemen. |
| Input Absensi Manual | `/hr/attendance/create` | Memasukkan data kehadiran karyawan secara manual (misalnya jika mesin fingerprint bermasalah). |
| Edit Absensi | `/hr/attendance/{id}/edit` | Mengkoreksi data absensi yang sudah tersimpan. |

**Kapan digunakan:**
- Ingin lihat siapa yang hadir/tidak hadir hari ini atau bulan ini → Rekap Absensi
- Ingin koreksi atau tambah data kehadiran secara manual → Input Absensi Manual
- Ingin cek kehadiran karyawan tertentu berdasarkan departemen → Rekap Absensi (filter departemen)

---

## 5. Cuti & Izin (Leave & Permission)

| Label | URL | Kegunaan |
|---|---|---|
| Daftar Permintaan Cuti | `/hr/leaves` | Melihat semua pengajuan cuti dan izin dari karyawan beserta statusnya (pending/disetujui/ditolak). |
| Buat Pengajuan Cuti | `/hr/leaves/create` | Mengajukan permohonan cuti atau izin tidak masuk kerja. |
| Detail Cuti | `/hr/leaves/{uuid}` | Melihat detail pengajuan cuti tertentu, termasuk alasan dan timeline persetujuan. |

**Kapan digunakan:**
- Ingin mengajukan cuti atau izin → Buat Pengajuan Cuti
- Ingin lihat siapa saja yang sedang cuti → Daftar Permintaan Cuti
- Ingin menyetujui/menolak pengajuan cuti karyawan (untuk atasan) → Detail Cuti
- Ingin cek status pengajuan cuti yang sudah diajukan → Daftar Permintaan Cuti

---

## 6. Kontrak Karyawan (Employee Contract)

| Label | URL | Kegunaan |
|---|---|---|
| Daftar Kontrak | `/hr/contracts` | Melihat semua kontrak kerja karyawan (PKWT, PKWTT, dll) beserta status dan tanggal berakhirnya. |
| Buat Kontrak Baru | `/hr/contracts/create` | Membuat kontrak kerja baru untuk karyawan. |
| Detail Kontrak | `/hr/contracts/{uuid}` | Melihat isi dan detail kontrak tertentu. |
| Perpanjang Kontrak | `/hr/contracts/{uuid}/extend` | Memperpanjang masa berlaku kontrak karyawan yang akan habis. |
| Cetak PDF Kontrak | `/hr/contracts/template-pdf` | Mencetak atau mengunduh kontrak dalam format PDF. |

**Kapan digunakan:**
- Ingin buat kontrak untuk karyawan baru → Buat Kontrak Baru
- Ingin lihat kontrak mana saja yang akan segera habis → Daftar Kontrak (filter status)
- Ingin perpanjang kontrak yang hampir expired → Perpanjang Kontrak
- Ingin cetak surat kontrak → Cetak PDF Kontrak

---

## 7. Jadwal Kerja (Work Schedule)

| Label | URL | Kegunaan |
|---|---|---|
| Lihat Jadwal Kerja | `/hr/work_schedules` | Melihat jadwal shift kerja karyawan per grup (Grup A–D) dengan pola Shift 1/2/3/Libur. |
| Buat Jadwal Kerja | `/hr/work_schedules/create` | Membuat jadwal shift baru. |
| Perubahan Jadwal | `/hr/work_schedules/change` | Mengajukan atau mencatat perubahan jadwal shift karyawan. |

**Kapan digunakan:**
- Ingin lihat siapa yang masuk shift apa hari ini/minggu ini → Lihat Jadwal Kerja
- Ingin ubah jadwal shift seorang karyawan → Perubahan Jadwal

---

## 8. Surat Tugas (Assignments)

| Label | URL | Kegunaan |
|---|---|---|
| Daftar Surat Tugas | `/hr/assignments` | Melihat semua surat tugas yang pernah dibuat. |
| Buat Surat Tugas | `/hr/assignments/create` | Membuat surat tugas baru untuk karyawan yang ditugaskan ke suatu lokasi/kegiatan. |
| Detail Surat Tugas | `/hr/assignments/{id}` | Melihat detail surat tugas tertentu. |

**Kapan digunakan:**
- Ingin menugaskan karyawan ke suatu proyek atau lokasi → Buat Surat Tugas
- Ingin melihat riwayat penugasan karyawan → Daftar Surat Tugas

---

## 9. Rekrutmen (Recruitment)

### 9a. Dashboard Rekrutmen

| Label | URL | Kegunaan |
|---|---|---|
| Dashboard Rekrutmen | `/hr/recruitment/dashboard` | Melihat overview statistik rekrutmen: jumlah pelamar, tahap seleksi, hasil rekrutmen per departemen/posisi. |

### 9b. Permintaan Rekrutmen

| Label | URL | Kegunaan |
|---|---|---|
| Daftar Permintaan Rekrutmen | `/hr/recruitment/requests` | Melihat semua permintaan buka lowongan yang diajukan oleh departemen. |
| Buat Permintaan Rekrutmen | `/hr/recruitment/requests/create` | Mengajukan permintaan rekrutmen karyawan baru untuk posisi tertentu. |
| Detail Permintaan | `/hr/recruitment/requests/{uuid}` | Melihat detail dan status permintaan rekrutmen. |

### 9c. Screening Kandidat

| Label | URL | Kegunaan |
|---|---|---|
| Daftar Screening | `/hr/screening` | Melihat semua kandidat yang sedang dalam proses seleksi/screening. |
| Detail Screening Kandidat | `/hr/screening/{uuid}` | Melihat profil lengkap kandidat: data diri, pengalaman kerja, pendidikan, sertifikasi, keahlian bahasa & komputer, serta tahap seleksi saat ini. |
| Tambah Kandidat Screening | `/hr/screening/create` | Mendaftarkan kandidat baru ke dalam proses screening. |

**Tahap screening yang bisa dilakukan dari halaman detail:**
- Lanjutkan ke tahap berikutnya (advance)
- Setujui / tolak tahap seleksi
- Upload hasil MCU (Medical Check Up)
- Setujui hasil MCU
- Reschedule jadwal seleksi
- Tolak kandidat

### 9d. Status Rekrutmen (Candidates)

| Label | URL | Kegunaan |
|---|---|---|
| Status Rekrutmen | `/hr/candidates` | Melihat status akhir semua kandidat rekrutmen (diterima, ditolak, on-hold, dll). |

**Kapan digunakan (Rekrutmen secara keseluruhan):**
- Ingin buka lowongan untuk posisi tertentu → Buat Permintaan Rekrutmen
- Ingin lihat pelamar yang masuk dan proses seleksinya → Daftar Screening
- Ingin proses atau nilai seorang kandidat → Detail Screening Kandidat
- Ingin lihat hasil akhir rekrutmen (siapa yang diterima) → Status Rekrutmen
- Ingin lihat statistik rekrutmen keseluruhan → Dashboard Rekrutmen

---

## 10. Pelatihan (Training)

| Label | URL | Kegunaan |
|---|---|---|
| Jadwal Pelatihan | `/hr/trainings/schedules` | Melihat daftar semua jadwal pelatihan karyawan. |
| Buat Jadwal Pelatihan | `/hr/trainings/schedules/create` | Membuat jadwal pelatihan baru (termasuk pengajuan yang butuh persetujuan). |
| Nilai Pelatihan | `/hr/trainings/grades` | Melihat dan mengelola nilai/hasil pelatihan karyawan. |
| Input Nilai Pelatihan | `/hr/trainings/grades/create` | Memasukkan nilai hasil pelatihan untuk peserta. |
| Kompetensi | `/hr/trainings/competencies` | Mengelola daftar kompetensi yang digunakan sebagai acuan pelatihan. |

**Kapan digunakan:**
- Ingin jadwalkan pelatihan untuk karyawan → Buat Jadwal Pelatihan
- Ingin lihat pelatihan apa yang sudah/akan dilakukan → Jadwal Pelatihan
- Ingin input atau lihat nilai hasil pelatihan → Nilai Pelatihan / Input Nilai
- Ingin kelola kompetensi jabatan → Kompetensi

---

## 11. General Affairs (GA)

### 11a. Aset

| Label | URL | Kegunaan |
|---|---|---|
| Daftar Aset | `/hr/assets` | Melihat semua aset perusahaan yang dikelola oleh GA (inventaris kantor, peralatan, dll). |
| Tambah Aset | `/hr/assets/create` | Mendaftarkan aset baru ke sistem inventaris. |
| Detail Aset | `/hr/assets/{id}` | Melihat detail informasi suatu aset. |

### 11b. Kendaraan (Fleet)

| Label | URL | Kegunaan |
|---|---|---|
| Daftar Kendaraan | `/hr/vehicles` | Melihat semua kendaraan operasional perusahaan. |
| Tambah Kendaraan | `/hr/vehicles/create` | Mendaftarkan kendaraan baru. |
| Detail Kendaraan | `/hr/vehicles/{id}` | Melihat detail informasi kendaraan tertentu. |

### 11c. Tiket Maintenance

| Label | URL | Kegunaan |
|---|---|---|
| Daftar Tiket Maintenance | `/hr/maintenance-tickets` | Melihat semua tiket kerusakan atau permintaan perbaikan aset/fasilitas. |
| Buat Tiket Maintenance | `/hr/maintenance-tickets/create` | Melaporkan kerusakan atau permintaan perbaikan fasilitas/aset. |
| Detail Tiket | `/hr/maintenance-tickets/{id}` | Melihat detail dan status tiket maintenance. |

**Kapan digunakan (GA secara keseluruhan):**
- Ingin daftarkan atau lihat inventaris kantor → Daftar/Tambah Aset
- Ingin kelola armada kendaraan perusahaan → Daftar/Tambah Kendaraan
- Ingin laporkan kerusakan fasilitas atau alat → Buat Tiket Maintenance
- Ingin pantau status perbaikan yang sedang berjalan → Daftar Tiket Maintenance

---

## 12. Job Desk

| Label | URL | Kegunaan |
|---|---|---|
| Daftar Job Desk | `/hr/job-desk` | Melihat daftar uraian tugas (job description) untuk setiap jabatan/posisi. |
| Buat Job Desk | `/hr/job-desk/create` | Membuat uraian tugas baru untuk suatu posisi/jabatan. |
| Detail Job Desk | `/hr/job-desk/{id}` | Melihat uraian tugas lengkap suatu posisi. |

**Kapan digunakan:**
- Ingin lihat atau buat job description untuk suatu jabatan → Job Desk
- Ingin ketahui tanggung jawab dan tugas suatu posisi → Detail Job Desk

---

## 13. Laporan Kecelakaan Kerja (Work Accident)

| Label | URL | Kegunaan |
|---|---|---|
| Daftar Laporan Kecelakaan | `/hr/work-accident` | Melihat semua laporan insiden kecelakaan kerja yang pernah terjadi. |
| Buat Laporan Kecelakaan | `/hr/work-accident/create` | Melaporkan kejadian kecelakaan kerja baru. |
| Detail Laporan | `/hr/work-accident/{uuid}` | Melihat detail laporan kecelakaan tertentu. |

**Kapan digunakan:**
- Ada karyawan yang mengalami kecelakaan saat bekerja → Buat Laporan Kecelakaan
- Ingin lihat riwayat insiden keselamatan kerja → Daftar Laporan Kecelakaan

---

## 14. Buku Tamu (Guest Book / Appointments)

| Label | URL | Kegunaan |
|---|---|---|
| Daftar Kunjungan | `/hr/appointments` | Melihat daftar semua tamu/pengunjung yang pernah datang ke kantor. |
| Daftarkan Tamu Baru | `/hr/appointments/create` | Mencatat kunjungan tamu baru yang datang ke kantor. |
| Detail Kunjungan | `/hr/appointments/{id}` | Melihat detail informasi kunjungan tamu tertentu. |

**Kapan digunakan:**
- Ada tamu yang datang ke kantor dan perlu dicatat → Daftarkan Tamu Baru
- Ingin lihat siapa saja yang pernah berkunjung → Daftar Kunjungan

---

## 15. CMS Aktivitas

| Label | URL | Kegunaan |
|---|---|---|
| Daftar Aktivitas | `/hr/cms/activities` | Melihat dan mengelola konten aktivitas perusahaan (untuk keperluan publikasi/dokumentasi internal). |
| Buat Aktivitas | `/hr/cms/activities/create` | Membuat entri aktivitas baru. |
| Detail Aktivitas | `/hr/cms/activities/{id}` | Melihat detail suatu aktivitas. |

---

## Ringkasan Pertanyaan Umum → Menu yang Tepat

| Pertanyaan / Kebutuhan User | Menu yang Dituju | URL |
|---|---|---|
| "Saya mau lihat data karyawan" | Daftar Karyawan | `/hr/employees` |
| "Saya mau tambah karyawan baru" | Tambah Karyawan | `/hr/employees/create` |
| "Saya mau lihat absensi bulan ini" | Rekap Absensi | `/hr/attendance` |
| "Saya mau input absensi manual" | Input Absensi Manual | `/hr/attendance/create` |
| "Saya mau ajukan cuti" | Buat Pengajuan Cuti | `/hr/leaves/create` |
| "Saya mau lihat siapa yang cuti" | Daftar Cuti | `/hr/leaves` |
| "Saya mau setujui cuti karyawan" | Daftar Cuti → klik detail | `/hr/leaves` |
| "Saya mau lihat kontrak yang mau habis" | Daftar Kontrak | `/hr/contracts` |
| "Saya mau buat kontrak baru" | Buat Kontrak | `/hr/contracts/create` |
| "Saya mau perpanjang kontrak" | Perpanjang Kontrak | `/hr/contracts/{uuid}/extend` |
| "Saya mau pindahkan karyawan ke divisi lain" | Buat Mutasi | `/hr/mutation/create` |
| "Saya mau lihat jadwal shift" | Jadwal Kerja | `/hr/work_schedules` |
| "Saya mau buka lowongan" | Buat Permintaan Rekrutmen | `/hr/recruitment/requests/create` |
| "Saya mau proses kandidat pelamar" | Daftar Screening | `/hr/screening` |
| "Saya mau jadwalkan pelatihan" | Buat Jadwal Pelatihan | `/hr/trainings/schedules/create` |
| "Saya mau input nilai pelatihan" | Input Nilai Pelatihan | `/hr/trainings/grades/create` |
| "Saya mau laporkan kerusakan fasilitas" | Buat Tiket Maintenance | `/hr/maintenance-tickets/create` |
| "Saya mau daftarkan aset baru" | Tambah Aset | `/hr/assets/create` |
| "Saya mau buat surat tugas" | Buat Surat Tugas | `/hr/assignments/create` |
| "Saya mau catat tamu yang datang" | Daftarkan Tamu | `/hr/appointments/create` |
| "Saya mau laporkan kecelakaan kerja" | Buat Laporan Kecelakaan | `/hr/work-accident/create` |
| "Saya mau lihat job description jabatan tertentu" | Job Desk | `/hr/job-desk` |
