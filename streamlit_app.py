import streamlit as st
import whisper
import tempfile
import os

st.set_page_config(
    page_title="DarkCut AI",
    page_icon="🎬"
)

st.title("🎬 DarkCut AI")
st.subheader("Encontre os melhores momentos do seu vídeo")

video = st.file_uploader(
    "📤 Envie seu vídeo",
    type=["mp4", "mov", "avi", "mkv"]
)

if video:

    st.success("Vídeo recebido! 🚀")
    st.video(video)

    if st.button("🤖 Encontrar melhores cortes"):

        with st.spinner("🧠 Analisando o vídeo..."):

            with tempfile.NamedTemporaryFile(
                delete=False,
                suffix=".mp4"
            ) as arquivo:

                arquivo.write(video.getbuffer())
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

        st.success(f"🔥 {len(cortes)} corte(s) encontrado(s)!")

        for i, corte in enumerate(cortes):

            st.markdown(
                f"### ✂️ Corte {i + 1}"
            )

            st.write(
                f"⏱️ {corte['inicio']:.1f}s → "
                f"{corte['fim']:.1f}s"
            )

            st.write(
                f"📝 {corte['texto']}"
            )

            if st.button(
                f"🎬 Selecionar Corte {i + 1}",
                key=f"corte_{i}"
            ):

                st.session_state["corte_selecionado"] = corte
                st.success(
                    f"✅ Corte {i + 1} selecionado!"
                )

        if "corte_selecionado" in st.session_state:

            corte = st.session_state["corte_selecionado"]

            st.subheader("🎯 Corte selecionado")

            st.write(
                f"{corte['inicio']:.1f}s → "
                f"{corte['fim']:.1f}s"
            )

            st.info(
                "🚧 Próxima etapa: gerar automaticamente "
                "o arquivo MP4 desse corte."
            )

        os.remove(caminho)
