import streamlit as st
import subprocess
import tempfile
import os
import urllib.request


st.set_page_config(
    page_title="DarkCut AI",
    page_icon="🎬",
    layout="centered"
)


st.title("🎬 DarkCut AI")
st.subheader("Crie vídeos automaticamente")


# =========================================================
# VOZ TESTE
# =========================================================

MODELO_URL = (
    "https://huggingface.co/rhasspy/piper-voices/"
    "resolve/main/pt/pt_BR/cadu/medium/"
    "pt_BR-cadu-medium.onnx"
)

CONFIG_URL = (
    "https://huggingface.co/rhasspy/piper-voices/"
    "resolve/main/pt/pt_BR/cadu/medium/"
    "pt_BR-cadu-medium.onnx.json"
)


@st.cache_resource
def baixar_modelo():

    pasta = os.path.join(
        tempfile.gettempdir(),
        "darkcut_voice"
    )

    os.makedirs(
        pasta,
        exist_ok=True
    )

    modelo = os.path.join(
        pasta,
        "voz.onnx"
    )

    config = os.path.join(
        pasta,
        "voz.onnx.json"
    )

    if not os.path.exists(modelo):

        urllib.request.urlretrieve(
            MODELO_URL,
            modelo
        )

    if not os.path.exists(config):

        urllib.request.urlretrieve(
            CONFIG_URL,
            config
        )

    return modelo, config


def gerar_amostra():

    modelo, config = baixar_modelo()

    texto = (
        "Esta é uma amostra de voz do DarkCut AI. "
        "Em breve você poderá escolher entre seis vozes."
    )

    arquivo = tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".wav"
    )

    arquivo.close()

    comando = [
        "python",
        "-m",
        "piper",
        "--model",
        modelo,
        "--config",
        config,
        "--output_file",
        arquivo.name
    ]

    resultado = subprocess.run(
        comando,
        input=texto,
        text=True,
        capture_output=True
    )

    if resultado.returncode != 0:

        try:
            os.remove(arquivo.name)
        except:
            pass

        raise Exception(
            resultado.stderr
        )

    return arquivo.name


# =========================================================
# INTERFACE
# =========================================================

st.markdown("### 🎙️ Escolha sua voz")

st.markdown(
    "**👨 Masculina 1 — Natural**"
)

if st.button(
    "▶️ Ouvir amostra",
    use_container_width=True
):

    try:

        with st.spinner(
            "🎙️ Preparando voz..."
        ):

            audio = gerar_amostra()

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
            "❌ Não foi possível gerar a voz."
        )

        st.code(
            str(erro)
        )


# =========================================================
# RESTANTE DA INTERFACE
# =========================================================

st.markdown("---")

st.markdown("### 🎭 Tema")

tema = st.selectbox(
    "Escolha o tema",
    [
        "👻 Terror",
        "🏰 Histórias Medievais",
        "📖 Histórias Bíblicas",
        "🕵️ Mistérios",
        "👽 OVNIs e Fenômenos",
        "😱 Casos Bizarros",
        "🧟 Lendas e Criaturas",
        "📜 História",
        "🔥 Curiosidades",
        "❤️ Histórias Emocionantes"
    ]
)


st.markdown("### ⏱️ Duração")

duracao = st.selectbox(
    "Escolha a duração",
    [
        "30 segundos",
        "60 segundos",
        "90 segundos"
    ]
)


st.markdown("---")

if st.button(
    "✨ GERAR MEU VÍDEO",
    use_container_width=True
):

    st.info(
        "🧠 O gerador completo será conectado "
        "nas próximas etapas."
    )

    st.write("🎭 Tema:", tema)
    st.write("⏱️ Duração:", duracao)


st.markdown("---")

st.caption(
    "🎬 DarkCut AI — Ferramenta para criadores"
)
