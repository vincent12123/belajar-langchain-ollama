# tools_definition.py
# Definisi tools untuk function calling (OpenAI format)

tools = [
    {
        "type": "function",
        "function": {
            "name": "cari_siswa",
            "description": "Mencari data siswa berdasarkan nama (pencarian parsial). Gunakan ini ketika user menyebut nama siswa dan kamu perlu mencari ID-nya.",
            "parameters": {
                "type": "object",
                "properties": {
                    "nama": {
                        "type": "string",
                        "description": "Nama siswa yang dicari (bisa sebagian nama)"
                    }
                },
                "required": ["nama"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_siswa_by_kelas",
            "description": "Mengambil daftar semua siswa dalam satu kelas. Bisa menggunakan ID kelas atau nama kelas.",
            "parameters": {
                "type": "object",
                "properties": {
                    "kelas_id": {
                        "type": "integer",
                        "description": "ID kelas (opsional jika nama_kelas diisi)"
                    },
                    "nama_kelas": {
                        "type": "string",
                        "description": "Nama kelas, misal 'X RPL 1', 'XI TKJ 2' (opsional jika kelas_id diisi)"
                    }
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_absensi_by_siswa",
            "description": "Mengambil data absensi/kehadiran berdasarkan siswa. Bisa menggunakan ID siswa atau nama siswa.",
            "parameters": {
                "type": "object",
                "properties": {
                    "siswa_id": {
                        "type": "integer",
                        "description": "ID unik siswa di database (opsional jika nama_siswa diisi)"
                    },
                    "nama_siswa": {
                        "type": "string",
                        "description": "Nama siswa, bisa sebagian nama (opsional jika siswa_id diisi)"
                    },
                    "tanggal_mulai": {
                        "type": "string",
                        "description": "Tanggal mulai dalam format YYYY-MM-DD (opsional)"
                    },
                    "tanggal_akhir": {
                        "type": "string",
                        "description": "Tanggal akhir dalam format YYYY-MM-DD (opsional)"
                    }
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_absensi_by_kelas",
            "description": "Mengambil data absensi seluruh siswa dalam satu kelas pada tanggal tertentu. Bisa menggunakan ID kelas atau nama kelas.",
            "parameters": {
                "type": "object",
                "properties": {
                    "kelas_id": {
                        "type": "integer",
                        "description": "ID kelas (opsional jika nama_kelas diisi)"
                    },
                    "nama_kelas": {
                        "type": "string",
                        "description": "Nama kelas, misal 'X RPL 1', 'XI TKJ 2' (opsional jika kelas_id diisi)"
                    },
                    "tanggal": {
                        "type": "string",
                        "description": "Tanggal absensi dalam format YYYY-MM-DD. Default: hari ini"
                    }
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_siswa_tidak_hadir",
            "description": "Mengambil daftar siswa yang tidak hadir (alfa/sakit/izin) pada hari tertentu",
            "parameters": {
                "type": "object",
                "properties": {
                    "tanggal": {
                        "type": "string",
                        "description": "Tanggal dalam format YYYY-MM-DD. Default: hari ini"
                    },
                    "status": {
                        "type": "string",
                        "enum": ["alfa", "sakit", "izin"],
                        "description": "Filter berdasarkan status ketidakhadiran (opsional)"
                    }
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_rekap_absensi",
            "description": "Menghitung rekap/ringkasan absensi siswa (total hadir, sakit, izin, alfa). Bisa menggunakan ID siswa atau nama siswa.",
            "parameters": {
                "type": "object",
                "properties": {
                    "siswa_id": {
                        "type": "integer",
                        "description": "ID unik siswa (opsional jika nama_siswa diisi)"
                    },
                    "nama_siswa": {
                        "type": "string",
                        "description": "Nama siswa, bisa sebagian nama (opsional jika siswa_id diisi)"
                    },
                    "bulan": {
                        "type": "integer",
                        "description": "Bulan (1-12), opsional"
                    },
                    "tahun": {
                        "type": "integer",
                        "description": "Tahun (contoh: 2026), opsional"
                    }
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_rekap_absensi_bulanan",
            "description": "Menampilkan rekap absensi siswa yang dikelompokkan per bulan (hadir, sakit, izin, alfa, persentase kehadiran tiap bulan). Gunakan ini ketika user menyebut nama siswa dan ingin melihat rekap absensinya. Bisa menggunakan ID siswa atau nama siswa.",
            "parameters": {
                "type": "object",
                "properties": {
                    "nama_siswa": {
                        "type": "string",
                        "description": "Nama siswa, bisa sebagian nama"
                    },
                    "siswa_id": {
                        "type": "integer",
                        "description": "ID siswa (opsional jika nama_siswa diisi)"
                    },
                    "tahun": {
                        "type": "integer",
                        "description": "Filter tahun tertentu (contoh: 2026), opsional"
                    }
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_persentase_kehadiran",
            "description": "Menghitung persentase kehadiran. Bisa per siswa, per kelas, atau seluruh sekolah (tanpa siswa/kelas). Bisa filter bulan dan tahun.",
            "parameters": {
                "type": "object",
                "properties": {
                    "siswa_id": {
                        "type": "integer",
                        "description": "ID siswa (opsional)"
                    },
                    "nama_siswa": {
                        "type": "string",
                        "description": "Nama siswa, bisa sebagian nama (opsional, alternatif dari siswa_id)"
                    },
                    "kelas_id": {
                        "type": "integer",
                        "description": "ID kelas (opsional)"
                    },
                    "nama_kelas": {
                        "type": "string",
                        "description": "Nama kelas, misal 'X RPL 1' (opsional, alternatif dari kelas_id)"
                    },
                    "bulan": {
                        "type": "integer",
                        "description": "Bulan (1-12)"
                    },
                    "tahun": {
                        "type": "integer",
                        "description": "Tahun (contoh: 2026)"
                    }
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "buat_surat_peringatan_alfa",
            "description": "Membuat surat peringatan dalam bentuk PDF untuk siswa yang alfa (tidak hadir tanpa keterangan). Surat berisi kop sekolah, data siswa, daftar tanggal alfa, rekap kehadiran, dan tanda tangan kepala sekolah.",
            "parameters": {
                "type": "object",
                "properties": {
                    "nama_siswa": {
                        "type": "string",
                        "description": "Nama siswa yang akan dibuatkan surat peringatan"
                    },
                    "siswa_id": {
                        "type": "integer",
                        "description": "ID siswa (opsional jika nama_siswa diisi)"
                    }
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "buat_laporan_alfa",
            "description": "Membuat laporan PDF daftar semua siswa yang alfa (tidak hadir tanpa keterangan) pada tanggal tertentu. Berisi kop sekolah, tabel daftar siswa alfa, dan tanda tangan.",
            "parameters": {
                "type": "object",
                "properties": {
                    "tanggal": {
                        "type": "string",
                        "description": "Tanggal dalam format YYYY-MM-DD. Default: hari ini"
                    }
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_attendance_trends",
            "description": "Analyze attendance trends for a student or class over multiple months to identify patterns and improvements/deteriorations",
            "parameters": {
                "type": "object",
                "properties": {
                    "siswa_id": {
                        "type": "integer",
                        "description": "ID unik siswa di database (opsional jika nama_siswa diisi)"
                    },
                    "nama_siswa": {
                        "type": "string",
                        "description": "Nama siswa, bisa sebagian nama (opsional jika siswa_id diisi)"
                    },
                    "kelas_id": {
                        "type": "integer",
                        "description": "ID kelas (opsional jika nama_kelas diisi)"
                    },
                    "nama_kelas": {
                        "type": "string",
                        "description": "Nama kelas, misal 'X RPL 1', 'XI TKJ 2' (opsional jika kelas_id diisi)"
                    },
                    "months": {
                        "type": "integer",
                        "description": "Number of months to analyze (default: 6)"
                    }
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_geolocation_analysis",
            "description": "Analyze geolocation data for attendance validation and detect anomalies in student locations",
            "parameters": {
                "type": "object",
                "properties": {
                    "kelas_id": {
                        "type": "integer",
                        "description": "ID kelas (opsional jika nama_kelas diisi)"
                    },
                    "nama_kelas": {
                        "type": "string",
                        "description": "Nama kelas, misal 'X RPL', 'XI TSM' (opsional jika kelas_id diisi)"
                    },
                    "tanggal": {
                        "type": "string",
                        "description": "Specific date for analysis in YYYY-MM-DD format (opsional)"
                    }
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "compare_class_attendance",
            "description": "Compare attendance rates between different classes to identify patterns and performance differences",
            "parameters": {
                "type": "object",
                "properties": {
                    "tingkat": {
                        "type": "integer",
                        "description": "Grade level (10, 11, 12) (opsional)"
                    },
                    "jurusan": {
                        "type": "string",
                        "description": "Department (RPL, TKJ, etc.) (opsional)"
                    }
                }
            }
        }
    }

    ,
    {
        "type": "function",
        "function": {
            "name": "get_ringkasan_absensi_harian",
            "description": "Ringkasan absensi 1 kelas pada 1 tanggal: total Hadir/Izin/Sakit/Alfa + persentase hadir.",
            "parameters": {
                "type": "object",
                "properties": {
                    "kelas_id": {"type": "integer", "description": "ID kelas (opsional jika nama_kelas diisi)"},
                    "nama_kelas": {"type": "string", "description": "Nama kelas (opsional jika kelas_id diisi)"},
                    "tanggal": {"type": "string", "description": "Tanggal absensi (YYYY-MM-DD). Default: hari ini"}
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_ringkasan_absensi_range",
            "description": "Ringkasan absensi per hari untuk 1 kelas pada rentang tanggal (untuk grafik/tren).",
            "parameters": {
                "type": "object",
                "properties": {
                    "kelas_id": {"type": "integer", "description": "ID kelas (opsional jika nama_kelas diisi)"},
                    "nama_kelas": {"type": "string", "description": "Nama kelas (opsional jika kelas_id diisi)"},
                    "tanggal_mulai": {"type": "string", "description": "Tanggal mulai (YYYY-MM-DD)"},
                    "tanggal_akhir": {"type": "string", "description": "Tanggal akhir (YYYY-MM-DD)"}
                },
                "required": ["tanggal_mulai", "tanggal_akhir"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_rekap_absensi_kelas_range",
            "description": "Rekap absensi per siswa untuk 1 kelas pada rentang tanggal (Hadir/Izin/Sakit/Alfa + persen hadir).",
            "parameters": {
                "type": "object",
                "properties": {
                    "kelas_id": {"type": "integer", "description": "ID kelas (opsional jika nama_kelas diisi)"},
                    "nama_kelas": {"type": "string", "description": "Nama kelas (opsional jika kelas_id diisi)"},
                    "tanggal_mulai": {"type": "string", "description": "Tanggal mulai (YYYY-MM-DD)"},
                    "tanggal_akhir": {"type": "string", "description": "Tanggal akhir (YYYY-MM-DD)"}
                },
                "required": ["tanggal_mulai", "tanggal_akhir"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_top_siswa_absensi",
            "description": "Ambil top siswa dengan jumlah status tertentu (default: Alfa) pada rentang tanggal. Bisa per kelas atau seluruh sekolah (tanpa kelas).",
            "parameters": {
                "type": "object",
                "properties": {
                    "kelas_id": {"type": "integer", "description": "ID kelas (opsional, kosongkan untuk seluruh sekolah)"},
                    "nama_kelas": {"type": "string", "description": "Nama kelas (opsional, kosongkan untuk seluruh sekolah)"},
                    "tanggal_mulai": {"type": "string", "description": "Tanggal mulai (YYYY-MM-DD)"},
                    "tanggal_akhir": {"type": "string", "description": "Tanggal akhir (YYYY-MM-DD)"},
                    "status": {"type": "string", "description": "Status yang dihitung: Hadir/Izin/Sakit/Alfa. Default: Alfa"},
                    "limit": {"type": "integer", "description": "Jumlah maksimal baris. Default: 10"}
                },
                "required": ["tanggal_mulai", "tanggal_akhir"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_analisis_metode_absen",
            "description": "Analisis metode absen (field: metode) untuk 1 kelas pada rentang tanggal, termasuk breakdown status.",
            "parameters": {
                "type": "object",
                "properties": {
                    "kelas_id": {"type": "integer", "description": "ID kelas (opsional jika nama_kelas diisi)"},
                    "nama_kelas": {"type": "string", "description": "Nama kelas (opsional jika kelas_id diisi)"},
                    "tanggal_mulai": {"type": "string", "description": "Tanggal mulai (YYYY-MM-DD)"},
                    "tanggal_akhir": {"type": "string", "description": "Tanggal akhir (YYYY-MM-DD)"}
                },
                "required": ["tanggal_mulai", "tanggal_akhir"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_anomali_absensi",
            "description": "Deteksi anomali absensi: jarak terlalu jauh, metode non-manual tapi koordinat kosong, dan banyak siswa share koordinat identik.",
            "parameters": {
                "type": "object",
                "properties": {
                    "kelas_id": {"type": "integer", "description": "ID kelas (opsional jika nama_kelas diisi)"},
                    "nama_kelas": {"type": "string", "description": "Nama kelas (opsional jika kelas_id diisi)"},
                    "tanggal_mulai": {"type": "string", "description": "Tanggal mulai (YYYY-MM-DD)"},
                    "tanggal_akhir": {"type": "string", "description": "Tanggal akhir (YYYY-MM-DD)"},
                    "max_jarak_meter": {"type": "integer", "description": "Batas jarak_meter untuk dianggap anomali. Default: 200"},
                    "min_siswa_sama_koordinat": {"type": "integer", "description": "Minimal jumlah siswa dengan koordinat identik (per tanggal) untuk di-flag. Default: 4"},
                    "limit": {"type": "integer", "description": "Limit hasil per kategori anomali. Default: 100"}
                },
                "required": ["tanggal_mulai", "tanggal_akhir"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_statistik_waktu_absen",
            "description": "Statistik waktu_absen: distribusi per jam, total telat (waktu_absen > jam_telat), dan top siswa telat.",
            "parameters": {
                "type": "object",
                "properties": {
                    "kelas_id": {"type": "integer", "description": "ID kelas (opsional jika nama_kelas diisi)"},
                    "nama_kelas": {"type": "string", "description": "Nama kelas (opsional jika kelas_id diisi)"},
                    "tanggal_mulai": {"type": "string", "description": "Tanggal mulai (YYYY-MM-DD)"},
                    "tanggal_akhir": {"type": "string", "description": "Tanggal akhir (YYYY-MM-DD)"},
                    "jam_telat": {"type": "string", "description": "Ambang telat (HH:MM:SS). Default: 07:15:00"},
                    "limit": {"type": "integer", "description": "Limit top siswa telat. Default: 10"}
                },
                "required": ["tanggal_mulai", "tanggal_akhir"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_laporan_kepsek_range",
            "description": "Laporan ringkasan range untuk kepala sekolah: ringkasan lintas kelas, ranking kehadiran per kelas, dan alerts otomatis (kehadiran rendah, alfa tinggi). Cocok untuk laporan mingguan/2 mingguan/bulanan kepsek.",
            "parameters": {
                "type": "object",
                "properties": {
                    "tanggal_mulai": {"type": "string", "description": "Tanggal mulai periode (YYYY-MM-DD)"},
                    "tanggal_akhir": {"type": "string", "description": "Tanggal akhir periode (YYYY-MM-DD)"},
                    "tingkat": {"type": "integer", "description": "Filter tingkat/kelas (10, 11, 12). Opsional."},
                    "jurusan": {"type": "string", "description": "Filter jurusan (RPL, TKJ, dll). Opsional."},
                    "threshold_kehadiran": {"type": "number", "description": "Batas persen kehadiran untuk alert LOW_ATTENDANCE_CLASS. Default: 85.0"}
                },
                "required": ["tanggal_mulai", "tanggal_akhir"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_laporan_guru_harian",
            "description": "Laporan absensi harian detail untuk guru/wali kelas: daftar setiap siswa beserta status, metode, waktu absen, dan deteksi siswa yang belum punya record absensi.",
            "parameters": {
                "type": "object",
                "properties": {
                    "kelas_id": {"type": "integer", "description": "ID kelas (opsional jika nama_kelas diisi)"},
                    "nama_kelas": {"type": "string", "description": "Nama kelas, misal 'X RPL 1' (opsional jika kelas_id diisi)"},
                    "tanggal": {"type": "string", "description": "Tanggal absensi (YYYY-MM-DD). Default: hari ini"}
                }
            }
        }
    }
]
