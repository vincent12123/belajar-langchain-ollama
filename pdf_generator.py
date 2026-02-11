# pdf_generator.py
# Modul untuk generate surat PDF absensi

import os
import re
from datetime import date, datetime
from typing import Dict, Any, List
from fpdf import FPDF

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")

NAMA_BULAN = [
    "", "Januari", "Februari", "Maret", "April", "Mei", "Juni",
    "Juli", "Agustus", "September", "Oktober", "November", "Desember"
]


def _ensure_output_dir():
    os.makedirs(OUTPUT_DIR, exist_ok=True)


def _format_tanggal(tgl) -> str:
    """Format tanggal ke 'DD Bulan YYYY'"""
    if isinstance(tgl, str):
        tgl = datetime.strptime(tgl, "%Y-%m-%d").date()
    return f"{tgl.day} {NAMA_BULAN[tgl.month]} {tgl.year}"


def _safe_filename(text: str) -> str:
    """Konversi teks agar aman dijadikan nama file."""
    cleaned = re.sub(r"[^a-zA-Z0-9_-]+", "_", text.strip())
    return cleaned.strip("_") or "dokumen"


def _add_info_row(pdf: FPDF, label: str, value: str, value_style: str = ""):
    """Utility baris label-value untuk blok data surat."""
    pdf.set_font("Helvetica", "", 11)
    pdf.cell(40, 7, label)
    pdf.cell(5, 7, ":")
    pdf.set_font("Helvetica", value_style, 11)
    pdf.cell(0, 7, value or "-", new_x="LMARGIN", new_y="NEXT")


class SuratPDF(FPDF):
    """PDF dengan kop surat sekolah"""

    def __init__(self, school_info: Dict[str, str]):
        super().__init__()
        self.school_info = school_info
        self.set_auto_page_break(auto=True, margin=25)
        self.set_margins(15, 14, 15)

    def header(self):
        info = self.school_info
        nama_sekolah = info.get("nama_sekolah", info.get("school_name", "SMK Smart"))
        alamat = info.get("alamat", info.get("school_address", ""))
        telepon = info.get("telepon", info.get("school_phone", ""))
        email = info.get("email", info.get("school_email", ""))

        # Nama sekolah
        self.set_text_color(18, 40, 76)
        self.set_font("Helvetica", "B", 16)
        self.cell(0, 7, nama_sekolah.upper(), new_x="LMARGIN", new_y="NEXT", align="C")

        # Alamat
        self.set_text_color(80, 80, 80)
        self.set_font("Helvetica", "", 9)
        detail = alamat
        if telepon:
            detail += f"  |  Telp: {telepon}"
        if email:
            detail += f"  |  Email: {email}"
        self.cell(0, 5, detail or "-", new_x="LMARGIN", new_y="NEXT", align="C")

        self.set_text_color(0, 0, 0)

        # Garis
        self.set_draw_color(18, 40, 76)
        self.set_line_width(0.8)
        self.line(self.l_margin, self.get_y() + 2, self.w - self.r_margin, self.get_y() + 2)
        self.set_draw_color(160, 160, 160)
        self.set_line_width(0.2)
        self.line(self.l_margin, self.get_y() + 3.5, self.w - self.r_margin, self.get_y() + 3.5)
        self.set_draw_color(0, 0, 0)
        self.ln(9)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.cell(0, 10, f"Halaman {self.page_no()}/{{nb}}", align="C")


