import streamlit as st
import whisper
import tempfile
import os
import subprocess
import yt_dlp

st.set_page_config(
    page_title="DarkCut AI",
    page_icon="🎬"
)

st.title("🎬 DarkCut AI")
st.subheader("Transforme vídeos longos em Shorts")

# -------------------------
# FUNÇÃO: baixar vídeo
# -------------------------

def baixar_video(url):

    pasta = tempfile.mkdtemp()
    arquivo_saida = os.path.join(pasta, "video.%(ext)s")

    opcoes = {
        "outtmpl": arquivo_saida,
        "format": "best[ext=mp4]/best",
        "noplaylist": True,
        "quiet": True
    }

    with yt_dlp.YoutubeDL(opcoes) as ydl:
        ydl.download([url])

    arquivos = os.listdir(pasta)

    if not arquivos:
        raise Exception(
            "Nenhum arquivo de vídeo foi obtido."
        )

    return os.path.join(
        pasta,
        arquivos[0]
    )


# -------------------------
# FUNÇÃO: analisar
# -------------------------

def analisar_video(caminho):

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

    return cortes


# -------------------------
# LINK
# -------------------------

st.markdown("### 🔗 Opção 1 — Link do vídeo")

url = st.text_input(
    "Cole o link aqui",
    placeholder="https://..."
)

if st.button(
    "🔍 Verificar link",
    use_container_width=True
):

    if url.strip():

        st.success("✅ Link recebido!")

    else:

        st.warning(
            "⚠️ Cole um link primeiro."
        )


# -------------------------
# UPLOAD
# -------------------------

st.markdown("### 📤 Opção 2 — Enviar vídeo")

video = st.file_uploader(
    "Escolha seu vídeo",
    type=[
        "mp4",
        "mov",
        "avi",
        "mkv"
    ]
)


# -------------------------
# PROCESSAR
# -------------------------

if st.button(
    "🤖 Analisar vídeo",
    use_container_width=True
):

    caminho = None

    try:

        # LINK
        if url.strip():

           
