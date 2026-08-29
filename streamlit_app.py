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
    page_icon="🎬",
    layout="centered"
)

st.title("🎬 DarkCut AI")
st.subheader("Transforme vídeos longos em Shorts")


# =========================================================
# WHISPER
# =========================================================

@st.cache_resource
def carregar_modelo():
    return whisper.load_model("tiny")


def transcrever(caminho):

    modelo = carregar_modelo()

    resultado = modelo.transcribe(
        caminho,
        fp16=False
    )

    return resultado["segments"]


# =========================================================
# DOWNLOAD DO YOUTUBE
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

        mensagem = str(erro)

        if "403" in mensagem:

            raise Exception(
                "O YouTube bloqueou o download deste vídeo "
                "no servidor. Tente outro vídeo ou envie "
                "o arquivo diretamente."
            )

        raise Exception(
            f"Não foi possível obter o vídeo: {mensagem}"
        )


    arquivos = os.listdir(pasta)

    arquivos_video = [
        arquivo
        for arquivo in arquivos
        if arquivo.lower().endswith(
            (".mp4", ".webm", ".mkv", ".mov")
        )
    ]


    if not arquivos_video:

        raise Exception(
            "O download terminou, mas nenhum arquivo "
            "de vídeo foi encontrado."
        )


    return os.path.join(
        pasta,
        arquivos_video[0]
    )


# =========================================================
# ENCONTRAR CORTES
# =========================================================

def criar_cortes(segmentos):

    cortes = []

    inicio = None
    textos = []

    for segmento in segmentos:

        if inicio is None:

            inicio = segmento["start"]

        textos.append(
            segmento["text"].strip()
        )

        fim = segmento["end"]

        duracao = fim - inicio


        if duracao >= 30:

            cortes.append({

                "inicio": inicio,

                "fim": fim,

                "texto": " ".join(textos)

            })

            inicio = None
            textos = []


    return cortes


# =========================================================
# CRIAR MP4
# =========================================================

def gerar_corte(
    entrada,
    inicio,
    fim
):

    arquivo_saida = tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".mp4"
    )

    arquivo_saida.close()


    duracao = fim - inicio


    comando = [

        "ffmpeg",

        "-y",

        "-ss",
        str(inicio),

        "-i",
        entrada,

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

        arquivo_saida.name

    ]


    resultado = subprocess.run(
        comando,
        capture_output=True,
        text=True
    )


    if resultado.returncode != 0:

        try:
            os.remove(arquivo_saida.name)
        except:
            pass

        raise Exception(
            resultado.stderr
        )


    return arquivo_saida.name


# =========================================================
# INTERFACE
# =========================================================

st.markdown("---")

st.markdown(
    "### 🔗 Opção 1 — Link do YouTube"
)


url = st.text_input(
    "Cole o link do vídeo",
    placeholder="https://www.youtube.com/watch?v=..."
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


st.markdown("---")

st.markdown(
    "### 📤 Opção 2 — Enviar vídeo"
)


video = st.file_uploader(

    "Escolha um vídeo",

    type=[
        "mp4",
        "mov",
        "avi",
        "mkv",
        "webm"
    ]

)


st.markdown("---")


if st.button(
    "🤖 Analisar vídeo",
    use_container_width=True
):

    caminho = None


    try:

        # =============================================
        # UPLOAD
        # =============================================

        if video is not None:

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

                caminho = arquivo.name


        # =============================================
        # YOUTUBE
        # =============================================

        elif url.strip():

            with st.spinner(
                "🔗 Obtendo vídeo do YouTube..."
            ):

                caminho = baixar_video(
                    url.strip()
                )


        else:

            st.warning(
                "⚠️ Cole um link do YouTube "
                "ou envie um vídeo."
            )

            st.stop()


        # =============================================
        # VÍDEO RECEBIDO
        # =============================================

        st.success(
            "🎬 Vídeo recebido!"
        )


        # =============================================
        # TRANSCRIÇÃO
        # =============================================

        with st.spinner(
            "🧠 Transcrevendo vídeo..."
        ):

            segmentos = transcrever(
                caminho
            )


        if not segmentos:

            st.warning(
                "⚠️ Não foi possível encontrar fala "
                "no vídeo."
            )

            st.stop()


        # =============================================
        # CORTES
        # =============================================

        with st.spinner(
            "✂️ Encontrando cortes..."
        ):

            cortes = criar_cortes(
                segmentos
            )


        if not cortes:

            st.warning(
                "⚠️ Nenhum corte de pelo menos "
                "30 segundos foi encontrado."
            )

        else:

            st.success(
                f"🔥 {len(cortes)} corte(s) encontrados!"
            )


            st.session_state[
                "cortes"
            ] = cortes


            st.session_state[
                "video"
            ] = caminho


    except Exception as erro:

        st.error(
            "❌ Não foi possível processar o vídeo."
        )

        st.warning(
            str(erro)
        )


# =========================================================
# CORTES SUGERIDOS
# =========================================================

if "cortes" in st.session_state:

    st.markdown("---")

    st.markdown(
        "## ✂️ Cortes sugeridos"
    )


    for i, corte in enumerate(
        st.session_state["cortes"]
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
            f"✂️ Gerar Corte {i + 1}",
            key=f"gerar_{i}",
            use_container_width=True
        ):

            try:

                with st.spinner(
                    "🎬 Gerando MP4..."
                ):

                    entrada = st.session_state[
                        "video"
                    ]


                    caminho_saida = gerar_corte(

                        entrada,

                        corte["inicio"],

                        corte["fim"]

                    )


                st.success(
                    "🎉 Corte criado!"
                )


                with open(
                    caminho_saida,
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
                        f"darkcut_corte_"
                        f"{i + 1}.mp4"
                    ),

                    mime="video/mp4",

                    use_container_width=True

                )


                try:

                    os.remove(
                        caminho_saida
                    )

                except:

                    pass


            except Exception as erro:

                st.error(
                    "❌ Erro ao gerar o corte."
                )

                st.code(
                    str(erro)
    )
