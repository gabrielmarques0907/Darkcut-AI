import streamlit as st

st.set_page_config(
    page_title="DarkCut AI",
    page_icon="🎬"
)

st.title("🎬 DarkCut AI")
st.subheader("Sua IA de vídeos e cortes")

st.write("Transforme vídeos longos em Shorts, Reels e TikToks.")

video = st.file_uploader(
    "📤 Envie seu vídeo",
    type=["mp4", "mov", "avi", "mkv"]
)

if video:
    st.success("Vídeo recebido! 🚀")
    st.video(video)

    st.info(
        "🤖 O DarkCut AI está pronto para receber "
        "o sistema de análise automática de cortes."
    )
