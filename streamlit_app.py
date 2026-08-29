import streamlit as st
import tempfile
import os
import wave
from piper import PiperVoice


st.set_page_config(
    page_title="DarkCut AI",
    page_icon="🎬"
)

st.title("🎬 DarkCut AI")
st.subheader("Teste de voz")


# =========================================================
# CONFIGURAÇÃO DA VOZ
# =========================================================

MODELO = "pt_BR-cadu-medium.onnx"


# =========================================================
# CARREGAR VOZ
# =========================================================

@st.cache_resource
def carregar_voz():

    return PiperVoice.load(MODELO)


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

    with wave.open(arquivo.name, "wb") as wav_file:

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
    "Ouça uma amostra antes de escolher."
)


if st.button(
    "▶️ Ouvir amostra",
    use_container_width=True
):

    try:

        with st.spinner(
            "🎙️ Gerando amostra..."
        ):

            audio = gerar_audio(
                "Olá! Esta é uma amostra da voz masculina do DarkCut AI."
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
            "✅ Voz pronta!"
        )

    except Exception as erro:

        st.error(
            "❌ Não foi possível gerar a voz."
        )

        st.code(
            str(erro)
        )


st.markdown("---")

st.info(
    "🔧 Estamos testando a primeira voz. "
    "Depois adicionaremos as outras cinco."
)
