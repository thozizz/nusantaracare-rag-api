# NusantaraCare RAG API

**Asisten AI berbasis RAG (Retrieval-Augmented Generation) untuk dokumen internal NusantaraCare.**

Layanan API ini memungkinkan karyawan NusantaraCare mendapatkan jawaban cepat dan akurat dari dokumen kebijakan dan SOP internal, lengkap dengan kutipan sumber yang dapat diverifikasi.

---

## 📌 1. Problem & Success Criteria

### Tujuan Bisnis
Karyawan NusantaraCare kesulitan mencari jawaban dari dokumen internal yang panjang dan tersebar. Pencarian keyword biasa (Ctrl+F) tidak efektif karena tidak memahami konteks pertanyaan. Selain itu, jawaban yang diberikan harus dapat dipertanggungjawabkan dan memiliki sumber yang jelas.

### Kriteria Sukses
1. Sistem dapat menjawab pertanyaan berdasarkan dokumen internal yang **aktif** (v2.0).
2. Setiap jawaban **wajib menyertakan kutipan sumber** (citation) yang valid.
3. Sistem **menolak** pertanyaan di luar cakupan dokumen (out-of-scope).
4. Sistem **tahan terhadap prompt injection** (instruksi berbahaya).
5. API dapat diakses publik melalui internet (FastAPI Cloud).

### Jenis Pertanyaan yang Ditargetkan
- SOP permintaan akses aplikasi
- Prosedur pelaporan gangguan/insiden
- Aturan pengadaan perlengkapan kerja
- Ketentuan prioritas tiket (P1, P2, P3)
- Batasan data dan kerahasiaan dalam tiket

### Batasan Sistem
- Hanya menjawab berdasarkan **satu dokumen** (`nusantaracare_panduan_operasional_internal_v2.md`)
- Tidak mencakup konsultasi medis, nasihat hukum, atau perhitungan gaji
- Hanya mendukung teks (tidak ada multimodal)

---

## 📚 2. Knowledge Base Understanding

### Sumber Dokumen
- **Nama Dokumen**: Panduan Operasional Layanan Internal NusantaraCare v2.0
- **File**: `data/raw_docs/nusantaracare_panduan_operasional_internal_v2.md`

### Metadata Utama
| Field | Value |
| :--- | :--- |
| `doc_id` | NC-OPS-001 |
| `doc_title` | Panduan Operasional Layanan Internal NusantaraCare |
| `doc_version` | 2.0 |
| `effective_date` | 2026-07-01 |
| `is_active` | `true` |
| `owner` | Direktorat Operasi dan Layanan Internal |
| `source_path` | `data/raw_docs/nusantaracare_panduan_operasional_internal_v2.md` |

### Struktur Dokumen
Dokumen terdiri dari 12 bagian utama:
1. Tujuan, Ruang Lingkup, dan Status Dokumen
2. Istilah dan Peran
3. Kanal Layanan dan Waktu Operasional
4. Klasifikasi Permintaan dan Prioritas
5. SOP Permintaan Akses dan Akun
6. SOP Gangguan Layanan dan Eskalasi
7. SOP Fasilitas dan Perlengkapan Kerja
8. Kebijakan Data, Kerahasiaan, dan Batas Layanan
9. Status Tiket, SLA, dan Komunikasi Pemohon
10. FAQ Operasional
11. Lampiran Matriks Keputusan
12. Riwayat Perubahan dan Arsip Kebijakan

### Perbedaan v1.4 (NONAKTIF) vs v2.0 (AKTIF)
| Aspek | v1.4 (Nonaktif) | v2.0 (Aktif) |
| :--- | :--- | :--- |
| **Saluran Permintaan** | Email biasa setara dengan portal | Hanya portal; email hanya jika portal down + penanda `[DARURAT-PORTAL]` |
| **Batas Pengajuan Perlengkapan** | 3 hari kerja | 5 hari kerja |
| **Status** | `is_active: false` | `is_active: true` |

Sistem secara otomatis **mengecualikan** semua chunk yang mengandung kata "Arsip Kebijakan v1.4" atau "NONAKTIF" saat *retrieval*.

---

## 🧠 3. RAG Design & Data Preparation

### A. Chunking Strategy
- **Metode**: Berbasis heading (section) dokumen
- **Ukuran**: Tidak ditentukan secara kaku; setiap section dijadikan satu chunk karena dokumen sudah terstruktur dengan baik
- **Alasan**: Section dalam dokumen sudah merepresentasikan satu topik utuh, sehingga memotong lebih lanjut berisiko memutus konteks

### B. Metadata per Chunk
Setiap chunk menyimpan metadata berikut:

```json
{
  "chunk_id": "NC-OPS-001#chunk-001",
  "section_title": "Tujuan, Ruang Lingkup, dan Status Dokumen",
  "metadata": {
    "doc_id": "NC-OPS-001",
    "doc_title": "Panduan Operasional Layanan Internal NusantaraCare",
    "doc_version": "2.0",
    "is_active": true,
    "category": "kebijakan_dan_sop_layanan_internal",
    "effective_date": "2026-07-01"
  }
}