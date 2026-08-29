import streamlit as st
import whisper
import tempfile
import os

st.set_page_config(
    page_title="DarkCut AI",
    page_icon="🎬"
)

st.title("🎬 DarkCut AI")
st.subheader("Sua IA de vídeos e cortes")

# Estado da aplicação
if "cortes" not in st.session_state:
    st.session_state.cortes = []

if "video_path" not in st.session_state:
    st.session_state.video_path = None

if "video_bytes" not in st.session_state:
    st.session_state.video_bytes = None

if "corte_selecionado" not in st.session_state:
    st.session_state.corte_selecionado = None


video = st.file_uploader(
    "📤 Envie seu vídeo",
    type=["mp4", "mov", "avi", "mkv"]
)

if video:

    st.success("Vídeo recebido! 🚀")

    # Guarda o vídeo na sessão
    st.session_state.video_bytes = video.getvalue()

    st.video(st.session_state.video_bytes)

    if st.button("🤖 Encontrar melhores cortes"):

        with st.spinner("🧠 Analisando o vídeo..."):

            with tempfile.NamedTemporaryFile(
                delete=False,
                suffix=".mp4"
            ) as arquivo:

                arquivo.write(st.session_state.video_bytes)
                caminho = arquivo.name

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

                cortes.append({
                    "inicio": inicio,
                    "fim": fim,
                    "texto": " ".join(textos)
                })

                inicio = None
                textos = []

        st.session_state.cortes = cortes

        os.remove(caminho)

        st.success(
            f"🔥 {len(cortes)} corte(s) encontrado(s)!"
        )


# Mostrar cortes salvos
if st.session_state.cortes:

    st.subheader("✂️ Cortes sugeridos")

    for i, corte in enumerate(st.session_state.cortes):

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
            f"🎯 Selecionar Corte {i + 1}",
            key=f"selecionar_{i}"
        ):

            st.session_state.corte_selecionado = i


# Mostrar seleção
if st.session_state.corte_selecionado is not None:

    numero = st.session_state.corte_selecionado + 1
    corte = st.session_state.cortes[
        st.session_state.corte_selecionado
    ]

    st.success(
        f"✅ Corte {numero} selecionado!"
    )

    st.write(
        f"⏱️ {corte['inicio']:.1f}s → "
        f"{corte['fim']:.1f}s"
    )

    st.info(
        "✂️ Próximo passo: gerar automaticamente "
        "o arquivo MP4 desse corte."
    )
