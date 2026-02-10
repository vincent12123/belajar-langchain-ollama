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