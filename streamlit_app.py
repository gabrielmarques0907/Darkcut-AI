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


def baixar_video(url):
    pasta = tempfile.mkdtemp()
    saida = os.path.join(pasta, "video.%(ext)s")

    opcoes = {
        "format": "best",
        "outtmpl": saida,
        "noplaylist": True,
        "quiet": True
    }

    with yt_dlp.YoutubeDL(opcoes) as ydl:
        ydl.download([url])

    arquivos = os.listdir(pasta)

    if len(arquivos) == 0:
        raise Exception("Nenhum vídeo foi encontrado.")

    return os.path.join(pasta, arquivos[0])


def transcrever(caminho):
    modelo = whisper.load_model("tiny")
    resultado = modelo.transcribe(caminho)
    return resultado["segments"]


def criar_cortes(segmentos):
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
        st.warning("⚠️ Cole um link primeiro.")


st.markdown("### 📤 Opção 2 — Enviar vídeo")

video = st.file_uploader(
    "Escolha um vídeo",
    type=["mp4", "mov", "avi", "mkv"]
)


if st.button(
    "🤖 Analisar vídeo",
    use_container_width=True
):

    caminho = None

    try:

        if video is not None:

            arquivo = tempfile.NamedTemporaryFile(
                delete=False,
                suffix=".mp4"
            )

            arquivo.write(video.getvalue())
            arquivo.close()

            caminho = arquivo.name

        elif url.strip():

            with st.spinner("🔗 Obtendo o vídeo..."):
                caminho = baixar_video(url.strip())

        else:

            st.warning(
                "⚠️ Cole um link ou envie um vídeo."
            )
            st.stop()


        st.success("🎬 Vídeo recebido!")


        with st.spinner("🧠 Transcrevendo vídeo..."):

            segmentos = transcrever(caminho)


        with st.spinner("✂️ Encontrando cortes..."):

            cortes = criar_cortes(segmentos)


        if len(cortes) == 0:

            st.warning(
                "Nenhum corte de 30 segundos foi encontrado."
            )

        else:

            st.success(
                f"🔥 {len(cortes)} corte(s) encontrados!"
            )


            st.session_state["cortes"] = cortes

            st.session_state["video"] = caminho


    except Exception as erro:

        st.error(
            "❌ Não foi possível processar o vídeo."
        )

        st.code(str(erro))


if "cortes" in st.session_state:

    st.markdown("## ✂️ Cortes sugeridos")


    for i, corte in enumerate(
        st.session_state["cortes"]
    ):

        st.markdown(
            f"### 🎬 Corte {i + 1}"
        )


        st.write(
            f"⏱️ {corte['inicio']:.1f}s → "
            f"{corte['fim']:.1f}s"
        )


        st.write(
            f"📝 {corte['texto']}"
        )


        if st.button(
            f"✂️ Gerar Corte {i + 1}",
            key=f"gerar_{i}",
            use_container_width=True
        ):

            entrada = st.session_state["video"]

            saida = tempfile.NamedTemporaryFile(
                delete=False,
                suffix=".mp4"
            )

            saida.close()


            comando = [
                "ffmpeg",
                "-y",
                "-ss",
                str(corte["inicio"]),
                "-i",
                entrada,
                "-t",
                str(
                    corte["fim"] - corte["inicio"]
                ),
                "-c:v",
                "libx264",
                "-c:a",
                "aac",
                saida.name
            ]


            resultado = subprocess.run(
                comando,
                capture_output=True,
                text=True
            )


            if resultado.returncode == 0:

                st.success(
                    "🎉 Corte criado!"
                )


                with open(
                    saida.name,
                    "rb"
                ) as arquivo:

                    dados = arquivo.read()


                st.video(dados)


                st.download_button(
                    "⬇️ Baixar MP4",
                    data=dados,
                    file_name=f"darkcut_corte_{i + 1}.mp4",
                    mime="video/mp4",
                    use_container_width=True
                )


            else:

                st.error(
                    "❌ Erro ao gerar o MP4."
                )

                st.code(
                    resultado.stderr
                )


            os.remove(saida.name)
