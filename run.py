
import streamlit as st

st.set_page_config(
    page_title="PIJAR | Platform Pendidikan",
    page_icon="📘",
    layout="wide",
)

st.title("PIJAR")
st.caption(
    "Platform Interaktif Jejaring Asesmen dan Refleksi"
)
st.markdown("### Terangi Potensi, Ukir Prestasi.")

menu = st.sidebar.radio(
    "Navigasi",
    ["Beranda", "Simulasi Ujian", "Tentang PIJAR"],
)

if menu == "Beranda":
    st.subheader("Selamat datang di PIJAR")
    st.write(
        "Platform untuk mendukung asesmen dan refleksi belajar."
    )

    col1, col2, col3 = st.columns(3)
    col1.metric("Status", "Demo")
    col2.metric("Modul", "3")
    col3.metric("Mode", "Pratinjau")

elif menu == "Simulasi Ujian":
    st.subheader("Simulasi Ujian")
    st.info("Contoh soal untuk menguji antarmuka.")

    jawaban = st.radio(
        "Berapakah 2 + 2?",
        ["3", "4", "5", "6"],
        index=None,
    )

    if st.button("Periksa Jawaban"):
        if jawaban is None:
            st.warning("Pilih jawaban terlebih dahulu.")
        elif jawaban == "4":
            st.success("Jawaban benar.")
        else:
            st.error("Jawaban belum tepat.")

elif menu == "Tentang PIJAR":
    st.subheader("Tentang PIJAR")
    st.write(
        "PIJAR membantu guru dan sekolah mengelola "
        "aktivitas asesmen dan refleksi belajar."
    )
