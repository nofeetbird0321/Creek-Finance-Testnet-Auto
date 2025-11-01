# Creek-Finance-Testnet-Auto

# 🤖 Creek Finance Automation Bot — SUI Testnet Automation

Skrip **Node.js** otomatis untuk menjalankan serangkaian aktivitas **DeFi di jaringan SUI Testnet**, seperti klaim faucet token, staking, deposit/borrow, repay, dan withdraw pada protokol **Creek Finance (XAUM / GUSD / USDC)**.  
Didesain agar berjalan 24 jam penuh secara otomatis untuk setiap wallet yang terdaftar.

---

## 🚀 Fitur Utama

- **Auto Faucet Management**
  - Memastikan setiap wallet memiliki saldo SUI minimal.
  - Mengulangi request faucet otomatis hingga tercapai batas minimal saldo.

- **Auto Token Claim**
  - Mengklaim token `XAUM` dan `USDC` dari faucet Creek Finance.
  - Pengulangan klaim dapat dikonfigurasi (default beberapa kali per siklus).

- **Auto Swap**
  - Melakukan swap token USDC ↔ GUSD secara otomatis.
  - Dapat diatur jumlah dan frekuensi swap.

- **Auto Staking & Redeem**
  - Staking token XAUM dan melakukan redeem otomatis sesuai konfigurasi.

- **Auto Lending Protocol**
  - Deposit collateral (GR, SUI, USDC) dan melakukan `borrow` GUSD.
  - Dapat `repay` pinjaman dan `withdraw` collateral secara otomatis.

- **Auto Health Factor Management**
  - Menghitung dan memantau *health factor* setiap wallet secara real-time.
  - Menyesuaikan jumlah deposit dan borrow agar tetap aman (> 1.5 HF).

- **Daily Scheduler (Loop 24 Jam)**
  - Bot berjalan otomatis sepanjang hari dan mengulang siklus setiap 24 jam.
  - Setiap wallet dijalankan berurutan dengan delay acak antar proses.

---

## ⚙️ Persyaratan

### 1. Instalasi Modul
Pastikan Node.js versi **18+** telah terinstal, lalu jalankan perintah:
```bash
npm install @mysten/sui.js chalk undici
```

### 2. File Konfigurasi
Skrip membutuhkan file berikut di direktori yang sama dengan `index.js`:

| File | Deskripsi |
|------|------------|
| `privatekey.txt` | Daftar private key wallet (Base64, 1 per baris). |

Contoh isi file `privatekey.txt`:
```
suiprivkey1a2b3c4d5e6f7g8h9i0jklmnopqrstuvwxyz
suiprivkey1qazwsxedcrfvtgbyhnujmikolp12345678
```

---

## 🧩 Cara Menjalankan

1. Pastikan semua dependensi sudah terinstal.
2. Simpan semua private key yang ingin digunakan di `privatekey.txt`.
3. Jalankan bot dengan perintah:
   ```bash
   node index.js
   ```
4. Bot akan memproses setiap wallet satu per satu dan menampilkan log aktivitas di terminal.

---

## ⚙️ Konfigurasi Utama

Terdapat objek `CONFIG` di bagian atas file untuk mengatur parameter penting:

| Nama Konfigurasi | Deskripsi | Default |
|------------------|------------|----------|
| `RPC_URL` | Endpoint node SUI yang digunakan | `https://sui-testnet-rpc.publicnode.com` |
| `MIN_SUI_BALANCE` | Minimal saldo SUI per wallet sebelum meminta faucet | `0.1` |
| `XAUM_CLAIM_COUNT` | Jumlah klaim faucet XAUM per siklus | `3` |
| `USDC_CLAIM_COUNT` | Jumlah klaim faucet USDC per siklus | `3` |
| `STAKE_XAUM_COUNT` | Jumlah staking XAUM | `1` |
| `DEPOSIT_GR_COUNT` | Jumlah deposit collateral GR | `1` |
| `BORROW_GUSD_COUNT` | Jumlah peminjaman token GUSD | `1` |
| `REPAY_GUSD_COUNT` | Jumlah pelunasan pinjaman | `1` |
| `WITHDRAW_COUNT` | Jumlah penarikan collateral | `1` |
| `GAS_BUDGET` | Batas gas untuk transaksi | `20000000` |
| `DELAY_MIN_MS` / `DELAY_MAX_MS` | Rentang waktu acak antar transaksi | `3000–7000 ms` |

