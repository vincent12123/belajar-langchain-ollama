# db_functions.py
# Fungsi-fungsi SQL query untuk mengambil data absensi

import mysql.connector
from datetime import date
from typing import Optional, List, Dict, Any
from config import DB_CONFIG


def get_db_connection():
    """Buat koneksi baru ke database"""
    return mysql.connector.connect(**DB_CONFIG)


def _resolve_siswa_id(cursor, nama_siswa: str) -> Optional[int]:
    """Cari siswa_id berdasarkan nama (LIKE search). Return ID jika ditemukan tepat 1."""
    cursor.execute(
        "SELECT id FROM siswa WHERE nama LIKE %s AND deleted_at IS NULL LIMIT 2",
        [f"%{nama_siswa}%"]
    )
    rows = cursor.fetchall()
    if len(rows) == 1:
        return rows[0]["id"]
    return None


def _resolve_kelas_id(cursor, nama_kelas: str) -> Optional[int]:
    """Cari kelas_id berdasarkan nama (LIKE search). Return ID jika ditemukan tepat 1."""
    cursor.execute(
        "SELECT id FROM kelas WHERE nama LIKE %s AND deleted_at IS NULL LIMIT 2",
        [f"%{nama_kelas}%"]
    )
    rows = cursor.fetchall()
    if len(rows) == 1:
        return rows[0]["id"]
    return None


def cari_siswa(nama: str) -> List[Dict[str, Any]]:
    """Cari siswa berdasarkan nama (pencarian parsial)"""
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    query = """
        SELECT s.id, s.nama, s.nis, s.status,
               k.nama AS kelas
        FROM siswa s
        LEFT JOIN penempatan_kelas pk ON pk.siswa_id = s.id AND pk.status = 'aktif'
        LEFT JOIN kelas k ON pk.kelas_id = k.id
        WHERE s.nama LIKE %s AND s.deleted_at IS NULL
        ORDER BY s.nama
        LIMIT 10
    """
    cursor.execute(query, [f"%{nama}%"])
    result = cursor.fetchall()

    cursor.close()
    db.close()
    return result


