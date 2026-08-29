import streamlit as st
import whisper
import tempfile
import os
import subprocess
import re


# =========================================================
# CONFIGURAÇÃO
# =========================================================

st.set_page_config(
    page_title="DarkCut AI",
    page_icon="🎬",
    layout="centered"
)


st.title("🎬 DarkCut AI")
st.subheader("Transforme vídeos longos em Shorts com IA")


# =========================================================
# MODELO WHISPER
# =========================================================

@st.cache_resource
def carregar_modelo():
    return whisper.load_model("tiny")


# =========================================================
# VALIDAR LINK DO YOUTUBE
# =========================================================

def validar_youtube(url):
    padrao = (
        r"(https?://)?(www\.)?"
        r"(youtube\.com/watch\?v=|youtu\.be/)"
        r"[\w-]+"
    )

    return re.match(padrao, url.strip()) is not None


# =========================================================
# SALVAR UPLOAD
# =========================================================

def salvar_video(upload):
    extensao = os.path.splitext(upload.name)[1]

    if not extensao:
        extensao = ".mp4"

    arquivo = tempfile.NamedTemporaryFile(
        delete=False,
        suffix=extensao
    )

    arquivo.write(upload.getvalue())
    arquivo.close()

    return arquivo.name


# =========================================================
# TRANSCRIÇÃO
# =========================================================

def transcrever(caminho):

    modelo = carregar_modelo()

    resultado = modelo.transcribe(
        caminho,
        fp16=False
    )

    return resultado["segments"]


# =========================================================
# ENCONTRAR CORTES
# =========================================================

def criar_cortes(segmentos, duracao_minima=30, duracao_maxima=60):

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

        if duracao >= duracao_minima:

            fim_corte = min(
                fim,
                inicio + duracao_maxima
            )

            cortes.append({
                "inicio": inicio,
                "fim": fim_corte,
                "texto": " ".join(textos)
            })

            inicio = None
            textos = []

    return cortes


# =========================================================
# GERAR CORTE 9:16
# =========================================================

def gerar_corte_9x16(
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

        # Corte vertical 9:16
        "-vf",
        "crop=ih*9/16:ih:(iw-ih*9/16)/2:0,scale=1080:1920",

        "-c:v",
        "libx264",

        "-preset",
        "veryfast",

        "-crf",
        "23",

        "-c:a",
        "aac",

        "-b:a",
        "128k",

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

        os.remove(saida.name)

        raise Exception(
            resultado.stderr
        )

    return saida.name


# =========================================================
# LINK YOUTUBE
# =========================================================

st.markdown("### 🔗 Opção 1 — Link do YouTube")

url = st.text_input(
    "Cole o link do YouTube",
    placeholder="https://www.youtube.com/watch?v=..."
)


if st.button(
    "🔍 Verificar link",
    use_container_width=True
):

    if not url.strip():

        st.warning(
            "⚠️ Cole um link primeiro."
        )

    elif validar_youtube(url):

        st.success(
            "✅ Link do YouTube reconhecido!"
        )

        st.info(
            "ℹ️ Para processar o vídeo nesta versão, "
            "envie o arquivo de vídeo pelo campo abaixo. "
            "O DarkCut não tenta contornar as restrições "
            "de download do YouTube."
        )

    else:

        st.error(
            "❌ Esse não parece ser um link válido do YouTube."
        )


# =========================================================
# UPLOAD
# =========================================================

st.markdown("### 📤 Opção 2 — Enviar vídeo")

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


# =========================================================
# CONFIGURAÇÕES
# =========================================================

st.markdown("### ⚙️ Configurações")

duracao_minima = st.slider(
    "Duração mínima do corte",
    min_value=15,
    max_value=60,
    value=30
)

duracao_maxima = st.slider(
    "Duração máxima do corte",
    min_value=30,
    max_value=120,
    value=60
)


# =========================================================
# ANALISAR
# =========================================================

if st.button(
    "🤖 Analisar vídeo",
    use_container_width=True
):

    caminho = None

    try:

        # ---------------------------------------------
        # UPLOAD
        # ---------------------------------------------

        if video is not None:

            with st.spinner(
                "📤 Preparando vídeo..."
            ):

                caminho = salvar_video(video)

        # ---------------------------------------------
        # LINK YOUTUBE
        # ---------------------------------------------

        elif url.strip():

            if not validar_youtube(url):

                st.error(
                    "❌ Link do YouTube inválido."
                )

                st.stop()

            st.warning(
                "⚠️ O link foi reconhecido, "
                "mas o DarkCut precisa do arquivo "
                "do vídeo para processá-lo nesta versão."
            )

            st.stop()

        # ---------------------------------------------
        # NADA ENVIADO
        # ---------------------------------------------

        else:

            st.warning(
                "⚠️ Envie um vídeo primeiro."
            )

            st.stop()


        st.success(
            "🎬 Vídeo recebido!"
        )


        # ---------------------------------------------
        # TRANSCRIÇÃO
        # ---------------------------------------------

        with st.spinner(
            "🧠 Transcrevendo vídeo com IA..."
        ):

            segmentos = transcrever(
                caminho
            )


        if not segmentos:

            st.error(
                "❌ Não foi possível encontrar fala no vídeo."
            )

            st.stop()


        # ---------------------------------------------
        # CORTES
        # ---------------------------------------------

        with st.spinner(
            "✂️ Encontrando melhores trechos..."
        ):

            cortes = criar_cortes(
                segmentos,
                duracao_minima,
                duracao_maxima
            )


        if not cortes:

            st.warning(
                f"⚠️ Nenhum trecho de pelo menos "
                f"{duracao_minima} segundos foi encontrado."
            )

            st.stop()


        st.success(
            f"🔥 {len(cortes)} corte(s) encontrados!"
        )


        st.session_state["cortes"] = cortes
        st.session_state["video"] = caminho


    except Exception as erro:

        st.error(
            "❌ Não foi possível processar o vídeo."
        )

        st.code(
            str(erro)
        )


# =========================================================
# MOSTRAR CORTES
# =========================================================

if "cortes" in st.session_state:

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
            f"⏱️ {corte['inicio']:.1f}s → "
            f"{corte['fim']:.1f}s"
        )


        st.write(
            f"📝 {corte['texto']}"
        )


        if st.button(
            f"🎬 Gerar Corte {i + 1} — 9:16",
            key=f"gerar_{i}",
            use_container_width=True
        ):

            entrada = st.session_state["video"]


            try:

                with st.spinner(
                    "🎬 Gerando vídeo vertical 9:16..."
                ):

                    arquivo_saida = gerar_corte_9x16(
                        entrada,
                        corte["inicio"],
                        corte["fim"]
                    )


                st.success(
                    "🎉 Corte criado com sucesso!"
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


                os.remove(
                    arquivo_saida
                )


            except Exception as erro:

                st.error(
                    "❌ Erro ao gerar o corte."
                )

                st.code(
                    str(erro)
)
