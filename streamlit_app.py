import streamlit as st
import whisper
import tempfile
import os
import subprocess
import yt_dlp


# =========================================================
# CONFIGURAÇÃO
# =========================================================

st.set_page_config(
    page_title="DarkCut AI",
    page_icon="🎬"
)

st.title("🎬 DarkCut AI")
st.subheader("Transforme vídeos longos em Shorts")


# =========================================================
# MODELO WHISPER
# =========================================================

@st.cache_resource
def carregar_modelo():
    return whisper.load_model("tiny")


# =========================================================
# EXTRAIR ÁUDIO
# =========================================================

def extrair_audio(video):

    audio = tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".wav"
    )

    audio.close()

    comando = [
        "ffmpeg",
        "-y",
        "-i",
        video,
        "-vn",
        "-ac",
        "1",
        "-ar",
        "16000",
        "-c:a",
        "pcm_s16le",
        audio.name
    ]

    resultado = subprocess.run(
        comando,
        capture_output=True,
        text=True
    )

    if resultado.returncode != 0:

        try:
            os.remove(audio.name)
        except:
            pass

        raise Exception(
            "Não foi possível extrair o áudio."
        )

    return audio.name


# =========================================================
# TRANSCRIÇÃO
# =========================================================

def transcrever(audio):

    modelo = carregar_modelo()

    resultado = modelo.transcribe(
        audio,
        fp16=False
    )

    return resultado["segments"]


# =========================================================
# CRIAR ATÉ 5 CORTES
# =========================================================

def criar_cortes(segmentos):

    cortes = []

    inicio = None
    textos = []

    for segmento in segmentos:

        if inicio is None:

            inicio = segmento["start"]
            textos = []

        textos.append(
            segmento["text"].strip()
        )

        fim = segmento["end"]

        duracao = fim - inicio

        # Entre 50 e 75 segundos
        if duracao >= 50:

            fim_corte = min(
                fim,
                inicio + 75
            )

            cortes.append({
                "inicio": inicio,
                "fim": fim_corte,
                "texto": " ".join(textos)
            })

            inicio = None
            textos = []

        # Máximo de 5
        if len(cortes) >= 5:
            break

    return cortes[:5]


# =========================================================
# BAIXAR YOUTUBE
# =========================================================

def baixar_video(url):

    pasta = tempfile.mkdtemp()

    saida = os.path.join(
        pasta,
        "video.%(ext)s"
    )

    opcoes = {
        "format": "bv*+ba/b",
        "outtmpl": saida,
        "noplaylist": True,
        "quiet": True,
        "no_warnings": True,
        "merge_output_format": "mp4"
    }

    try:

        with yt_dlp.YoutubeDL(opcoes) as ydl:
            ydl.download([url])

    except Exception as erro:

        if "403" in str(erro):

            raise Exception(
                "Não foi possível baixar este vídeo pelo link. "
                "Por enquanto, baixe o vídeo e envie o arquivo "
                "diretamente pelo botão de upload."
            )

        raise Exception(
            f"Não foi possível obter o vídeo: {erro}"
        )

    arquivos = os.listdir(pasta)

    videos = [
        arquivo
        for arquivo in arquivos
        if arquivo.lower().endswith(
            (".mp4", ".webm", ".mkv", ".mov")
        )
    ]

    if not videos:

        raise Exception(
            "Nenhum vídeo foi encontrado."
        )

    return os.path.join(
        pasta,
        videos[0]
    )


# =========================================================
# GERAR CORTE
# =========================================================

def gerar_corte(video, inicio, fim):

    saida = tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".mp4"
    )

    saida.close()

    duracao = fim - inicio

    comando = [
        "ffmpeg",
        "-y",
        "-ss",
        str(inicio),
        "-i",
        video,
        "-t",
        str(duracao),
        "-c:v",
        "libx264",
        "-preset",
        "veryfast",
        "-c:a",
        "aac",
        "-movflags",
        "+faststart",
        saida.name
    ]

    resultado = subprocess.run(
        comando,
        capture_output=True,
        text=True
    )

    if resultado.returncode != 0:

        raise Exception(
            resultado.stderr
        )

    return saida.name


# =========================================================
# LINK
# =========================================================