def get_siswa_by_kelas(
    kelas_id: Optional[int] = None,
    nama_kelas: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Ambil daftar siswa dalam satu kelas (bisa pakai ID atau nama kelas)"""
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    if not kelas_id and nama_kelas:
        kelas_id = _resolve_kelas_id(cursor, nama_kelas)
        if not kelas_id:
            cursor.close()
            db.close()
            return [{"error": f"Kelas dengan nama '{nama_kelas}' tidak ditemukan atau ada lebih dari satu hasil. Coba gunakan nama kelas yang lebih spesifik."}]

    if not kelas_id:
        cursor.close()
        db.close()
        return [{"error": "Harus menyertakan kelas_id atau nama_kelas"}]

    query = """
        SELECT s.id, s.nama, s.nis, s.status,
               k.nama AS kelas
        FROM penempatan_kelas pk
        JOIN siswa s ON pk.siswa_id = s.id
        JOIN kelas k ON pk.kelas_id = k.id
        WHERE pk.kelas_id = %s AND pk.status = 'aktif'
              AND s.deleted_at IS NULL
        ORDER BY s.nama
    """
    cursor.execute(query, [kelas_id])
    result = cursor.fetchall()

    cursor.close()
    db.close()
    return result


def get_absensi_by_siswa(
    siswa_id: Optional[int] = None,
    nama_siswa: Optional[str] = None,
    tanggal_mulai: Optional[str] = None,
    tanggal_akhir: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Ambil data absensi berdasarkan siswa (bisa pakai ID atau nama)"""
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    if not siswa_id and nama_siswa:
        siswa_id = _resolve_siswa_id(cursor, nama_siswa)
        if not siswa_id:
            cursor.close()
            db.close()
            return [{"error": f"Siswa dengan nama '{nama_siswa}' tidak ditemukan atau ada lebih dari satu hasil. Gunakan fungsi cari_siswa untuk mencari dulu."}]

    if not siswa_id:
        cursor.close()
        db.close()
        return [{"error": "Harus menyertakan siswa_id atau nama_siswa"}]

    query = """
        SELECT 
            s.nama AS nama_siswa,
            s.nis,
            k.nama AS kelas,
            a.tanggal,
            a.status
        FROM absensi a
        JOIN siswa s ON a.siswa_id = s.id
        JOIN kelas k ON a.kelas_id = k.id
        WHERE a.siswa_id = %s
    """
    params = [siswa_id]

    if tanggal_mulai and tanggal_akhir:
        query += " AND a.tanggal BETWEEN %s AND %s"
        params.extend([tanggal_mulai, tanggal_akhir])

    query += " ORDER BY a.tanggal DESC LIMIT 50"
    cursor.execute(query, params)
    result = cursor.fetchall()

    cursor.close()
    db.close()
    return result


def get_absensi_by_kelas(
    kelas_id: Optional[int] = None,
    nama_kelas: Optional[str] = None,
    tanggal: str = ""
) -> List[Dict[str, Any]]:
    """Ambil data absensi seluruh siswa dalam satu kelas (bisa pakai ID atau nama kelas)"""
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    if not kelas_id and nama_kelas:
        kelas_id = _resolve_kelas_id(cursor, nama_kelas)
        if not kelas_id:
            cursor.close()
            db.close()
            return [{"error": f"Kelas dengan nama '{nama_kelas}' tidak ditemukan atau ada lebih dari satu hasil. Coba gunakan nama kelas yang lebih spesifik."}]

    if not kelas_id:
        cursor.close()
        db.close()
        return [{"error": "Harus menyertakan kelas_id atau nama_kelas"}]

    if not tanggal:
        tanggal = date.today().isoformat()

    query = """
        SELECT 
            s.nama AS nama_siswa,
            s.nis,
            a.status
        FROM absensi a
        JOIN siswa s ON a.siswa_id = s.id
        WHERE a.kelas_id = %s AND a.tanggal = %s
        ORDER BY s.nama
    """
    cursor.execute(query, [kelas_id, tanggal])
    result = cursor.fetchall()

    cursor.close()
    db.close()
    return result


def get_siswa_tidak_hadir(
    tanggal: Optional[str] = None,
    status: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Ambil daftar siswa yang tidak hadir"""
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    if not tanggal:
        tanggal = date.today().isoformat()

    query = """
        SELECT 
            s.nama AS nama_siswa,
            s.nis,
            k.nama AS kelas,
            a.status
        FROM absensi a
        JOIN siswa s ON a.siswa_id = s.id
        JOIN kelas k ON a.kelas_id = k.id
        WHERE a.tanggal = %s AND a.status != 'Hadir'
    """
    params = [tanggal]

    if status:
        query += " AND a.status = %s"
        params.append(status)

    query += " ORDER BY k.nama, s.nama"
    cursor.execute(query, params)
    result = cursor.fetchall()

    cursor.close()
    db.close()
    return result


def get_rekap_absensi(
    siswa_id: Optional[int] = None,
    nama_siswa: Optional[str] = None,
    bulan: Optional[int] = None,
    tahun: Optional[int] = None
) -> Optional[Dict[str, Any]]:
    """Hitung rekap absensi siswa (bisa pakai ID atau nama)"""
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    if not siswa_id and nama_siswa:
        siswa_id = _resolve_siswa_id(cursor, nama_siswa)
        if not siswa_id:
            cursor.close()
            db.close()
            return {"error": f"Siswa dengan nama '{nama_siswa}' tidak ditemukan atau ada lebih dari satu hasil. Gunakan fungsi cari_siswa untuk mencari dulu."}

    if not siswa_id:
        cursor.close()
        db.close()
        return {"error": "Harus menyertakan siswa_id atau nama_siswa"}

    query = """
        SELECT 
            s.nama AS nama_siswa,
            s.nis,
            COUNT(CASE WHEN a.status = 'hadir' THEN 1 END) AS total_hadir,
            COUNT(CASE WHEN a.status = 'sakit' THEN 1 END) AS total_sakit,
            COUNT(CASE WHEN a.status = 'izin' THEN 1 END)  AS total_izin,
            COUNT(CASE WHEN a.status = 'alfa' THEN 1 END)  AS total_alfa,
            COUNT(*) AS total_hari
        FROM absensi a
        JOIN siswa s ON a.siswa_id = s.id
        WHERE a.siswa_id = %s
    """
    params = [siswa_id]

    if bulan:
        query += " AND MONTH(a.tanggal) = %s"
        params.append(bulan)
    if tahun:
        query += " AND YEAR(a.tanggal) = %s"
        params.append(tahun)

    query += " GROUP BY s.id, s.nama, s.nis"
    cursor.execute(query, params)
    result = cursor.fetchone()

    cursor.close()
    db.close()
    return result


def get_rekap_absensi_bulanan(
    nama_siswa: Optional[str] = None,
    siswa_id: Optional[int] = None,
    tahun: Optional[int] = None
) -> Dict[str, Any]:
    """Rekap absensi siswa per bulan, diurutkan berdasarkan bulan"""
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    if not siswa_id and nama_siswa:
        siswa_id = _resolve_siswa_id(cursor, nama_siswa)
        if not siswa_id:
            cursor.close()
            db.close()
            return {"error": f"Siswa dengan nama '{nama_siswa}' tidak ditemukan atau ada lebih dari satu hasil. Gunakan fungsi cari_siswa untuk mencari dulu."}

    if not siswa_id:
        cursor.close()
        db.close()
        return {"error": "Harus menyertakan siswa_id atau nama_siswa"}

    # Ambil info siswa
    cursor.execute("""
        SELECT s.nama, s.nis, k.nama AS kelas
        FROM siswa s
        LEFT JOIN penempatan_kelas pk ON pk.siswa_id = s.id AND pk.status = 'aktif'
        LEFT JOIN kelas k ON pk.kelas_id = k.id
        WHERE s.id = %s
    """, [siswa_id])
    info_siswa = cursor.fetchone()

    # Rekap per bulan
    query = """
        SELECT
            YEAR(a.tanggal) AS tahun,
            MONTH(a.tanggal) AS bulan,
            COUNT(CASE WHEN a.status = 'Hadir' THEN 1 END) AS hadir,
            COUNT(CASE WHEN a.status = 'Sakit' THEN 1 END) AS sakit,
            COUNT(CASE WHEN a.status = 'Izin' THEN 1 END)  AS izin,
            COUNT(CASE WHEN a.status = 'Alfa' THEN 1 END)  AS alfa,
            COUNT(*) AS total_hari,
            ROUND(COUNT(CASE WHEN a.status = 'Hadir' THEN 1 END) * 100.0 / COUNT(*), 1) AS persen_hadir
        FROM absensi a
        WHERE a.siswa_id = %s
    """
    params = [siswa_id]

    if tahun:
        query += " AND YEAR(a.tanggal) = %s"
        params.append(tahun)

    query += " GROUP BY YEAR(a.tanggal), MONTH(a.tanggal) ORDER BY tahun, bulan"
    cursor.execute(query, params)
    rekap_bulanan = cursor.fetchall()

    cursor.close()
    db.close()

    return {
        "siswa": info_siswa,
        "rekap_per_bulan": rekap_bulanan
    }


def get_persentase_kehadiran(
    siswa_id: Optional[int] = None,
    nama_siswa: Optional[str] = None,
    kelas_id: Optional[int] = None,
    nama_kelas: Optional[str] = None,
    bulan: Optional[int] = None,
    tahun: Optional[int] = None
) -> Optional[Dict[str, Any]]:
    """Hitung persentase kehadiran siswa atau kelas"""
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    if not siswa_id and nama_siswa:
        siswa_id = _resolve_siswa_id(cursor, nama_siswa)
        if not siswa_id:
            cursor.close()
            db.close()
            return {"error": f"Siswa dengan nama '{nama_siswa}' tidak ditemukan atau ada lebih dari satu hasil. Gunakan fungsi cari_siswa untuk mencari dulu."}

    if not kelas_id and not siswa_id and nama_kelas:
        kelas_id = _resolve_kelas_id(cursor, nama_kelas)
        if not kelas_id:
            cursor.close()
            db.close()
            return {"error": f"Kelas dengan nama '{nama_kelas}' tidak ditemukan atau ada lebih dari satu hasil. Coba gunakan nama kelas yang lebih spesifik."}

    if siswa_id:
        query = """
            SELECT 
                s.nama AS nama_siswa,
                ROUND(
                    COUNT(CASE WHEN a.status = 'hadir' THEN 1 END) * 100.0 / COUNT(*), 2
                ) AS persentase_kehadiran
            FROM absensi a
            JOIN siswa s ON a.siswa_id = s.id
            WHERE a.siswa_id = %s
        """
        params = [siswa_id]
    elif kelas_id:
        query = """
            SELECT 
                k.nama AS kelas,
                ROUND(
                    COUNT(CASE WHEN a.status = 'hadir' THEN 1 END) * 100.0 / COUNT(*), 2
                ) AS persentase_kehadiran
            FROM absensi a
            JOIN kelas k ON a.kelas_id = k.id
            WHERE a.kelas_id = %s
        """
        params = [kelas_id]
    else:
        return {"error": "Harus menyertakan siswa_id atau kelas_id"}

    if bulan:
        query += " AND MONTH(a.tanggal) = %s"
        params.append(bulan)
    if tahun:
        query += " AND YEAR(a.tanggal) = %s"
        params.append(tahun)

    cursor.execute(query, params)
    result = cursor.fetchone()

    cursor.close()
    db.close()
    return result


def get_school_settings() -> Dict[str, str]:
    """Ambil info sekolah dari tabel settings"""
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    cursor.execute("SELECT `key`, `value` FROM settings")
    rows = cursor.fetchall()

    cursor.close()
    db.close()

    settings = {}
    for row in rows:
        settings[row["key"]] = row["value"] or ""
    return settings


def get_data_alfa_siswa(
    nama_siswa: Optional[str] = None,
    siswa_id: Optional[int] = None
) -> Dict[str, Any]:
    """Ambil data lengkap siswa yang alfa: info siswa, daftar tanggal alfa, dan rekap kehadiran"""
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    if not siswa_id and nama_siswa:
        siswa_id = _resolve_siswa_id(cursor, nama_siswa)
        if not siswa_id:
            cursor.close()
            db.close()
            return {"error": f"Siswa dengan nama '{nama_siswa}' tidak ditemukan atau ada lebih dari satu hasil. Gunakan fungsi cari_siswa untuk mencari dulu."}

    if not siswa_id:
        cursor.close()
        db.close()
        return {"error": "Harus menyertakan siswa_id atau nama_siswa"}

    # Info siswa + kelas
    cursor.execute("""
        SELECT s.nama, s.nis, s.nama_orang_tua, s.whatsapp_orang_tua,
               k.nama AS kelas
        FROM siswa s
        LEFT JOIN penempatan_kelas pk ON pk.siswa_id = s.id AND pk.status = 'aktif'
        LEFT JOIN kelas k ON pk.kelas_id = k.id
        WHERE s.id = %s
    """, [siswa_id])
    info = cursor.fetchone()

    # Daftar tanggal alfa
    cursor.execute("""
        SELECT a.tanggal
        FROM absensi a
        WHERE a.siswa_id = %s AND a.status = 'Alfa'
        ORDER BY a.tanggal
    """, [siswa_id])
    daftar_alfa = [row["tanggal"] for row in cursor.fetchall()]

    # Rekap kehadiran total
    cursor.execute("""
        SELECT
            COUNT(CASE WHEN a.status = 'Hadir' THEN 1 END) AS total_hadir,
            COUNT(CASE WHEN a.status = 'Sakit' THEN 1 END) AS total_sakit,
            COUNT(CASE WHEN a.status = 'Izin' THEN 1 END)  AS total_izin,
            COUNT(CASE WHEN a.status = 'Alfa' THEN 1 END)  AS total_alfa,
            COUNT(*) AS total_hari
        FROM absensi a
        WHERE a.siswa_id = %s
    """, [siswa_id])
    rekap = cursor.fetchone()

    cursor.close()
    db.close()

    persen = 0.0
    if rekap and rekap["total_hari"] > 0:
        persen = round(rekap["total_hadir"] * 100.0 / rekap["total_hari"], 1)

    return {
        "siswa": info,
        "daftar_tanggal_alfa": daftar_alfa,
        "rekap": rekap,
        "persentase_kehadiran": persen
    }


def get_data_alfa_harian(
    tanggal: Optional[str] = None
) -> Dict[str, Any]:
    """Ambil daftar semua siswa yang alfa pada tanggal tertentu"""
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    if not tanggal:
        tanggal = date.today().isoformat()

    cursor.execute("""
        SELECT s.nama AS nama_siswa, s.nis, k.nama AS kelas
        FROM absensi a
        JOIN siswa s ON a.siswa_id = s.id
        JOIN kelas k ON a.kelas_id = k.id
        WHERE a.tanggal = %s AND a.status = 'Alfa'
        ORDER BY k.nama, s.nama
    """, [tanggal])
    daftar = cursor.fetchall()

    cursor.close()
    db.close()

    return {
        "tanggal": tanggal,
        "total": len(daftar),
        "daftar_siswa": daftar
    }


def buat_surat_peringatan_alfa(
    nama_siswa: Optional[str] = None,
    siswa_id: Optional[int] = None
) -> Dict[str, Any]:
    """Buat surat peringatan PDF untuk siswa yang alfa"""
    from pdf_generator import generate_surat_peringatan

    data = get_data_alfa_siswa(nama_siswa=nama_siswa, siswa_id=siswa_id)
    if "error" in data:
        return data

    if not data["daftar_tanggal_alfa"]:
        nama = data["siswa"].get("nama", nama_siswa or siswa_id)
        return {"pesan": f"Siswa {nama} tidak memiliki catatan alfa. Surat tidak dibuat."}

    school_info = get_school_settings()
    path = generate_surat_peringatan(data, school_info)
    return {
        "pesan": f"Surat peringatan berhasil dibuat untuk {data['siswa']['nama']}",
        "file": path,
        "total_alfa": len(data["daftar_tanggal_alfa"]),
        "persentase_kehadiran": data["persentase_kehadiran"]
    }


def buat_laporan_alfa(
    tanggal: Optional[str] = None
) -> Dict[str, Any]:
    """Buat laporan PDF daftar siswa alfa pada tanggal tertentu"""
    from pdf_generator import generate_laporan_alfa

    data = get_data_alfa_harian(tanggal=tanggal)
    school_info = get_school_settings()
    path = generate_laporan_alfa(data, school_info)
    return {
        "pesan": f"Laporan alfa berhasil dibuat untuk tanggal {data['tanggal']}",
        "file": path,
        "total_siswa_alfa": data["total"]
    }