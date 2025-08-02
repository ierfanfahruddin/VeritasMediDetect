# Layanan Deteksi Anomali Jaspel

Layanan mikro (microservice) ini berfungsi sebagai backend AI untuk aplikasi utama SIMRS. Tujuannya adalah untuk menerima data laporan jasa pelayanan (jaspel), menganalisisnya untuk menemukan potensi anomali, dan mengembalikan data yang telah diperkaya dengan catatan analisis.

Layanan ini dibangun menggunakan Python dengan framework Flask.

---

## Arsitektur & Alur Data

Sistem ini menggunakan arsitektur microservice untuk memisahkan logika AI dari aplikasi utama (PHP/CodeIgniter).

1.  **Aplikasi SIMRS (PHP):** Mengumpulkan data laporan Jaspel dari database.
2.  **Kirim Data:** Aplikasi PHP mengirimkan data tersebut dalam format JSON ke endpoint `/analyze` pada layanan ini.
3.  **Analisis AI (Python):** Layanan ini menerima data, memprosesnya menggunakan aturan-aturan yang telah didefinisikan di `app.py` untuk menemukan anomali.
4.  **Terima Hasil:** Layanan ini mengembalikan data yang sudah diperkaya dengan kolom `is_anomaly` dan `anomaly_reason`.
5.  **Tampilkan Laporan:** Aplikasi PHP menerima kembali data yang sudah dianalisis dan menampilkannya dalam laporan Excel, termasuk kolom "Analisis AI".

---

## Instalasi & Setup

Untuk menjalankan layanan ini, Anda memerlukan Python 3.8+ terinstal di sistem Anda.

1.  **Buka Terminal:** Arahkan terminal Anda ke direktori proyek ini.
    ```bash
    cd path/to/anomaly_detection_service
    ```

2.  **Buat Lingkungan Virtual (Recommended):** Ini akan mengisolasi dependensi proyek.
    ```bash
    python -m venv venv
    ```

3.  **Aktifkan Lingkungan Virtual:**
    *   **Windows:**
        ```bash
        venv\Scripts\activate
        ```
    *   **macOS/Linux:**
        ```bash
        source venv/bin/activate
        ```
    Anda akan melihat `(venv)` di awal prompt terminal Anda jika berhasil.

4.  **Instal Dependensi:** Gunakan file `requirements.txt` untuk menginstal semua library yang dibutuhkan.
    ```bash
    pip install -r requirements.txt
    ```

---

## Menjalankan Layanan

Setelah instalasi selesai, jalankan server Flask dengan perintah:

```bash
python app.py
```

Server akan berjalan di `http://127.0.0.1:5000`. Biarkan terminal ini tetap terbuka agar layanan tetap aktif. Server akan secara otomatis me-restart jika Anda membuat perubahan pada file `app.py`.

---

## Dokumentasi API

### Endpoint: `POST /analyze`

Endpoint ini adalah inti dari layanan.

*   **Method:** `POST`
*   **URL:** `http://127.0.0.1:5000/analyze`
*   **Body (Payload):** Permintaan harus berupa JSON dengan struktur spesifik berikut:
    ```json
    {
      "records": [
        { "pasien_nm": "John Doe", "lokasi_nm": "ICU", "ekg_qty": 1, "usg_qty": 0, ... },
        { "pasien_nm": "Jane Smith", "lokasi_nm": "UGD", "ekg_qty": 12, "usg_qty": 1, ... },
        ...
      ]
    }
    ```
    Kunci utamanya adalah `"records"`, yang nilainya adalah sebuah array (list) dari objek-objek (dictionary) data. Setiap objek mewakili satu baris dari laporan Anda.

*   **Response (Success):** Jika berhasil, layanan akan mengembalikan JSON dengan data yang telah dianalisis.
    ```json
    {
      "analyzed_records": [
        { "pasien_nm": "John Doe", ..., "is_anomaly": false, "anomaly_reason": "" },
        { "pasien_nm": "Jane Smith", ..., "is_anomaly": true, "anomaly_reason": "Frekuensi EKG Tinggi (>5)" }
      ]
    }


    FYI cuma repo iseng2 saja😁