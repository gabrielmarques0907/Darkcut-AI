import streamlit as st
import whisper
import tempfile
import os
import subprocess
import re

st.set_page_config(
    page_title="DarkCut AI",
    page_icon="🎬"
)

st.title("🎬 DarkCut AI")
st.subheader("IA para encontrar os melhores cortes")

if "cortes" not in st.session_state:
    st.session_state.cortes = []

if "video_bytes" not in st.session_state:
    st.session_state.video_bytes = None

if "corte_selecionado" not in st.session_state:
    st.session_state.corte_selecionado = None


def pontuar(texto, duracao):
    pontos = 50
    texto_lower = texto.lower()

    palavras = [
        "segredo", "nunca", "sempre", "importante",
        "problema", "verdade", "incrível", "melhor",
        "pior", "porque", "como", "por quê",
        "surpresa", "atenção", "erro", "descobri"
    ]

    for palavra in palavras:
        if palavra in texto_lower:
            pontos += 5

    if "?" in texto:
        pontos += 8

    if len(texto.split()) > 45:
        pontos += 5

    if 20 <= duracao <= 60:
        pontos += 8

    return min(pontos, 100)


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
            duracao = fim - inicio

            if duracao >= 30:

                texto = " ".join(textos)

                cortes.append({
                    "inicio": inicio,
                    "fim": fim,
                    "texto": texto,
                    "pontuacao": pontuar(
                        texto,
                        duracao
                    )
                })

                inicio = None
                textos = []

        cortes.sort(
            key=lambda x: x["pontuacao"],
            reverse=True
        )

        st.session_state.cortes = cortes

        os.remove(caminho)

        st.success(
            f"🔥 {len(cortes)} corte(s) encontrados!"
        )


if st.session_state.cortes:

    st.subheader("🔥 TOP CORTES")

    for i, corte in enumerate(
        st.session_state.cortes
    ):

        nota = corte["pontuacao"]

        st.markdown(
            f"### #{i + 1} — ⭐ {nota}/100"
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


if st.session_state.corte_selecionado is not None:

    i = st.session_state.corte_selecionado
    corte = st.session_state.cortes[i]

    st.success(
        f"✅ Corte #{i + 1} selecionado!"
    )

    if st.button("✂️ Gerar MP4 deste corte"):

        with st.spinner("🎬 Gerando corte..."):

            entrada = tempfile.NamedTemporaryFile(
                delete=False,
                suffix=".mp4"
            )

            entrada.write(
                st.session_state.video_bytes
            )

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
                str(
                    corte["fim"] -
                    corte["inicio"]
                ),
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

            if processo.returncode == 0:

                with open(
                    saida.name,
                    "rb"
                ) as arquivo:

                    video_cortado = arquivo.read()

                st.success(
                    "🎉 Corte gerado!"
                )

                st.video(video_cortado)

                st.download_button(
                    "⬇️ Baixar MP4",
                    data=video_cortado,
                    file_name=f"darkcut_{i + 1}.mp4",
                    mime="video/mp4"
                )

            else:

                st.error(
                    "❌ Erro ao gerar o corte."
                )

            os.remove(entrada.name)
            os.remove(saida.name)
