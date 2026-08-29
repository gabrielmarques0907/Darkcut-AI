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
# YOUTUBE
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
            "Nenhum arquivo de vídeo foi encontrado."
        )

    return os.path.join(
        pasta,
        videos[0]
    )


# =========================================================
# ENCONTRAR ATÉ 5 CORTES DE 50 A 75 SEGUNDOS
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

        # Corte entre 50 e 75 segundos
        if duracao >= 50:

            if duracao <= 75:

                cortes.append({
                    "inicio": inicio,
                    "fim": fim,
                    "texto": " ".join(textos)
                })

                inicio = None
                textos = []

            else:

                fim_corte = inicio + 75

                cortes.append({
                    "inicio": inicio,
                    "fim": fim_corte,
                    "texto": " ".join(textos)
                })

                inicio = None
                textos = []

        # Máximo de 5 cortes
        if len(cortes) >= 5:
            break

    return cortes[:5]


# =========================================================
# GERAR MP4
# =========================================================

def gerar_corte(
    entrada,
    inicio,
    fim
):

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
        saida.name
    ]

    resultado = subprocess.run(
        comando,
        capture_output=True,
        text=True
    )

    if resultado.returncode != 0:

        try:
            os.remove(saida.name)
        except:
            pass

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
# PROCESSAMENTO
# =========================================================

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

            tamanho = video.size

            limite = 1024 * 1024 * 1024

            if tamanho > limite:

                st.error(
                    "❌ O arquivo ultrapassa o limite de 1 GB."
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

                caminho = arquivo.name


        # =============================================
        # YOUTUBE
        # =============================================

        elif url.strip():

            with st.spinner(
                "🔗 Tentando obter o vídeo..."
            ):

                caminho = baixar_video(
                    url.strip()
                )


        else:

            st.warning(
                "⚠️ Cole um link ou envie um vídeo."
            )

            st.stop()


        # =============================================
        # RECEBIDO
        # =============================================

        st.success(
            "🎬 Vídeo recebido!"
        )


        # =============================================
        # TRANSCRIÇÃO
        # =============================================

        with st.spinner(
            "🧠 Analisando o vídeo..."
        ):

            segmentos = transcrever(
                caminho
            )


        if not segmentos:

            st.warning(
                "⚠️ Não foi possível encontrar fala."
            )

            st.stop()


        # =============================================
        # CORTES
        # =============================================

        with st.spinner(
            "🔥 Procurando até 5 cortes..."
        ):

            cortes = criar_cortes(
                segmentos
            )


        if not cortes:

            st.warning(
                "⚠️ Não encontramos trechos entre "
                "50 e 75 segundos."
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

        st.warning(
            str(erro)
        )


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
                    "🎬 Gerando Short..."
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
                        f"darkcut_corte_{i + 1}.mp4"
                    ),
                    mime="video/mp4",
                    use_container_width=True
                )


            except Exception as erro:

                st.error(
                    "❌ Erro ao gerar o MP4."
                )

                st.code(
                    str(erro)
    )
