import streamlit as st
import time
from agent import run_agent

# Konfigurasi Halaman
st.set_page_config(
    page_title="Asisten Absensi Sekolah",
    page_icon="🏫",
    layout="centered"
)

# Judul Aplikasi
st.title("🏫 Sistem Absensi Sekolah AI")
st.markdown("Tanyakan apa saja tentang absensi siswa, laporan, atau surat peringatan.")

# Inisialisasi History Chat
if "messages" not in st.session_state:
    st.session_state.messages = []

# Tampilkan History Chat
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Input Chat User
if prompt := st.chat_input("Contoh: 'Siapa yang alfa hari ini?' atau 'Buat surat peringatan untuk Budi'"):
    # 1. Tampilkan pesan user
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. Proses di backend (Agent)
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.markdown("⏳ *Sedang menganalisis data...*")
        
        try:
            # Panggil fungsi run_agent dari file agent.py yang sudah ada
            # Kita tidak perlu model param karena sudah default di config
            response = run_agent(prompt)
            
            # Tampilkan respons akhir
            message_placeholder.markdown(response)
            
            # Simpan ke history
            st.session_state.messages.append({"role": "assistant", "content": response})
            
        except Exception as e:
            error_message = f"❌ Terjadi kesalahan: {str(e)}"
            message_placeholder.error(error_message)
