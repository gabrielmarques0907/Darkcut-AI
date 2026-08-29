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
st.subheader("Transforme vídeos em Shorts automaticamente")


def baixar_video(url):
    pasta = tempfile.mkdtemp()
    caminho = os.path.join(pasta, "video.%(ext)s")

    opcoes = {
    "format": "bestvideo+bestaudio/best",
    "outtmpl": caminho,
    "merge_output_format": "mp4",
    "quiet": True,
    "noplaylist": True
    
     }

    with yt_dlp.YoutubeDL(opcoes) as ydl:
        ydl.download([url])

    arquivos = os.listdir(pasta)

    if not arquivos:
        raise Exception("Não foi possível obter o vídeo.")

    return os.path.join(pasta, arquivos[0])


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


url = st.text_input(
    "🔗 Cole o link do vídeo",
    placeholder="https://..."
)


video = st.file_uploader(
    "📤 Ou envie um vídeo",
    type=["mp4", "mov", "avi", "mkv"]
)


if st.button("🤖 Analisar vídeo"):

    caminho = None

    try:

        if url:

            with st.spinner("🔗 Obtendo vídeo..."):
                caminho = baixar_video(url)

        elif video:

            arquivo = tempfile.NamedTemporaryFile(
                delete=False,
                suffix=".mp4"
            )

            arquivo.write(video.getvalue())
            arquivo.close()

            caminho = arquivo.name

        else:

            st.warning(
                "⚠️ Cole um link ou envie um vídeo."
            )

            st.stop()


        with st.spinner("🧠 Analisando o vídeo..."):

            cortes = analisar_video(caminho)


        st.session_state["cortes"] = cortes

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


    except Exception as erro:

        st.error(
            "❌ Não foi possível processar esse link."
        )

        st.code(str(erro))


    finally:

        if caminho and os.path.exists(caminho):

            os.remove(caminho)
