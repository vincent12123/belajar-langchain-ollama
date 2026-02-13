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


def get_daftar_kelas() -> List[Dict[str, Any]]:
    """Ambil daftar semua kelas aktif (id, nama, tingkat, jurusan, wali_kelas)"""
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute("""
        SELECT k.id, k.nama, k.tingkat, k.jurusan, k.wali_kelas
        FROM kelas k
        WHERE k.deleted_at IS NULL
        ORDER BY k.tingkat ASC, k.nama ASC
    """)
    result = cursor.fetchall()
    cursor.close()
    db.close()
    return result


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


def get_attendance_trends(
    siswa_id: Optional[int] = None,
    nama_siswa: Optional[str] = None,
    kelas_id: Optional[int] = None,
    nama_kelas: Optional[str] = None,
    months: int = 6
) -> Dict[str, Any]:
    """Analyze attendance trends for a student or class over multiple months to identify patterns and improvements/deteriorations"""
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    # Resolve student ID if name provided
    if not siswa_id and nama_siswa:
        siswa_id = _resolve_siswa_id(cursor, nama_siswa)
        if not siswa_id:
            cursor.close()
            db.close()
            return {"error": f"Siswa dengan nama '{nama_siswa}' tidak ditemukan atau ada lebih dari satu hasil. Gunakan fungsi cari_siswa untuk mencari dulu."}

    # Resolve class ID if name provided
    if not kelas_id and nama_kelas:
        kelas_id = _resolve_kelas_id(cursor, nama_kelas)
        if not kelas_id:
            cursor.close()
            db.close()
            return {"error": f"Kelas dengan nama '{nama_kelas}' tidak ditemukan atau ada lebih dari satu hasil. Coba gunakan nama kelas yang lebih spesifik."}

    # Build query based on whether we're analyzing student or class
    if siswa_id:
        query = """
            SELECT
                YEAR(a.tanggal) AS tahun,
                MONTH(a.tanggal) AS bulan,
                COUNT(CASE WHEN a.status = 'Hadir' THEN 1 END) AS hadir,
                COUNT(*) AS total_hari,
                ROUND(COUNT(CASE WHEN a.status = 'Hadir' THEN 1 END) * 100.0 / COUNT(*), 1) AS persen_hadir
            FROM absensi a
            WHERE a.siswa_id = %s
            GROUP BY YEAR(a.tanggal), MONTH(a.tanggal)
            ORDER BY tahun DESC, bulan DESC
            LIMIT %s
        """
        params = [siswa_id, months]
    elif kelas_id:
        query = """
            SELECT
                YEAR(a.tanggal) AS tahun,
                MONTH(a.tanggal) AS bulan,
                COUNT(CASE WHEN a.status = 'Hadir' THEN 1 END) AS hadir,
                COUNT(*) AS total_hari,
                ROUND(COUNT(CASE WHEN a.status = 'Hadir' THEN 1 END) * 100.0 / COUNT(*), 1) AS persen_hadir
            FROM absensi a
            WHERE a.kelas_id = %s
            GROUP BY YEAR(a.tanggal), MONTH(a.tanggal)
            ORDER BY tahun DESC, bulan DESC
            LIMIT %s
        """
        params = [kelas_id, months]
    else:
        cursor.close()
        db.close()
        return {"error": "Harus menyertakan siswa_id/nama_siswa atau kelas_id/nama_kelas"}

    cursor.execute(query, params)
    monthly_data = cursor.fetchall()

    # Calculate trends (improvement/deterioration)
    for i in range(len(monthly_data) - 1):
        current_percentage = monthly_data[i]["persen_hadir"]
        next_percentage = monthly_data[i + 1]["persen_hadir"]
        if current_percentage > next_percentage:
            monthly_data[i]["trend"] = "meningkat"
        elif current_percentage < next_percentage:
            monthly_data[i]["trend"] = "menurun"
        else:
            monthly_data[i]["trend"] = "stabil"

    # Last entry has no comparison
    if monthly_data:
        monthly_data[-1]["trend"] = "terbaru"

    cursor.close()
    db.close()

    return {
        "periode_analisis": f"{months} bulan terakhir",
        "data": monthly_data
    }


