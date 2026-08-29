import streamlit as st
import wave
from piper import PiperVoice


st.set_page_config(
    page_title="DarkCut AI",
    page_icon="🎬"
)

st.title("🎬 DarkCut AI")
st.subheader("🎙️ Teste de voz")


MODELO = "voices/pt_BR-cadu-medium.onnx"


@st.cache_resource
def carregar_voz():
    return PiperVoice.load(MODELO)


def gerar_audio(texto):

    voz = carregar_voz()

    arquivo = "amostra.wav"

    with wave.open(arquivo, "wb") as wav_file:
        voz.synthesize(
            texto,
            wav_file
        )

    return arquivo


st.markdown("### 👨 Masculina 1 — Natural")

st.write(
    "Ouça a voz antes de escolher."
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
                "Olá! Esta é uma amostra da voz do DarkCut AI. "
                "Em breve você poderá criar histórias incríveis."
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
            "✅ Voz funcionando!"
        )

    except Exception as erro:

        st.error(
            "❌ Erro ao gerar a voz."
        )

        st.code(
            str(erro)
        )
