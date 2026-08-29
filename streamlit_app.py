import streamlit as st
import tempfile
import os
import wave
import urllib.request
from piper import PiperVoice


st.set_page_config(
    page_title="DarkCut AI",
    page_icon="🎬"
)

st.title("🎬 DarkCut AI")
st.subheader("Teste de voz")


# =========================================================
# CONFIGURAÇÃO
# =========================================================

PASTA_VOZ = os.path.join(
    tempfile.gettempdir(),
    "darkcut_voice"
)

os.makedirs(
    PASTA_VOZ,
    exist_ok=True
)

MODELO = os.path.join(
    PASTA_VOZ,
    "pt_BR-cadu-medium.onnx"
)

CONFIG = os.path.join(
    PASTA_VOZ,
    "pt_BR-cadu-medium.onnx.json"
)


URL_MODELO = (
    "https://huggingface.co/rhasspy/piper-voices/"
    "resolve/main/pt/pt_BR/cadu/medium/"
    "pt_BR-cadu-medium.onnx"
)

URL_CONFIG = (
    "https://huggingface.co/rhasspy/piper-voices/"
    "resolve/main/pt/pt_BR/cadu/medium/"
    "pt_BR-cadu-medium.onnx.json"
)


# =========================================================
# BAIXAR MODELO
# =========================================================

def preparar_modelo():

    if not os.path.exists(MODELO):

        st.write("📥 Baixando modelo de voz...")

        urllib.request.urlretrieve(
            URL_MODELO,
            MODELO
        )


    if not os.path.exists(CONFIG):

        st.write("📥 Baixando configuração da voz...")

        urllib.request.urlretrieve(
            URL_CONFIG,
            CONFIG
        )


# =========================================================
# CARREGAR VOZ
# =========================================================

@st.cache_resource
def carregar_voz():

    preparar_modelo()

    return PiperVoice.load(
        MODELO,
        config_path=CONFIG
    )


# =========================================================
# GERAR ÁUDIO
# =========================================================

def gerar_audio(texto):

    voz = carregar_voz()

    arquivo = tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".wav"
    )

    arquivo.close()

    with wave.open(
        arquivo.name,
        "wb"
    ) as wav_file:

        voz.synthesize(
            texto,
            wav_file
        )

    return arquivo.name


# =========================================================
# INTERFACE
# =========================================================

st.markdown("### 🎙️ Vozes")

st.markdown(
    "#### 👨 Masculina 1 — Natural"
)

st.write(
    "Ouça a voz antes de escolher."
)


if st.button(
    "▶️ Ouvir amostra",
    use_container_width=True
):

    try:

        with st.spinner(
            "🎙️ Preparando a voz..."
        ):

            audio = gerar_audio(
                "Olá! Esta é uma amostra da voz masculina natural do DarkCut AI."
            )


        with open(
            audio,
            "rb"
        ) as arquivo:

            dados = arquivo.read()


        st.audio(
            dados,
            format="audio/wav"
        )


        st.success(
            "✅ Amostra pronta!"
        )


    except Exception as erro:

        st.error(
            "❌ Erro ao gerar a voz."
        )

        st.code(
            str(erro)
        )


st.markdown("---")

st.info(
    "🔧 Estamos testando a primeira voz. "
    "Depois adicionaremos as outras cinco."
)