def get_geolocation_analysis(
    kelas_id: Optional[int] = None,
    nama_kelas: Optional[str] = None,
    tanggal: Optional[str] = None
) -> Dict[str, Any]:
    """Analyze geolocation data for attendance validation and detect anomalies in student locations"""
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    # Resolve class ID if name provided
    if not kelas_id and nama_kelas:
        kelas_id = _resolve_kelas_id(cursor, nama_kelas)
        if not kelas_id:
            cursor.close()
            db.close()
            return {"error": f"Kelas dengan nama '{nama_kelas}' tidak ditemukan atau ada lebih dari satu hasil. Coba gunakan nama kelas yang lebih spesifik."}

    # Base query for geolocation analysis
    query = """
        SELECT
            a.id,
            s.nama AS nama_siswa,
            s.nis,
            k.nama AS kelas,
            a.tanggal,
            a.latitude,
            a.longitude,
            a.status
        FROM absensi a
        JOIN siswa s ON a.siswa_id = s.id
        JOIN kelas k ON a.kelas_id = k.id
        WHERE a.latitude IS NOT NULL AND a.longitude IS NOT NULL
    """
    params = []

    # Add filters
    if kelas_id:
        query += " AND a.kelas_id = %s"
        params.append(kelas_id)

    if tanggal:
        query += " AND a.tanggal = %s"
        params.append(tanggal)

    query += " ORDER BY a.tanggal DESC, k.nama, s.nama LIMIT 100"

    cursor.execute(query, params)
    records = cursor.fetchall()

    # Statistics
    total_records = len(records)
    valid_coordinates = len([r for r in records if r["latitude"] and r["longitude"]])
    percentage_valid = round((valid_coordinates / total_records * 100), 1) if total_records > 0 else 0

    # Detect anomalies (simplified - identical coordinates for multiple students)
    coordinate_groups = {}
    for record in records:
        coord_key = f"{record['latitude']},{record['longitude']}"
        if coord_key not in coordinate_groups:
            coordinate_groups[coord_key] = []
        coordinate_groups[coord_key].append(record)

    # Find groups with multiple students at same location
    suspicious_locations = []
    for coord_key, group in coordinate_groups.items():
        if len(group) > 3:  # More than 3 students at same location is suspicious
            suspicious_locations.append({
                "coordinates": coord_key,
                "student_count": len(group),
                "students": [f"{s['nama_siswa']} ({s['nis']})" for s in group[:5]],  # Show first 5
                "tanggal": group[0]["tanggal"]
            })

    cursor.close()
    db.close()

    return {
        "total_records": total_records,
        "valid_coordinates": valid_coordinates,
        "percentage_valid_coordinates": percentage_valid,
        "suspicious_locations": suspicious_locations[:10],  # Limit to 10 suspicious cases
        "flagged_records_count": len(suspicious_locations)
    }