> Semua parameter dapat disesuaikan langsung dari variabel `CONFIG` di awal skrip.

---

## 🧠 Mekanisme Kerja Bot

1. **Membaca private key** dari `privatekey.txt`.  
2. **Inisialisasi wallet** dan memeriksa saldo SUI.  
3. Jika saldo di bawah `MIN_SUI_BALANCE`, bot akan **meminta faucet otomatis**.  
4. Setelah cukup dana:
   - Melakukan klaim faucet `XAUM` dan `USDC`.  
   - Menjalankan swap, staking, deposit, borrow, repay, dan withdraw.  
   - Memantau *health factor* dan menyesuaikan jumlah transaksi.  
5. Setelah semua wallet selesai, bot menunggu 24 jam sebelum memulai ulang siklus baru.

---

## 🧾 Contoh Output Terminal

```
🔑 Memuat wallet ke-1: 0x3f2b8f1f0aa6bbdcb6ee35f7f88d1723d5a62d89
💧 Memeriksa saldo SUI... (0.02 SUI)
⚙️ Meminta faucet... [percobaan 1/5]
✅ Faucet berhasil diterima (+0.5 SUI)

💰 Klaim faucet XAUM (3x)
💰 Klaim faucet USDC (3x)
🔁 Swap USDC → GUSD
💎 Stake XAUM
🏦 Deposit GR sebagai collateral
💸 Borrow GUSD
💰 Repay GUSD
📤 Withdraw collateral
📊 Health factor: 1.83 ✅ Aman
```

---

## ⚠️ Peringatan Keamanan

> ⚡ **PENTING:**  
> - Jangan pernah membagikan file `privatekey.txt` kepada siapa pun.  
> - Selalu gunakan **Testnet** untuk pengujian.  
> - Hindari menjalankan skrip ini di **Mainnet**, karena semua transaksi dilakukan langsung dari wallet Anda.  
> - Gunakan **VPN / proxy** jika menjalankan banyak akun untuk menghindari rate limit.  
> - Simpan file konfigurasi di lokasi aman dan terenkripsi.

---

## 🔧 Troubleshooting

| Masalah | Penyebab | Solusi |
|----------|-----------|--------|
| `Cannot find module '@mysten/sui.js'` | Dependensi belum diinstal | Jalankan `npm install @mysten/sui.js` |
| `ENOENT: no such file or directory, open 'privatekey.txt'` | File belum ada | Buat file dan isi dengan private key |
| `Invalid private key format` | Format key tidak Base64 | Pastikan key valid dari wallet SUI |
| `Rate limit faucet` | Terlalu sering request faucet | Gunakan proxy atau jeda antar akun |

---

## 🧩 Struktur File Proyek

```
CreekFinanceAutoBot/
├── index.js              # Skrip utama
├── privatekey.txt        # Daftar private key wallet
├── package.json          # (Opsional) file npm
└── README.md             # Dokumentasi
```

---

## 👨‍💻 Pembuat
**Creek Finance Automation Bot**  
Dibuat oleh: **iwwwit**  
Lisensi: **MIT License**

---

## 🏁 Catatan Tambahan

Bot ini dibuat untuk tujuan **edukasi dan eksperimen otomatisasi protokol DeFi di jaringan SUI Testnet**.  
Gunakan dengan bijak dan tanggung jawab penuh atas aset Anda sendiri.
