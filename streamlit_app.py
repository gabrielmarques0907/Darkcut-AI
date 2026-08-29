import streamlit as st
import whisper
import tempfile

st.set_page_config(
    page_title="DarkCut AI",
    page_icon="🎬"
)

st.title("🎬 DarkCut AI")
st.subheader("Sua IA de vídeos e cortes")

st.write("Envie um vídeo e a IA vai transcrever o conteúdo.")

video = st.file_uploader(
    "📤 Envie seu vídeo",
    type=["mp4", "mov", "avi", "mkv"]
)

if video:
    st.success("Vídeo recebido! 🚀")
    st.video(video)

    if st.button("🤖 Analisar vídeo"):
        with st.spinner("🧠 Analisando o vídeo..."):
            with tempfile.NamedTemporaryFile(
                delete=False,
                suffix=".mp4"
            ) as arquivo:
                arquivo.write(video.read())
                caminho = arquivo.name

            modelo = whisper.load_model("tiny")
            resultado = modelo.transcribe(caminho)

        st.success("✅ Análise concluída!")

        st.subheader("📝 Transcrição")
        st.write(resultado["text"])