def generate_surat_peringatan(data: Dict[str, Any], school_info: Dict[str, str]) -> str:
    """Generate surat peringatan alfa untuk satu siswa. Return path file PDF."""
    _ensure_output_dir()

    siswa = data["siswa"]
    daftar_alfa = data["daftar_tanggal_alfa"]
    rekap = data["rekap"]
    persen = data["persentase_kehadiran"]

    pdf = SuratPDF(school_info)
    pdf.alias_nb_pages()
    pdf.add_page()

    hari_ini = _format_tanggal(date.today())
    tahun_ini = date.today().year
    bulan_ini = date.today().month
    kepala_sekolah = school_info.get("kepala_sekolah", school_info.get("principal_name", "Kepala Sekolah"))
    kode_sekolah = school_info.get("kode_sekolah", "SMK")
    nomor_surat = f"{len(daftar_alfa):03d}/SP-ALFA/{kode_sekolah}/{bulan_ini:02d}/{tahun_ini}"

    # Tanggal surat
    pdf.set_font("Helvetica", "", 11)
    pdf.cell(0, 6, f"Sintang, {hari_ini}", new_x="LMARGIN", new_y="NEXT", align="R")
    pdf.ln(2)

    # Perihal
    pdf.set_font("Helvetica", "", 11)
    pdf.cell(30, 6, "Nomor")
    pdf.cell(5, 6, ":")
    pdf.cell(0, 6, nomor_surat, new_x="LMARGIN", new_y="NEXT")
    pdf.cell(30, 6, "Lampiran")
    pdf.cell(5, 6, ":")
    pdf.cell(0, 6, "-", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(30, 6, "Perihal")
    pdf.cell(5, 6, ":")
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(0, 6, "Surat Peringatan Ketidakhadiran Siswa", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)

    # Kepada
    pdf.set_font("Helvetica", "", 11)
    pdf.cell(0, 6, "Kepada Yth.", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "B", 11)
    nama_ortu = siswa.get("nama_orang_tua", "-") or "-"
    pdf.cell(0, 6, f"Bapak/Ibu {nama_ortu}", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 11)
    pdf.cell(0, 6, "Orang Tua/Wali Siswa", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 6, "di Tempat", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)

    # Isi surat
    pdf.cell(0, 7, "Dengan hormat,", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)
    pdf.multi_cell(0, 7,
        "Melalui surat ini, kami sampaikan bahwa putra/putri Bapak/Ibu "
        "dengan data sebagai berikut:"
    )
    pdf.ln(2)

    # Data siswa
    _add_info_row(pdf, "   Nama", siswa.get("nama", "-"), value_style="B")
    _add_info_row(pdf, "   NIS", str(siswa.get("nis", "-")))
    _add_info_row(pdf, "   Kelas", siswa.get("kelas", "-") or "-")
    pdf.ln(2)

    pdf.multi_cell(0, 7,
        f"Tercatat tidak hadir tanpa keterangan (Alfa) sebanyak "
        f"{len(daftar_alfa)} hari pada tanggal-tanggal berikut:"
    )
    pdf.ln(2)

    # Tabel tanggal alfa
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_fill_color(230, 238, 250)
    pdf.cell(15, 7, "No", border=1, align="C", fill=True)
    pdf.cell(90, 7, "Tanggal", border=1, align="C", fill=True)
    pdf.cell(85, 7, "Status", border=1, align="C", fill=True)
    pdf.ln()

    pdf.set_font("Helvetica", "", 10)
    for i, tgl in enumerate(daftar_alfa, 1):
        pdf.cell(15, 7, str(i), border=1, align="C")
        pdf.cell(90, 7, _format_tanggal(tgl), border=1, align="C")
        pdf.cell(85, 7, "Alfa", border=1, align="C")
        pdf.ln()
    pdf.ln(4)

    # Rekap kehadiran
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(0, 7, "Rekap Kehadiran:", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_fill_color(230, 238, 250)
    pdf.cell(36, 7, "Hadir", border=1, align="C", fill=True)
    pdf.cell(36, 7, "Sakit", border=1, align="C", fill=True)
    pdf.cell(36, 7, "Izin", border=1, align="C", fill=True)
    pdf.cell(36, 7, "Alfa", border=1, align="C", fill=True)
    pdf.cell(36, 7, "Total", border=1, align="C", fill=True)
    pdf.cell(36, 7, "% Hadir", border=1, align="C", fill=True)
    pdf.ln()
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(36, 7, str(rekap.get("total_hadir", 0)), border=1, align="C")
    pdf.cell(36, 7, str(rekap.get("total_sakit", 0)), border=1, align="C")
    pdf.cell(36, 7, str(rekap.get("total_izin", 0)), border=1, align="C")
    pdf.cell(36, 7, str(rekap.get("total_alfa", 0)), border=1, align="C")
    pdf.cell(36, 7, str(rekap.get("total_hari", 0)), border=1, align="C")
    pdf.cell(36, 7, f"{persen}%", border=1, align="C")
    pdf.ln(6)

    # Penutup
    pdf.set_font("Helvetica", "", 11)
    pdf.multi_cell(0, 7,
        "Kami mengharapkan perhatian dan kerja sama Bapak/Ibu untuk memantau "
        "kehadiran putra/putri di sekolah. Apabila ada kendala, silakan "
        "menghubungi wali kelas atau pihak sekolah."
    )
    pdf.ln(2)
    pdf.cell(0, 7, "Atas perhatian dan kerja samanya, kami ucapkan terima kasih.", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(8)

    # Tanda tangan
    pdf.cell(120)
    pdf.cell(0, 6, "Hormat kami,", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(120)
    pdf.cell(0, 6, "Kepala Sekolah", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(20)
    pdf.cell(120)
    pdf.set_font("Helvetica", "BU", 11)
    pdf.cell(0, 6, kepala_sekolah, new_x="LMARGIN", new_y="NEXT")

    # Simpan
    nama_siswa = _safe_filename(siswa.get("nama", "siswa"))
    nama_file = f"surat_peringatan_{nama_siswa}_{date.today().isoformat()}.pdf"
    path = os.path.join(OUTPUT_DIR, nama_file)
    pdf.output(path)
    return path


def generate_laporan_alfa(data: Dict[str, Any], school_info: Dict[str, str]) -> str:
    """Generate laporan daftar siswa alfa harian. Return path file PDF."""
    _ensure_output_dir()

    tanggal = data["tanggal"]
    daftar = data["daftar_siswa"]
    total = data["total"]

    pdf = SuratPDF(school_info)
    pdf.alias_nb_pages()
    pdf.add_page()

    kepala_sekolah = school_info.get("kepala_sekolah", school_info.get("principal_name", "Kepala Sekolah"))

    # Judul
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 8, "LAPORAN SISWA TIDAK HADIR (ALFA)", new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.set_font("Helvetica", "", 11)
    pdf.cell(0, 7, f"Tanggal: {_format_tanggal(tanggal)}", new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(0, 7, f"Total Siswa Alfa: {total} orang", new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.ln(6)

    if total == 0:
        pdf.set_font("Helvetica", "I", 11)
        pdf.cell(0, 10, "Tidak ada siswa yang alfa pada tanggal ini.", new_x="LMARGIN", new_y="NEXT", align="C")
    else:
        # Tabel
        pdf.set_font("Helvetica", "B", 10)
        pdf.set_fill_color(230, 238, 250)
        pdf.cell(15, 7, "No", border=1, align="C", fill=True)
        pdf.cell(70, 7, "Nama Siswa", border=1, align="C", fill=True)
        pdf.cell(40, 7, "NIS", border=1, align="C", fill=True)
        pdf.cell(55, 7, "Kelas", border=1, align="C", fill=True)
        pdf.ln()

        pdf.set_font("Helvetica", "", 10)
        for i, s in enumerate(daftar, 1):
            pdf.cell(15, 7, str(i), border=1, align="C")
            pdf.cell(70, 7, s.get("nama_siswa", "-"), border=1)
            pdf.cell(40, 7, str(s.get("nis", "-")), border=1, align="C")
            pdf.cell(55, 7, s.get("kelas", "-"), border=1, align="C")
            pdf.ln()

        pdf.ln(3)
        pdf.set_font("Helvetica", "I", 10)
        pdf.cell(0, 7, "Catatan: Data berdasarkan absensi harian pada tanggal tersebut.", new_x="LMARGIN", new_y="NEXT")

    pdf.ln(10)

    # Tanda tangan
    pdf.set_font("Helvetica", "", 11)
    pdf.cell(0, 6, f"Sintang, {_format_tanggal(date.today())}", new_x="LMARGIN", new_y="NEXT", align="R")
    pdf.ln(2)
    pdf.cell(120)
    pdf.cell(0, 6, "Mengetahui,", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(120)
    pdf.cell(0, 6, "Kepala Sekolah", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(20)
    pdf.cell(120)
    pdf.set_font("Helvetica", "BU", 11)
    pdf.cell(0, 6, kepala_sekolah, new_x="LMARGIN", new_y="NEXT")

    # Simpan
    tgl_str = tanggal if isinstance(tanggal, str) else tanggal.isoformat()
    nama_file = f"laporan_alfa_{_safe_filename(tgl_str)}.pdf"
    path = os.path.join(OUTPUT_DIR, nama_file)
    pdf.output(path)
    return path
