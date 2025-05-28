**Prasyarat:**

1. **Docker Desktop Terinstal:** Pastikan Anda sudah menginstal [Docker Desktop](https://www.docker.com/products/docker-desktop/) untuk Windows. Docker Desktop sudah termasuk Docker Engine dan Docker Compose.
2. **Editor Teks:** VS Code, Sublime Text, Notepad++, atau editor lainnya.

---

## 🐳 Tutorial Integrasi Antar Service dengan Flask & Docker

Tutorial ini adalah panduan langkah demi langkah untuk membangun sistem Integrasi antar Service dasar menggunakan **Flask** dan **SQLite**, yang dijalankan dalam **kontainer Docker** menggunakan **Docker Compose**. Sistem ini terdiri dari tiga layanan independen:

1. **Provider Pengguna**: Mengelola data pengguna (di `user_data.db`, dipersistenkan via Docker Volume).
2. **Provider Produk**: Mengelola data produk (di `product_data.db`, dipersistenkan via Docker Volume).
3. **Consumer Pesanan**: Membuat pesanan dengan mengambil data dari provider (menyimpan pesanan di `order_data.db`, dipersistenkan via Docker Volume).

Komunikasi antar layanan bersifat **sinkronus** melalui API REST yang dibangun dengan Flask, berjalan dalam jaringan Docker internal.

## 📂 Struktur Direktori & Pengaturan Awal (Docker)

Mari kita siapkan struktur proyek untuk Docker.

1. **Buat Direktori Proyek**: Pilih lokasi (misalnya, Desktop atau Documents) dan buat direktori utama. Buka **Command Prompt (CMD)** atau **PowerShell**.
    
    ```bash
    :: Buat direktori utama proyek
    mkdir tutorial_services_docker
    cd tutorial_services_docker
    
    ```
    
2. **Buat Sub-Direktori Layanan**:
    
    ```bash
    mkdir user_service
    mkdir product_service
    mkdir order_service
    
    ```
    
3. **Buat File `requirements.txt` di *root* proyek**:
File ini akan digunakan oleh semua layanan.
    
    ```powershell
    # (Di dalam tutorial_services_docker)
    New-Item requirements.txt
    
    ```
    
    Buka file `requirements.txt` dengan editor teks dan tambahkan baris berikut:
    
    ```
    Flask==3.1.0
    requests==2.31.0
    
    ```
    
4. **Struktur Direktori Awal**:
    
    ```
    tutorial_services_docker/
    ├── user_service/
    ├── product_service/
    ├── order_service/
    └── requirements.txt
    
    ```
    
    *(Kita tidak perlu `venv` karena dependensi akan diinstal di dalam image Docker).*
    

## 💻 Kode Implementasi Layanan (Flask)

Salin kode `app.py` yang sama persis dari tutorial pekan lalu ke dalam direktori masing-masing layanan.

1. **Buat `user_service/app.py`**: Salin kode `app.py` untuk User Service dari tutorial asli ke sini.
    - **Penting:** Kode ini sudah siap untuk Docker karena menggunakan `host='0.0.0.0'` dan path database relatif (`os.path.join(os.path.dirname(__file__), DB_NAME)`).
2. **Buat `product_service/app.py`**: Salin kode `app.py` untuk Product Service dari tutorial asli ke sini.
    - **Penting:** Kode ini juga sudah siap untuk Docker.
3. **Buat `order_service/app.py`**: Salin kode `app.py` untuk Order Service dari tutorial asli ke sini.
    - **Penting:** Kode ini *sudah* dirancang untuk mengambil URL provider dari environment variable (`os.getenv`), yang akan kita set melalui Docker Compose. Default `localhost` akan **tidak berfungsi** antar kontainer; kita akan menggunakan nama service Docker sebagai gantinya.

## 🐳 Membuat Dockerfile untuk Setiap Layanan

Setiap layanan memerlukan `Dockerfile` untuk mendefinisikan cara membangun image containernya. Karena ketiganya mirip (aplikasi Flask dasar), Dockerfile-nya akan sangat mirip.

1. **Buat `user_service/Dockerfile`**:
    
    ```
    # user_service/Dockerfile
    FROM python:3.10-slim
    WORKDIR /app
    
    # Salin requirements.txt dari root context
    COPY requirements.txt . 
    
    RUN pip install --no-cache-dir -r requirements.txt
    
    # Salin kode aplikasi dari subdirektori user_service di dalam context
    COPY user_service/. . 
    
    EXPOSE 5001
    CMD ["python", "app.py"]
    ```
    
2. **Buat `product_service/Dockerfile`**:
(Sangat mirip, hanya beda EXPOSE port)
    
    ```
    # product_service/Dockerfile
    FROM python:3.10-slim
    WORKDIR /app
    COPY requirements.txt . 
    RUN pip install --no-cache-dir -r requirements.txt
    COPY product_service/. . 
    EXPOSE 5002
    CMD ["python", "app.py"]
    ```
    
3. **Buat `order_service/Dockerfile`**:
(Sangat mirip, hanya beda EXPOSE port)
    
    ```
    # order_service/Dockerfile
    FROM python:3.10-slim
    WORKDIR /app
    COPY requirements.txt .
    RUN pip install --no-cache-dir -r requirements.txt
    COPY order_service/. . 
    EXPOSE 5003
    CMD ["python", "app.py"]
    ```
    
4. **(Opsional tapi Direkomendasikan) Buat file `.dockerignore` di *root* proyek**:
File ini mencegah file/folder yang tidak perlu disalin ke konteks build Docker, mempercepat build dan membuat image lebih kecil.
    
    ```
    # tutorial_services_docker/.dockerignore
    __pycache__/
    *.pyc
    *.pyo
    *.pyd
    .Python
    env/
    venv/
    .git/
    .idea/
    *.db # Kita akan gunakan volume untuk database
    *.db-journal
    
    ```
    

## ⚙️ Membuat `docker-compose.yml`

File ini akan mendefinisikan dan menjalankan ketiga layanan kita bersama-sama. Buat file `docker-compose.yml` di direktori root (`tutorial_services_docker`).

```yaml
# tutorial_services_docker/docker-compose.yml
version: '3.8'

services:
  user_service:
    build:
      context: . # <-- Ubah: Konteks adalah direktori root proyek
      dockerfile: user_service/Dockerfile # <-- Tambah: Tentukan path Dockerfile
    container_name: tutorial_user_service
    ports:
      - "5001:5001"
    volumes:
      - user_data:/app
    working_dir: /app
    stop_signal: SIGINT
    restart: unless-stopped

  product_service:
    build:
      context: . # <-- Ubah: Konteks adalah direktori root proyek
      dockerfile: product_service/Dockerfile # <-- Tambah: Tentukan path Dockerfile
    container_name: tutorial_product_service
    ports:
      - "5002:5002"
    volumes:
      - product_data:/app
    working_dir: /app
    stop_signal: SIGINT
    restart: unless-stopped

  order_service:
    build:
      context: . # <-- Ubah: Konteks adalah direktori root proyek
      dockerfile: order_service/Dockerfile # <-- Tambah: Tentukan path Dockerfile
    container_name: tutorial_order_service
    ports:
      - "5003:5003"
    volumes:
      - order_data:/app
    working_dir: /app
    environment:
      USER_PROVIDER_URL: http://user_service:5001
      PRODUCT_PROVIDER_URL: http://product_service:5002
      FLASK_DEBUG: "1"
    depends_on:
      - user_service
      - product_service
    stop_signal: SIGINT
    restart: unless-stopped

volumes:
  user_data:
  product_data:
  order_data:
```

**Penjelasan `docker-compose.yml`:**

- `version`: Menentukan versi skema Docker Compose.
- `services`: Mendefinisikan setiap container (layanan).
    - `user_service`, `product_service`, `order_service`: Nama logis untuk setiap layanan. Nama ini juga berfungsi sebagai hostname dalam jaringan internal Docker yang dibuat oleh Compose.
    - `build.context`: Menunjuk ke direktori yang berisi `Dockerfile` untuk layanan tersebut.
    - `container_name`: Nama spesifik untuk container (opsional tapi membantu).
    - `ports`: Memetakan port dari mesin host Anda ke port di dalam container (`HOST:CONTAINER`). Ini memungkinkan Anda mengakses layanan dari browser atau `curl` di `localhost`.
    - `volumes`: `nama_volume:/path/dalam/container`. Kita menggunakan *named volumes* (`user_data`, `product_data`, `order_data`) yang dikelola oleh Docker. Ini memastikan file `.db` tetap ada meskipun container dihapus dan dibuat ulang. Path `/app` digunakan karena itu `WORKDIR` kita, dan `app.py` membuat DB di direktori tempat ia dijalankan.
    - `working_dir`: Menetapkan direktori kerja default di dalam container.
    - `environment`: Menetapkan variabel lingkungan di dalam container `order_service`. **Ini krusial**: `USER_PROVIDER_URL` dan `PRODUCT_PROVIDER_URL` sekarang menunjuk ke `http://<nama-service>:<port-internal>`, memungkinkan `order_service` menemukan layanan lain dalam jaringan Docker.
    - `depends_on`: Mengontrol urutan *start* container. `order_service` akan dimulai *setelah* `user_service` dan `product_service` dimulai. **Penting**: Ini tidak menjamin aplikasi di dalam container tersebut sudah siap menerima koneksi, hanya containernya yang sudah berjalan. Untuk sistem yang lebih kompleks, Anda mungkin perlu mekanisme health check atau wait-for-it script.
    - `stop_signal: SIGINT`: Mengirim sinyal yang tepat agar Flask bisa shutdown dengan baik.
    - `restart: unless-stopped`: Kebijakan restart container.
- `volumes`: Mendeklarasikan *named volumes* yang akan digunakan oleh layanan. Docker akan mengelola penyimpanan ini.

**Struktur Direktori Final:**

```
tutorial_services_docker/
├── user_service/
│   ├── app.py
│   └── Dockerfile
├── product_service/
│   ├── app.py
│   └── Dockerfile
├── order_service/
│   ├── app.py
│   └── Dockerfile
├── requirements.txt
├── docker-compose.yml
└── .dockerignore         # Opsional

```

## 🚀 Menjalankan Layanan dengan Docker Compose

Sekarang, kita bisa menjalankan semua layanan dengan satu perintah.

1. **Buka CMD atau PowerShell** di direktori root proyek (`tutorial_services_docker`).
2. **Build dan Jalankan Container**:
    
    ```bash
    docker-compose up --build
    
    ```
    
    - `-build`: Memaksa Docker Compose untuk membangun image dari Dockerfile (penting saat pertama kali atau jika Anda mengubah Dockerfile/kode).
    - Perintah ini akan:
        - Membangun image Docker untuk setiap layanan (jika belum ada atau `-build` digunakan).
        - Membuat dan memulai container untuk setiap layanan.
        - Membuat jaringan Docker default agar container bisa saling berkomunikasi.
        - Melampirkan terminal Anda ke output log gabungan dari semua container.
        - Anda akan melihat output inisialisasi database dan log Flask dari ketiga layanan.
3. **Menjalankan di Latar Belakang (Detached Mode)**:
Jika Anda ingin terminal kembali bebas setelah container berjalan, gunakan flag `d`:
    
    ```bash
    docker-compose up --build -d
    
    ```
    
    Untuk melihat log jika berjalan di detached mode:
    
    ```bash
    docker-compose logs -f
    
    ```
    
    (`-f` untuk mengikuti log secara real-time). Tekan `Ctrl+C` untuk berhenti mengikuti log (container tetap berjalan).
    

## 🧪 Contoh Penggunaan (Interaksi API)

Karena kita memetakan port container ke `localhost` di `docker-compose.yml`, Anda bisa menggunakan `curl` (dari CMD/PowerShell baru) atau Postman **persis seperti pada tutorial pekan lalu**, menargetkan `http://localhost:5001`, `http://localhost:5002`, dan `http://localhost:5003`.

**Penggunaan Postman:**

Instruksi Postman dari tutorial pekan lalu **tetap berlaku** tanpa perubahan, karena Anda masih berinteraksi dengan `localhost` pada port yang dipetakan (5001, 5002, 5003).

## 🛑 Menghentikan Layanan

Untuk menghentikan dan menghapus container, jaringan, dan (opsional) volume:

1. Buka CMD/PowerShell di direktori `tutorial_services_docker`.
2. Jalankan:
    
    ```bash
    docker-compose down
    
    ```
    
    Untuk menghapus volume juga (data SQLite akan hilang!):
    
    ```bash
    docker-compose down -v
    
    ```
    

---

Tutorial ini sekarang sepenuhnya di-Dockerisasi, menyediakan lingkungan pengembangan yang konsisten dan terisolasi untuk aplikasi microservice Flask .