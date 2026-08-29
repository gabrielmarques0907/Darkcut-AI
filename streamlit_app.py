import streamlit as st
from datetime import date


# =========================================================
# CONFIGURAÇÃO
# =========================================================

st.set_page_config(
    page_title="DarkCut AI",
    page_icon="🎬",
    layout="centered"
)


# =========================================================
# TÍTULO
# =========================================================

st.title("🎬 DarkCut AI")
st.subheader("Crie vídeos automaticamente para suas redes sociais")


st.markdown(
    "Escolha um tema, uma voz e a duração. "
    "A IA cuidará do restante."
)


# =========================================================
# TEMAS
# =========================================================

temas = {
    "👻 Terror": "terror",
    "🏰 Histórias Medievais": "medieval",
    "📖 Histórias Bíblicas": "biblia",
    "🕵️ Mistérios": "misterios",
    "👽 OVNIs e Fenômenos": "ovnis",
    "😱 Casos Bizarros": "casos_bizarros",
    "🧟 Lendas e Criaturas": "lendas",
    "📜 História": "historia",
    "🔥 Curiosidades": "curiosidades",
    "❤️ Histórias Emocionantes": "emocionantes"
}


st.markdown("### 🎭 Escolha o tema")

tema_escolhido = st.selectbox(
    "Tema do vídeo",
    list(temas.keys())
)


# =========================================================
# VOZES
# =========================================================

vozes = {
    "👨 Masculina 1 — Natural": "masculina_1",
    "👨 Masculina 2 — Grave": "masculina_2",
    "👨 Masculina 3 — Dramática": "masculina_3",
    "👩 Feminina 1 — Natural": "feminina_1",
    "👩 Feminina 2 — Suave": "feminina_2",
    "👩 Feminina 3 — Dramática": "feminina_3"
}


st.markdown("### 🎙️ Escolha a voz")

voz_escolhida = st.selectbox(
    "V
