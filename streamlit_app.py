import streamlit as st
import whisper
import tempfile
import os
import subprocess

st.set_page_config(
    page_title="DarkCut AI",
    page_icon="🎬"
)

st.title("🎬 DarkCut AI")
st.subheader("Sua IA de vídeos e cortes")

if "cortes" not in st.session_state:
    st.session_state.cortes = []

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


if st.session_state.cortes:

    st.subheader("✂️ Cortes sugeridos")

    for i, corte in enumerate(st.session_state.cortes):

        st.markdown(f"### 🎬 Corte {i + 1}")

        st.write(
            f"⏱️ {corte['inicio']:.1f}s → "
            f"{corte['fim']:.1f}s"
        )

        st.write(f"📝 {corte['texto']}")

        if st.button(
            f"🎯 Selecionar Corte {i + 1}",
            key=f"selecionar_{i}"
        ):
            st.session_state.corte_selecionado = i


if st.session_state.corte_selecionado is not None:

    i = st.session_state.corte_selecionado
    corte = st.session_state.cortes[i]

    st.success(f"✅ Corte {i + 1} selecionado!")

    if st.button("✂️ Gerar MP4 deste corte"):

        with st.spinner("🎬 Gerando seu corte..."):

            entrada = tempfile.NamedTemporaryFile(
                delete=False,
                suffix=".mp4"
            )

            entrada.write(st.session_state.video_bytes)
            entrada.close()

            saida = tempfile.NamedTemporaryFile(
                delete=False,
                suffix=".mp4"
            )
            saida.close()

            comando = [
                "ffmpeg",
                "-y",
                "-ss",
                str(corte["inicio"]),
                "-i",
                entrada.name,
                "-t",
                str(corte["fim"] - corte["inicio"]),
                "-c:v",
                "libx264",
                "-c:a",
                "aac",
                saida.name
            ]

            processo = subprocess.run(
                comando,
                capture_output=True,
                text=True
            )

            if processo.returncode != 0:
                st.error("❌ Não foi possível gerar o corte.")
                st.code(processo.stderr)
            else:
                st.success("🎉 Corte gerado com sucesso!")

                with open(saida.name, "rb") as arquivo:
                    video_cortado = arquivo.read()

                st.video(video_cortado)

                st.download_button(
                    "⬇️ Baixar MP4",
                    data=video_cortado,
                    file_name=f"darkcut_corte_{i + 1}.mp4",
                    mime="video/mp4"
                )

            os.remove(entrada.name)
            os.remove(saida.name)
