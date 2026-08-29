import streamlit as st
import whisper
import tempfile
import os
import subprocess
import yt_dlp

st.set_page_config(
    page_title="DarkCut AI",
    page_icon="🎬",
    layout="centered"
)

st.title("🎬 DarkCut AI")
st.subheader("Transforme vídeos longos em Shorts")

# =========================
# FUNÇÕES
# =========================

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
        raise Exception(
            "Não foi possível obter o vídeo."
        )

    return os.path.join(
        pasta,
        arquivos[0]
    )


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

            texto = " ".join(textos)

            cortes.append({
                "inicio": inicio,
                "fim": fim,
                "texto": texto
            })

            inicio = None
            textos = []

    return cortes


# =========================
# ESTADO
# =========================

if "cortes" not in st.session_state:
    st.session_state.cortes = []

if "video_bytes" not in st.session_state:
    st.session_state.video_bytes = None

if "corte_selecionado" not in st.session_state:
    st.session_state.corte_selecionado = None


# =========================
# LINK
# =========================

st.markdown("### 🔗 Opção 1 — Link do vídeo")

url = st.text_input(
    "Cole o link do vídeo aqui",
    placeholder="https://..."
)

verificar_link = st.button(
    "🔍 Verificar link",
    use_container_width=True
)

if verificar_link:

    if url.strip():

        st.success("✅ Link recebido!")

        st.info(
            "O link foi recebido. "
            "Agora você pode tocar em "
            "🤖 Analisar vídeo."
        )

    else:

        st.warning(
            "⚠️ Cole um link antes de continuar."
        )


# =========================
# UPLOAD
# =========================

st.markdown("### 📤 Opção 2 — Enviar vídeo")

video = st.file_uploader(
    "Escolha um vídeo",
    type=[
        "mp4",
        "mov",
        "avi",
        "mkv"
    ]
)


# =========================
# ANALISAR
# =========================

analisar = st.button(
    "🤖 Analisar vídeo",
    use_container_width=True
)


if analisar:

    caminho = None

    try:

        # LINK

        if url.strip():

            with st.spinner(
                "🔗 Obtendo o vídeo..."
            ):

                caminho = baixar_video(
                    url.strip()
                )

        # UPLOAD

        elif video:

            arquivo = tempfile.NamedTemporaryFile(
                delete=False,
                suffix=".mp4"
            )

            arquivo.write(
                video.getvalue()
            )

            arquivo.close()

            caminho = arquivo.name

            st.session_state.video_bytes = (
                video.getvalue()
            )

        else:

            st.warning(
                "⚠️ Cole um link ou envie um vídeo."
            )

            st.stop()


        # Se veio por link
        if url.strip():

            with open(
                caminho,
                "rb"
            ) as arquivo:

                st.session_state.video_bytes = (
                    arquivo.read()
                )


        st.success(
            "🎬 Vídeo obtido com sucesso!"
        )

        st.video(
            st.session_state.video_bytes
        )


        # WHISPER

        with st.spinner(
            "🧠 Analisando o vídeo..."
        ):

            cortes = analisar_video(
                caminho
            )

        st.session_state.cortes = cortes

        st.session_state.corte_selecionado = None

        st.success(
            f"🔥 {len(cortes)} corte(s) encontrados!"
        )


    except Exception as erro:

        st.error(
            "❌ Não foi possível processar esse link."
        )

        st.code(
            str(erro)
        )


    finally:

        if caminho and os.path.exists(caminho):

            try:
                os.remove(caminho)
            except:
                pass


# =========================
# MOSTRAR CORTES
# =========================

if st.session_state.cortes:

    st.markdown("## ✂️ Cortes sugeridos")

    for i, corte in enumerate(
        st.session_state.cortes
    ):

        st.markdown(
            f"### 🎬 Corte {i + 1}"
        )

        st.write(
            f"⏱️ "
            f"{corte['inicio']:.1f}s → "
            f"{corte['fim']:.1f}s"
        )

        st.write(
            f"📝 {corte['texto']}"
        )

        if st.button(
            f"🎯 Selecionar Corte {i + 1}",
            key=f"selecionar_{i}",
            use_container_width=True
        ):

            st.session_state.corte_selecionado = i


# =========================
# CORTE SELECIONADO
# =========================

if (
    st.session_state.corte_selecionado
    is not None
):

    i = st.session_state.corte_selecionado

    corte = st.session_state.cortes[i]

    st.success(
        f"✅ Corte {i + 1} selecionado!"
    )

    st.write(
        f"⏱️ "
        f"{corte['inicio']:.1f}s → "
        f"{corte['fim']:.1f}s"
    )


    # =====================
    # GERAR MP4
    # =====================

    if st.button(
        "✂️ Gerar MP4 deste corte",
        use_container_width=True
    ):

        with st.spinner(
            "🎬 Gerando seu corte..."
        ):

            entrada = tempfile.NamedTemporaryFile(
                delete=False,
                suffix=".mp4"
            )

            entrada.write(
                st.session_state.video_bytes
            )

            entrada.close()


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
                entrada.name,
                "-t",
                str(
                    corte["fim"]
                    - corte["inicio"]
                ),
                "-c:v",
                "libx264",
                "-c:a",
                "aac",
                saida.name
            ]


            processo = subprocess.run(
                comando,
                capture_output=True,
                text=True
            )


            if processo.returncode != 0:

                st.error(
                    "❌ Não foi possível gerar o corte."
                )

                st.code(
                    processo.stderr
                )

            else:

                st.success(
                    "🎉 Corte gerado com sucesso!"
                )

                with open(
                    saida.name,
                    "rb"
                ) as arquivo:

                    video_cortado = (
                        arquivo.read()
                    )


                st.video(
                    video_cortado
                )


                st.download_button(
                    "⬇️ Baixar MP4",
                    data=video_cortado,
                    file_name=(
                        f"darkcut_corte_{i + 1}.mp4"
                    ),
                    mime="video/mp4",
                    use_container_width=True
                )


            os.remove(entrada.name)
            os.remove(saida.name)
