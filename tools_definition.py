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
            "description": "Menghitung persentase kehadiran siswa atau seluruh kelas dalam periode tertentu. Bisa menggunakan ID siswa, nama siswa, ID kelas, atau nama kelas.",
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
                        "description": "Nama kelas, misal 'X RPL 1', 'XI TKJ 2' (opsional jika kelas_id diisi)"
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
]
