import streamlit as st
import whisper
import tempfile
import os
import subprocess

st.set_page_config(
    page_title="DarkCut AI",
    page_icon="🎬"
)

st.title("🎬 DarkCut AI")
st.subheader("Transforme vídeos longos em Shorts")

st.markdown("### 🔗 Opção 1 — Link do vídeo")

url = st.text_input(
    "Cole o link do vídeo aqui",
    placeholder="https://..."
)

st.markdown("### 📤 Opção 2 — Enviar vídeo")

video = st.file_uploader(
    "Escolha um vídeo",
    type=["mp4", "mov", "avi", "mkv"]
)

if url:
    st.info(
        "🔗 Link recebido! O sistema de download "
        "será conectado na próxima etapa."
    )

if video:
    st.success("✅ Vídeo recebido!")

    st.session_state["video_bytes"] = video.getvalue()

    st.video(st.session_state["video_bytes"])

    if st.button("🤖 Encontrar melhores cortes"):

        with st.spinner("🧠 Analisando o vídeo..."):

            with tempfile.NamedTemporaryFile(
                delete=False,
                suffix=".mp4"
            ) as arquivo:

                arquivo.write(
                    st.session_state["video_bytes"]
                )

                caminho = arquivo.name

            modelo = whisper.load_model("tiny")

            resultado = modelo.transcribe(
                caminho,
                verbose=False
            )

        segmentos = resultado["segments"]

        cortes = []
        inicio = None
        textos = []

        for segmento in segmentos:

            if inicio is None:
                inicio = segmento["start"]

            textos.append(segmento["text"])

            fim = segmento["end"]

            if fim - inicio >= 30:

                cortes.append({
                    "inicio": inicio,
                    "fim": fim,
                    "texto": " ".join(textos)
                })

                inicio = None
                textos = []

        st.session_state["cortes"] = cortes

        os.remove(caminho)

        st.success(
            f"🔥 {len(cortes)} corte(s) encontrados!"
        )

        for i, corte in enumerate(cortes):

            st.markdown(
                f"### ✂️ Corte {i + 1}"
            )

            st.write(
                f"⏱️ {corte['inicio']:.1f}s → "
                f"{corte['fim']:.1f}s"
            )

            st.write(
                f"📝 {corte['texto']}"
            )
