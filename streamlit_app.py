import streamlit as st
import whisper
import tempfile
import os

st.set_page_config(
    page_title="DarkCut AI",
    page_icon="🎬"
)

st.title("🎬 DarkCut AI")
st.subheader("Sua IA de vídeos e cortes")

video = st.file_uploader(
    "📤 Envie seu vídeo",
    type=["mp4", "mov", "avi", "mkv"]
)

if video:
    st.success("Vídeo recebido! 🚀")
    st.video(video)

    if st.button("🤖 Encontrar melhores cortes"):

        with st.spinner("🧠 Analisando o vídeo..."):

            with tempfile.NamedTemporaryFile(
                delete=False,
                suffix=".mp4"
            ) as arquivo:
                arquivo.write(video.getbuffer())
                caminho = arquivo.name

            modelo = whisper.load_model("tiny")

            resultado = modelo.transcribe(
                caminho,
                verbose=False
            )

        st.success("✅ Análise concluída!")

        segmentos = resultado["segments"]

        st.subheader("✂️ Cortes sugeridos")

        inicio = None
        fim = None
        numero = 1

        for segmento in segmentos:

            if inicio is None:
                inicio = segmento["start"]

            fim = segmento["end"]

            duracao = fim - inicio

            if duracao >= 30:

                st.write(
                    f"🎬 **Corte {numero}** — "
                    f"{inicio:.1f}s → {fim:.1f}s"
                )

                st.caption(segmento["text"])

                inicio = None
                fim = None
                numero += 1

        os.remove(caminho)