def compare_class_attendance(
    tingkat: Optional[int] = None,
    jurusan: Optional[str] = None
) -> Dict[str, Any]:
    """Compare attendance rates between different classes to identify patterns and performance differences"""
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    # Query to get class attendance statistics
    query = """
        SELECT
            k.id AS kelas_id,
            k.nama AS kelas,
            COUNT(CASE WHEN a.status = 'Hadir' THEN 1 END) AS hadir,
            COUNT(*) AS total_hari,
            ROUND(COUNT(CASE WHEN a.status = 'Hadir' THEN 1 END) * 100.0 / COUNT(*), 1) AS persen_hadir
        FROM absensi a
        JOIN kelas k ON a.kelas_id = k.id
        WHERE 1=1
    """
    params = []

    # Add filters
    if tingkat:
        query += " AND k.tingkat = %s"
        params.append(tingkat)

    if jurusan:
        query += " AND k.jurusan = %s"
        params.append(jurusan)

    query += """
        GROUP BY k.id, k.nama
        HAVING total_hari > 0
        ORDER BY persen_hadir DESC
    """

    cursor.execute(query, params)
    class_stats = cursor.fetchall()

    # Calculate overall statistics
    if class_stats:
        avg_attendance = round(sum(c["persen_hadir"] for c in class_stats) / len(class_stats), 1)
        best_class = class_stats[0]
        worst_class = class_stats[-1]
    else:
        avg_attendance = 0
        best_class = None
        worst_class = None

    cursor.close()
    db.close()

    return {
        "filter_tingkat": tingkat,
        "filter_jurusan": jurusan,
        "total_kelas": len(class_stats),
        "rata_rata_kehadiran": avg_attendance,
        "kelas_terbaik": best_class,
        "kelas_terendah": worst_class,
        "perbandingan_kelas": class_stats
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
# ==========================
# Tambahan Kategori A (Absensi Lanjutan)
# ==========================

def get_ringkasan_absensi_harian(
    kelas_id: Optional[int] = None,
    nama_kelas: Optional[str] = None,
    tanggal: Optional[str] = None
) -> Dict[str, Any]:
    """
    Ringkasan absensi 1 kelas pada 1 tanggal: total Hadir/Izin/Sakit/Alfa + persentase hadir.
    Cocok untuk dashboard harian wali kelas.
    """
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    if not kelas_id and nama_kelas:
        kelas_id = _resolve_kelas_id(cursor, nama_kelas)
        if not kelas_id:
            cursor.close()
            db.close()
            return {"error": f"Kelas dengan nama '{nama_kelas}' tidak ditemukan atau ada lebih dari satu hasil. Coba gunakan nama kelas yang lebih spesifik."}

    if not kelas_id:
        cursor.close()
        db.close()
        return {"error": "Harus menyertakan kelas_id atau nama_kelas"}

    if not tanggal:
        tanggal = date.today().isoformat()

    query = """
        SELECT
            k.nama AS kelas,
            a.tanggal,
            COUNT(*) AS total_record,
            COUNT(CASE WHEN a.status = 'Hadir' THEN 1 END) AS hadir,
            COUNT(CASE WHEN a.status = 'Izin' THEN 1 END)  AS izin,
            COUNT(CASE WHEN a.status = 'Sakit' THEN 1 END) AS sakit,
            COUNT(CASE WHEN a.status = 'Alfa' THEN 1 END)  AS alfa,
            ROUND(COUNT(CASE WHEN a.status = 'Hadir' THEN 1 END) * 100.0 / COUNT(*), 1) AS persen_hadir
        FROM absensi a
        JOIN kelas k ON a.kelas_id = k.id
        WHERE a.kelas_id = %s AND a.tanggal = %s
        GROUP BY k.nama, a.tanggal
    """
    cursor.execute(query, [kelas_id, tanggal])
    summary = cursor.fetchone()

    # Jika tidak ada record, tetap kembalikan struktur yang konsisten
    if not summary:
        cursor.execute("SELECT nama FROM kelas WHERE id = %s LIMIT 1", [kelas_id])
        row = cursor.fetchone()
        kelas_nama = row["nama"] if row else None
        summary = {
            "kelas": kelas_nama,
            "tanggal": tanggal,
            "total_record": 0,
            "hadir": 0,
            "izin": 0,
            "sakit": 0,
            "alfa": 0,
            "persen_hadir": 0
        }

    cursor.close()
    db.close()
    return summary


def get_ringkasan_absensi_range(
    kelas_id: Optional[int] = None,
    nama_kelas: Optional[str] = None,
    tanggal_mulai: str = "",
    tanggal_akhir: str = ""
) -> Dict[str, Any]:
    """
    Ringkasan absensi per hari untuk 1 kelas pada rentang tanggal (untuk grafik/tren).
    Return: list per tanggal: total/hadir/izin/sakit/alfa/persen_hadir
    """
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    if not kelas_id and nama_kelas:
        kelas_id = _resolve_kelas_id(cursor, nama_kelas)
        if not kelas_id:
            cursor.close()
            db.close()
            return {"error": f"Kelas dengan nama '{nama_kelas}' tidak ditemukan atau ada lebih dari satu hasil. Coba gunakan nama kelas yang lebih spesifik."}

    if not kelas_id:
        cursor.close()
        db.close()
        return {"error": "Harus menyertakan kelas_id atau nama_kelas"}

    if not tanggal_mulai or not tanggal_akhir:
        cursor.close()
        db.close()
        return {"error": "Harus menyertakan tanggal_mulai dan tanggal_akhir (format YYYY-MM-DD)"}

    query = """
        SELECT
            a.tanggal,
            COUNT(*) AS total_record,
            COUNT(CASE WHEN a.status = 'Hadir' THEN 1 END) AS hadir,
            COUNT(CASE WHEN a.status = 'Izin' THEN 1 END)  AS izin,
            COUNT(CASE WHEN a.status = 'Sakit' THEN 1 END) AS sakit,
            COUNT(CASE WHEN a.status = 'Alfa' THEN 1 END)  AS alfa,
            ROUND(COUNT(CASE WHEN a.status = 'Hadir' THEN 1 END) * 100.0 / COUNT(*), 1) AS persen_hadir
        FROM absensi a
        WHERE a.kelas_id = %s
          AND a.tanggal BETWEEN %s AND %s
        GROUP BY a.tanggal
        ORDER BY a.tanggal ASC
    """
    cursor.execute(query, [kelas_id, tanggal_mulai, tanggal_akhir])
    rows = cursor.fetchall()

    cursor.close()
    db.close()
    return {
        "kelas_id": kelas_id,
        "tanggal_mulai": tanggal_mulai,
        "tanggal_akhir": tanggal_akhir,
        "data": rows
    }


def get_rekap_absensi_kelas_range(
    kelas_id: Optional[int] = None,
    nama_kelas: Optional[str] = None,
    tanggal_mulai: str = "",
    tanggal_akhir: str = ""
) -> Dict[str, Any]:
    """
    Rekap absensi per siswa untuk 1 kelas pada rentang tanggal.
    Output: list siswa + total Hadir/Izin/Sakit/Alfa + total_record.
    """
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    if not kelas_id and nama_kelas:
        kelas_id = _resolve_kelas_id(cursor, nama_kelas)
        if not kelas_id:
            cursor.close()
            db.close()
            return {"error": f"Kelas dengan nama '{nama_kelas}' tidak ditemukan atau ada lebih dari satu hasil. Coba gunakan nama kelas yang lebih spesifik."}

    if not kelas_id:
        cursor.close()
        db.close()
        return {"error": "Harus menyertakan kelas_id atau nama_kelas"}

    if not tanggal_mulai or not tanggal_akhir:
        cursor.close()
        db.close()
        return {"error": "Harus menyertakan tanggal_mulai dan tanggal_akhir (format YYYY-MM-DD)"}

    query = """
        SELECT
            s.id AS siswa_id,
            s.nama AS nama_siswa,
            s.nis,
            COUNT(*) AS total_record,
            COUNT(CASE WHEN a.status = 'Hadir' THEN 1 END) AS hadir,
            COUNT(CASE WHEN a.status = 'Izin' THEN 1 END)  AS izin,
            COUNT(CASE WHEN a.status = 'Sakit' THEN 1 END) AS sakit,
            COUNT(CASE WHEN a.status = 'Alfa' THEN 1 END)  AS alfa,
            ROUND(COUNT(CASE WHEN a.status = 'Hadir' THEN 1 END) * 100.0 / COUNT(*), 1) AS persen_hadir
        FROM absensi a
        JOIN siswa s ON a.siswa_id = s.id
        WHERE a.kelas_id = %s
          AND a.tanggal BETWEEN %s AND %s
        GROUP BY s.id, s.nama, s.nis
        ORDER BY alfa DESC, izin DESC, sakit DESC, s.nama ASC
    """
    cursor.execute(query, [kelas_id, tanggal_mulai, tanggal_akhir])
    rows = cursor.fetchall()

    cursor.close()
    db.close()
    return {
        "kelas_id": kelas_id,
        "tanggal_mulai": tanggal_mulai,
        "tanggal_akhir": tanggal_akhir,
        "data": rows
    }


def get_top_siswa_absensi(
    kelas_id: Optional[int] = None,
    nama_kelas: Optional[str] = None,
    tanggal_mulai: str = "",
    tanggal_akhir: str = "",
    status: str = "Alfa",
    limit: int = 10
) -> Dict[str, Any]:
    """
    Ambil top siswa dengan jumlah status tertentu (default: Alfa) pada rentang tanggal.
    Cocok untuk 'top offender' atau monitoring kasus.
    """
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    if not kelas_id and nama_kelas:
        kelas_id = _resolve_kelas_id(cursor, nama_kelas)
        if not kelas_id:
            cursor.close()
            db.close()
            return {"error": f"Kelas dengan nama '{nama_kelas}' tidak ditemukan atau ada lebih dari satu hasil. Coba gunakan nama kelas yang lebih spesifik."}

    if not kelas_id:
        cursor.close()
        db.close()
        return {"error": "Harus menyertakan kelas_id atau nama_kelas"}

    if not tanggal_mulai or not tanggal_akhir:
        cursor.close()
        db.close()
        return {"error": "Harus menyertakan tanggal_mulai dan tanggal_akhir (format YYYY-MM-DD)"}

    query = """
        SELECT
            s.id AS siswa_id,
            s.nama AS nama_siswa,
            s.nis,
            COUNT(*) AS total
        FROM absensi a
        JOIN siswa s ON a.siswa_id = s.id
        WHERE a.kelas_id = %s
          AND a.tanggal BETWEEN %s AND %s
          AND a.status = %s
        GROUP BY s.id, s.nama, s.nis
        HAVING total > 0
        ORDER BY total DESC, s.nama ASC
        LIMIT %s
    """
    cursor.execute(query, [kelas_id, tanggal_mulai, tanggal_akhir, status, limit])
    rows = cursor.fetchall()

    cursor.close()
    db.close()
    return {
        "kelas_id": kelas_id,
        "tanggal_mulai": tanggal_mulai,
        "tanggal_akhir": tanggal_akhir,
        "status": status,
        "limit": limit,
        "data": rows
    }


def get_analisis_metode_absen(
    kelas_id: Optional[int] = None,
    nama_kelas: Optional[str] = None,
    tanggal_mulai: str = "",
    tanggal_akhir: str = ""
) -> Dict[str, Any]:
    """
    Analisis metode absen (field: metode) untuk satu kelas pada rentang tanggal.
    Output: ringkasan per metode + breakdown status per metode.
    """
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    if not kelas_id and nama_kelas:
        kelas_id = _resolve_kelas_id(cursor, nama_kelas)
        if not kelas_id:
            cursor.close()
            db.close()
            return {"error": f"Kelas dengan nama '{nama_kelas}' tidak ditemukan atau ada lebih dari satu hasil. Coba gunakan nama kelas yang lebih spesifik."}

    if not kelas_id:
        cursor.close()
        db.close()
        return {"error": "Harus menyertakan kelas_id atau nama_kelas"}

    if not tanggal_mulai or not tanggal_akhir:
        cursor.close()
        db.close()
        return {"error": "Harus menyertakan tanggal_mulai dan tanggal_akhir (format YYYY-MM-DD)"}

    query = """
        SELECT
            a.metode,
            COUNT(*) AS total,
            COUNT(CASE WHEN a.status = 'Hadir' THEN 1 END) AS hadir,
            COUNT(CASE WHEN a.status = 'Izin' THEN 1 END)  AS izin,
            COUNT(CASE WHEN a.status = 'Sakit' THEN 1 END) AS sakit,
            COUNT(CASE WHEN a.status = 'Alfa' THEN 1 END)  AS alfa,
            ROUND(COUNT(CASE WHEN a.status = 'Hadir' THEN 1 END) * 100.0 / COUNT(*), 1) AS persen_hadir
        FROM absensi a
        WHERE a.kelas_id = %s
          AND a.tanggal BETWEEN %s AND %s
        GROUP BY a.metode
        ORDER BY total DESC, a.metode ASC
    """
    cursor.execute(query, [kelas_id, tanggal_mulai, tanggal_akhir])
    rows = cursor.fetchall()

    cursor.close()
    db.close()
    return {
        "kelas_id": kelas_id,
        "tanggal_mulai": tanggal_mulai,
        "tanggal_akhir": tanggal_akhir,
        "data": rows
    }


def get_anomali_absensi(
    kelas_id: Optional[int] = None,
    nama_kelas: Optional[str] = None,
    tanggal_mulai: str = "",
    tanggal_akhir: str = "",
    max_jarak_meter: int = 200,
    min_siswa_sama_koordinat: int = 4,
    limit: int = 100
) -> Dict[str, Any]:
    """
    Deteksi anomali absensi (khususnya geolokasi & data GPS):
    1) jarak_meter > max_jarak_meter
    2) metode != 'manual' tapi latitude/longitude null
    3) banyak siswa share koordinat yang sama pada tanggal yang sama (indikasi 'titip absen')
    """
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    if not kelas_id and nama_kelas:
        kelas_id = _resolve_kelas_id(cursor, nama_kelas)
        if not kelas_id:
            cursor.close()
            db.close()
            return {"error": f"Kelas dengan nama '{nama_kelas}' tidak ditemukan atau ada lebih dari satu hasil. Coba gunakan nama kelas yang lebih spesifik."}

    if not kelas_id:
        cursor.close()
        db.close()
        return {"error": "Harus menyertakan kelas_id atau nama_kelas"}

    if not tanggal_mulai or not tanggal_akhir:
        cursor.close()
        db.close()
        return {"error": "Harus menyertakan tanggal_mulai dan tanggal_akhir (format YYYY-MM-DD)"}

    # 1) Jarak terlalu jauh
    far_query = """
        SELECT
            a.id,
            a.tanggal,
            s.nama AS nama_siswa,
            s.nis,
            a.status,
            a.metode,
            a.waktu_absen,
            a.jarak_meter,
            a.latitude,
            a.longitude
        FROM absensi a
        JOIN siswa s ON a.siswa_id = s.id
        WHERE a.kelas_id = %s
          AND a.tanggal BETWEEN %s AND %s
          AND a.jarak_meter IS NOT NULL
          AND a.jarak_meter > %s
        ORDER BY a.jarak_meter DESC, a.tanggal DESC
        LIMIT %s
    """
    cursor.execute(far_query, [kelas_id, tanggal_mulai, tanggal_akhir, max_jarak_meter, limit])
    far_distance = cursor.fetchall()

    # 2) Metode non-manual tapi koordinat kosong
    missing_geo_query = """
        SELECT
            a.id,
            a.tanggal,
            s.nama AS nama_siswa,
            s.nis,
            a.status,
            a.metode,
            a.waktu_absen,
            a.latitude,
            a.longitude
        FROM absensi a
        JOIN siswa s ON a.siswa_id = s.id
        WHERE a.kelas_id = %s
          AND a.tanggal BETWEEN %s AND %s
          AND a.metode <> 'manual'
          AND (a.latitude IS NULL OR a.longitude IS NULL)
        ORDER BY a.tanggal DESC, s.nama ASC
        LIMIT %s
    """
    cursor.execute(missing_geo_query, [kelas_id, tanggal_mulai, tanggal_akhir, limit])
    missing_geolocation = cursor.fetchall()

    # 3) Banyak siswa dengan koordinat identik di tanggal yang sama
    group_query = """
        SELECT
            a.tanggal,
            a.latitude,
            a.longitude,
            COUNT(*) AS jumlah_siswa
        FROM absensi a
        WHERE a.kelas_id = %s
          AND a.tanggal BETWEEN %s AND %s
          AND a.latitude IS NOT NULL
          AND a.longitude IS NOT NULL
        GROUP BY a.tanggal, a.latitude, a.longitude
        HAVING jumlah_siswa >= %s
        ORDER BY jumlah_siswa DESC, a.tanggal DESC
        LIMIT 20
    """
    cursor.execute(group_query, [kelas_id, tanggal_mulai, tanggal_akhir, min_siswa_sama_koordinat])
    groups = cursor.fetchall()

    suspicious_shared_coordinates = []
    detail_query = """
        SELECT
            s.nama AS nama_siswa,
            s.nis,
            a.status,
            a.metode,
            a.waktu_absen
        FROM absensi a
        JOIN siswa s ON a.siswa_id = s.id
        WHERE a.kelas_id = %s
          AND a.tanggal = %s
          AND a.latitude = %s
          AND a.longitude = %s
        ORDER BY s.nama ASC
        LIMIT 15
    """
    for g in groups:
        cursor.execute(detail_query, [kelas_id, g["tanggal"], g["latitude"], g["longitude"]])
        siswa_list = cursor.fetchall()
        suspicious_shared_coordinates.append({
            "tanggal": g["tanggal"],
            "latitude": g["latitude"],
            "longitude": g["longitude"],
            "jumlah_siswa": g["jumlah_siswa"],
            "sampel_siswa": siswa_list
        })

    cursor.close()
    db.close()

    return {
        "kelas_id": kelas_id,
        "tanggal_mulai": tanggal_mulai,
        "tanggal_akhir": tanggal_akhir,
        "max_jarak_meter": max_jarak_meter,
        "min_siswa_sama_koordinat": min_siswa_sama_koordinat,
        "far_distance": far_distance,
        "missing_geolocation": missing_geolocation,
        "suspicious_shared_coordinates": suspicious_shared_coordinates
    }


def get_statistik_waktu_absen(
    kelas_id: Optional[int] = None,
    nama_kelas: Optional[str] = None,
    tanggal_mulai: str = "",
    tanggal_akhir: str = "",
    jam_telat: str = "07:15:00",
    limit: int = 10
) -> Dict[str, Any]:
    """
    Statistik waktu_absen untuk 1 kelas pada rentang tanggal:
    - distribusi per jam
    - total telat (waktu_absen > jam_telat) khusus status Hadir
    - top siswa telat
    """
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    if not kelas_id and nama_kelas:
        kelas_id = _resolve_kelas_id(cursor, nama_kelas)
        if not kelas_id:
            cursor.close()
            db.close()
            return {"error": f"Kelas dengan nama '{nama_kelas}' tidak ditemukan atau ada lebih dari satu hasil. Coba gunakan nama kelas yang lebih spesifik."}

    if not kelas_id:
        cursor.close()
        db.close()
        return {"error": "Harus menyertakan kelas_id atau nama_kelas"}

    if not tanggal_mulai or not tanggal_akhir:
        cursor.close()
        db.close()
        return {"error": "Harus menyertakan tanggal_mulai dan tanggal_akhir (format YYYY-MM-DD)"}

    # Distribusi per jam
    dist_query = """
        SELECT
            HOUR(a.waktu_absen) AS jam,
            COUNT(*) AS total
        FROM absensi a
        WHERE a.kelas_id = %s
          AND a.tanggal BETWEEN %s AND %s
          AND a.waktu_absen IS NOT NULL
        GROUP BY HOUR(a.waktu_absen)
        ORDER BY jam ASC
    """
    cursor.execute(dist_query, [kelas_id, tanggal_mulai, tanggal_akhir])
    distribusi_per_jam = cursor.fetchall()

    # Total telat (khusus Hadir)
    telat_query = """
        SELECT
            COUNT(*) AS total_telat
        FROM absensi a
        WHERE a.kelas_id = %s
          AND a.tanggal BETWEEN %s AND %s
          AND a.status = 'Hadir'
          AND a.waktu_absen IS NOT NULL
          AND a.waktu_absen > %s
    """
    cursor.execute(telat_query, [kelas_id, tanggal_mulai, tanggal_akhir, jam_telat])
    total_telat_row = cursor.fetchone() or {"total_telat": 0}

    # Top siswa telat
    top_telat_query = """
        SELECT
            s.id AS siswa_id,
            s.nama AS nama_siswa,
            s.nis,
            COUNT(*) AS total_telat,
            MAX(a.waktu_absen) AS telat_terparah
        FROM absensi a
        JOIN siswa s ON a.siswa_id = s.id
        WHERE a.kelas_id = %s
          AND a.tanggal BETWEEN %s AND %s
          AND a.status = 'Hadir'
          AND a.waktu_absen IS NOT NULL
          AND a.waktu_absen > %s
        GROUP BY s.id, s.nama, s.nis
        ORDER BY total_telat DESC, telat_terparah DESC
        LIMIT %s
    """
    cursor.execute(top_telat_query, [kelas_id, tanggal_mulai, tanggal_akhir, jam_telat, limit])
    top_telat = cursor.fetchall()

    cursor.close()
    db.close()

    return {
        "kelas_id": kelas_id,
        "tanggal_mulai": tanggal_mulai,
        "tanggal_akhir": tanggal_akhir,
        "jam_telat": jam_telat,
        "distribusi_per_jam": distribusi_per_jam,
        "total_telat": total_telat_row["total_telat"],
        "top_telat": top_telat
    }


# ==========================
# Laporan Structured: Kepsek & Guru
# ==========================

def get_laporan_kepsek_range(
    tanggal_mulai: str = "",
    tanggal_akhir: str = "",
    tingkat: Optional[int] = None,
    jurusan: Optional[str] = None,
    threshold_kehadiran: float = 85.0
) -> Dict[str, Any]:
    """
    Laporan ringkasan range untuk kepala sekolah: lintas kelas, ranking,
    alerts otomatis (LOW_ATTENDANCE_CLASS, HIGH_ALFA_CLASS).
    Output sesuai format structured 'kepsek_ringkasan_range'.
    """
    from datetime import datetime

    if not tanggal_mulai or not tanggal_akhir:
        return {"error": "Harus menyertakan tanggal_mulai dan tanggal_akhir (format YYYY-MM-DD)"}

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    # ── 1) Ranking per kelas ──
    ranking_query = """
        SELECT
            k.id   AS kelas_id,
            k.nama AS kelas,
            COUNT(*) AS total_record,
            COUNT(CASE WHEN a.status = 'Hadir' THEN 1 END) AS hadir,
            COUNT(CASE WHEN a.status = 'Izin'  THEN 1 END) AS izin,
            COUNT(CASE WHEN a.status = 'Sakit' THEN 1 END) AS sakit,
            COUNT(CASE WHEN a.status = 'Alfa'  THEN 1 END) AS alfa,
            ROUND(COUNT(CASE WHEN a.status = 'Hadir' THEN 1 END) * 100.0 / COUNT(*), 2) AS persen_hadir
        FROM absensi a
        JOIN kelas k ON a.kelas_id = k.id
        WHERE a.tanggal BETWEEN %s AND %s
    """
    params: list = [tanggal_mulai, tanggal_akhir]

    if tingkat:
        ranking_query += " AND k.tingkat = %s"
        params.append(tingkat)
    if jurusan:
        ranking_query += " AND k.jurusan = %s"
        params.append(jurusan)

    ranking_query += """
        GROUP BY k.id, k.nama
        HAVING total_record > 0
        ORDER BY persen_hadir DESC
    """
    cursor.execute(ranking_query, params)
    ranking_kelas = cursor.fetchall()

    # ── 2) Summary aggregat ──
    total_kelas = len(ranking_kelas)
    total_record = sum(r["total_record"] for r in ranking_kelas)
    total_hadir = sum(r["hadir"] for r in ranking_kelas)
    total_izin  = sum(r["izin"]  for r in ranking_kelas)
    total_sakit = sum(r["sakit"] for r in ranking_kelas)
    total_alfa  = sum(r["alfa"]  for r in ranking_kelas)
    rata_rata   = round(total_hadir * 100.0 / total_record, 2) if total_record else 0

    # Jumlah hari unik yang ter-record
    cursor.execute(
        "SELECT COUNT(DISTINCT tanggal) AS hari FROM absensi WHERE tanggal BETWEEN %s AND %s",
        [tanggal_mulai, tanggal_akhir]
    )
    hari_row = cursor.fetchone()
    total_hari_tercatat = hari_row["hari"] if hari_row else 0

    # Jumlah siswa unik
    siswa_params: list = [tanggal_mulai, tanggal_akhir]
    siswa_query = "SELECT COUNT(DISTINCT siswa_id) AS jml FROM absensi a JOIN kelas k ON a.kelas_id = k.id WHERE a.tanggal BETWEEN %s AND %s"
    if tingkat:
        siswa_query += " AND k.tingkat = %s"
        siswa_params.append(tingkat)
    if jurusan:
        siswa_query += " AND k.jurusan = %s"
        siswa_params.append(jurusan)
    cursor.execute(siswa_query, siswa_params)
    siswa_row = cursor.fetchone()
    total_siswa = siswa_row["jml"] if siswa_row else 0

    # ── 3) Alerts otomatis ──
    alerts = []
    for r in ranking_kelas:
        if r["persen_hadir"] < threshold_kehadiran:
            alerts.append({
                "type": "LOW_ATTENDANCE_CLASS",
                "message": f"Kehadiran kelas {r['kelas']} di bawah {threshold_kehadiran}% pada periode ini ({r['persen_hadir']}%).",
                "kelas_id": r["kelas_id"],
                "kelas": r["kelas"],
                "value": float(r["persen_hadir"])
            })
        if r["alfa"] >= 10:
            alerts.append({
                "type": "HIGH_ALFA_CLASS",
                "message": f"Alfa tinggi pada kelas {r['kelas']} ({r['alfa']} kejadian).",
                "kelas_id": r["kelas_id"],
                "kelas": r["kelas"],
                "value": int(r["alfa"])
            })

    cursor.close()
    db.close()

    return {
        "report_type": "kepsek_ringkasan_range",
        "scope": {
            "tanggal_mulai": tanggal_mulai,
            "tanggal_akhir": tanggal_akhir,
            "filter_tingkat": tingkat,
            "filter_jurusan": jurusan,
            "include_weekends": True
        },
        "summary": {
            "total_kelas": total_kelas,
            "total_siswa": total_siswa,
            "total_hari_tercatat": total_hari_tercatat,
            "breakdown_total": {
                "Hadir": total_hadir,
                "Izin": total_izin,
                "Sakit": total_sakit,
                "Alfa": total_alfa
            },
            "rata_rata_persen_hadir": rata_rata
        },
        "ranking_kelas": ranking_kelas,
        "alerts": alerts,
        "generated_at": datetime.now().isoformat()
    }


def get_laporan_guru_harian(
    kelas_id: Optional[int] = None,
    nama_kelas: Optional[str] = None,
    tanggal: Optional[str] = None
) -> Dict[str, Any]:
    """
    Laporan absensi harian detail untuk guru/wali kelas:
    daftar setiap siswa beserta status, metode, waktu_absen, dan
    deteksi siswa yang belum punya record absensi di tanggal tersebut.
    Output sesuai format structured 'guru_absensi_harian_detail'.
    """
    from datetime import datetime

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    # Resolve kelas
    if not kelas_id and nama_kelas:
        kelas_id = _resolve_kelas_id(cursor, nama_kelas)
        if not kelas_id:
            cursor.close()
            db.close()
            return {"error": f"Kelas dengan nama '{nama_kelas}' tidak ditemukan atau ada lebih dari satu hasil. Coba gunakan nama kelas yang lebih spesifik."}

    if not kelas_id:
        cursor.close()
        db.close()
        return {"error": "Harus menyertakan kelas_id atau nama_kelas"}

    if not tanggal:
        tanggal = date.today().isoformat()

    # Ambil nama kelas
    cursor.execute("SELECT nama FROM kelas WHERE id = %s LIMIT 1", [kelas_id])
    kelas_row = cursor.fetchone()
    kelas_nama = kelas_row["nama"] if kelas_row else None

    # ── 1) Daftar siswa aktif di kelas ──
    cursor.execute("""
        SELECT s.id AS siswa_id, s.nama, s.nis
        FROM penempatan_kelas pk
        JOIN siswa s ON pk.siswa_id = s.id
        WHERE pk.kelas_id = %s AND pk.status = 'aktif'
              AND s.deleted_at IS NULL
        ORDER BY s.nama
    """, [kelas_id])
    siswa_aktif = cursor.fetchall()
    siswa_id_set = {s["siswa_id"] for s in siswa_aktif}

    # ── 2) Record absensi yang sudah ada ──
    cursor.execute("""
        SELECT
            a.siswa_id,
            s.nis,
            s.nama,
            a.status,
            a.metode,
            a.waktu_absen
        FROM absensi a
        JOIN siswa s ON a.siswa_id = s.id
        WHERE a.kelas_id = %s AND a.tanggal = %s
        ORDER BY s.nama
    """, [kelas_id, tanggal])
    records = cursor.fetchall()

    # Build students list & track recorded IDs
    students = []
    recorded_ids = set()
    counts = {"Hadir": 0, "Izin": 0, "Sakit": 0, "Alfa": 0}

    for r in records:
        recorded_ids.add(r["siswa_id"])
        status = r["status"]
        if status in counts:
            counts[status] += 1

        waktu = r["waktu_absen"]
        if waktu is not None:
            waktu = str(waktu)  # timedelta → string

        students.append({
            "siswa_id": r["siswa_id"],
            "nis": r["nis"],
            "nama": r["nama"],
            "status": status,
            "metode": r["metode"],
            "waktu_absen": waktu,
            "catatan": None       # tabel absensi belum punya kolom catatan
        })

    # ── 3) Siswa aktif tanpa record (missing) ──
    missing_records = []
    for s in siswa_aktif:
        if s["siswa_id"] not in recorded_ids:
            missing_records.append({
                "siswa_id": s["siswa_id"],
                "nis": s["nis"],
                "nama": s["nama"],
                "note": "Belum ada record absensi di tanggal ini"
            })

    total_siswa = len(siswa_aktif)
    persen_hadir = round(counts["Hadir"] * 100.0 / total_siswa, 2) if total_siswa else 0

    cursor.close()
    db.close()

    return {
        "report_type": "guru_absensi_harian_detail",
        "scope": {
            "tanggal": tanggal,
            "kelas_id": kelas_id,
            "kelas": kelas_nama
        },
        "summary": {
            "total_siswa": total_siswa,
            "counts": counts,
            "persen_hadir": persen_hadir
        },
        "students": students,
        "missing_records": missing_records,
        "generated_at": datetime.now().isoformat()
    }