st.markdown("---")

st.markdown(
    "### 🔗 Opção 1 — Link do YouTube"
)

url = st.text_input(
    "Cole o link aqui",
    placeholder="https://youtube.com/..."
)

if st.button(
    "🔗 Verificar link",
    use_container_width=True
):

    if url.strip():

        st.success(
            "✅ Link recebido!"
        )

    else:

        st.warning(
            "⚠️ Cole um link primeiro."
        )


# =========================================================
# UPLOAD
# =========================================================

st.markdown("---")

st.markdown(
    "### 📤 Opção 2 — Enviar vídeo"
)

video = st.file_uploader(
    "Escolha um vídeo de até 1 GB",
    type=[
        "mp4",
        "mov",
        "avi",
        "mkv",
        "webm"
    ]
)


# =========================================================
# ANALISAR
# =========================================================

st.markdown("---")

if st.button(
    "🤖 Analisar vídeo",
    use_container_width=True
):

    caminho_video = None
    caminho_audio = None

    try:

        # =============================================
        # UPLOAD
        # =============================================

        if video is not None:

            limite = 1024 * 1024 * 1024

            if video.size > limite:

                st.error(
                    "❌ O vídeo ultrapassa o limite de 1 GB."
                )

                st.stop()

            with st.spinner(
                "📥 Preparando vídeo..."
            ):

                arquivo = tempfile.NamedTemporaryFile(
                    delete=False,
                    suffix=".mp4"
                )

                arquivo.write(
                    video.getvalue()
                )

                arquivo.close()

                caminho_video = arquivo.name


        # =============================================
        # YOUTUBE
        # =============================================

        elif url.strip():

            with st.spinner(
                "🔗 Obtendo vídeo..."
            ):

                caminho_video = baixar_video(
                    url.strip()
                )


        else:

            st.warning(
                "⚠️ Envie um vídeo ou cole um link."
            )

            st.stop()


        st.success(
            "🎬 Vídeo recebido!"
        )


        # =============================================
        # EXTRAIR ÁUDIO
        # =============================================

        with st.spinner(
            "🎵 Preparando áudio..."
        ):

            caminho_audio = extrair_audio(
                caminho_video
            )


        # =============================================
        # WHISPER
        # =============================================

        with st.spinner(
            "🧠 Analisando fala do vídeo..."
        ):

            segmentos = transcrever(
                caminho_audio
            )


        # =============================================
        # CORTES
        # =============================================

        with st.spinner(
            "🔥 Procurando os melhores trechos..."
        ):

            cortes = criar_cortes(
                segmentos
            )


        if not cortes:

            st.warning(
                "⚠️ Não encontramos trechos "
                "entre 50 e 75 segundos."
            )

        else:

            st.success(
                f"🔥 {len(cortes)} corte(s) encontrados!"
            )

            st.session_state["cortes"] = cortes
            st.session_state["video"] = caminho_video


    except Exception as erro:

        st.error(
            "❌ Não foi possível processar o vídeo."
        )

        st.code(
            str(erro)
        )


    finally:

        # Apaga somente o áudio temporário
        if caminho_audio:

            try:
                os.remove(caminho_audio)
            except:
                pass


# =========================================================
# MOSTRAR CORTES
# =========================================================

if "cortes" in st.session_state:

    st.markdown("---")

    st.markdown(
        "## ✂️ Cortes encontrados"
    )

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

            try:

                with st.spinner(
                    "🎬 Gerando corte..."
                ):

                    arquivo_saida = gerar_corte(
                        st.session_state["video"],
                        corte["inicio"],
                        corte["fim"]
                    )


                st.success(
                    "🎉 Corte criado!"
                )


                with open(
                    arquivo_saida,
                    "rb"
                ) as arquivo:

                    dados = arquivo.read()


                st.video(
                    dados
                )


                st.download_button(
                    "⬇️ Baixar MP4",
                    data=dados,
                    file_name=(
                        f"darkcut_corte_{i + 1}.mp4"
                    ),
                    mime="video/mp4",
                    use_container_width=True
                )


            except Exception as erro:

                st.error(
                    "❌ Erro ao gerar o corte."
                )

                st.code(
                    str(erro)
    )
