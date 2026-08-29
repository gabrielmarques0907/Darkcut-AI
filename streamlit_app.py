import streamlit as st


# =========================================================
# CONFIGURAÇÃO
# =========================================================

st.set_page_config(
    page_title="DarkCut AI",
    page_icon="🎬",
    layout="centered"
)


# =========================================================
# CABEÇALHO
# =========================================================

st.title("🎬 DarkCut AI")

st.subheader(
    "Crie vídeos automaticamente para suas redes sociais"
)

st.write(
    "Escolha um tema, uma voz e a duração. "
    "A inteligência artificial cuidará do restante."
)


# =========================================================
# TEMAS
# =========================================================

temas = [
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


st.markdown("### 🎭 Escolha o tema")

tema = st.selectbox(
    "Tema do vídeo",
    temas
)


# =========================================================
# VOZES
# =========================================================

vozes = [
    "👨 Masculina 1 — Natural",
    "👨 Masculina 2 — Grave",
    "👨 Masculina 3 — Dramática",
    "👩 Feminina 1 — Natural",
    "👩 Feminina 2 — Suave",
    "👩 Feminina 3 — Dramática"
]


st.markdown("### 🎙️ Escolha a voz")

voz = st.selectbox(
    "Voz da narração",
    vozes
)


# =========================================================
# DURAÇÃO
# =========================================================

st.markdown("### ⏱️ Duração do vídeo")

duracao = st.selectbox(
    "Escolha a duração",
    [
        "30 segundos",
        "60 segundos",
        "90 segundos"
    ]
)


# =========================================================
# ORIGEM DA HISTÓRIA
# =========================================================

st.markdown("### 📚 Origem da história")

tipo_historia = st.radio(
    "Como você quer que a IA encontre/crie a história?",
    [
        "🔎 Procurar uma história como referência",
        "🤖 Criar uma história original",
        "🎲 Automático"
    ]
)


# =========================================================
# BOTÃO GERAR
# =========================================================

st.markdown("---")

gerar = st.button(
    "✨ GERAR MEU VÍDEO",
    use_container_width=True
)


if gerar:

    st.session_state["gerando"] = True

    st.success(
        "🚀 Configuração recebida!"
    )

    st.markdown("### ⚙️ Configurações escolhidas")

    st.write(
        "🎭 Tema: " + tema
    )

    st.write(
        "🎙️ Voz: " + voz
    )

    st.write(
        "⏱️ Duração: " + duracao
    )

    st.write(
        "📚 Tipo: " + tipo_historia
    )

    st.info(
        "🧠 O motor de inteligência artificial "
        "será conectado na próxima etapa."
    )


# =========================================================
# ÁREA DO VÍDEO
# =========================================================

if "gerando" in st.session_state:

    st.markdown("---")

    st.markdown("### 🎬 Seu vídeo")

    st.write(
        "O vídeo gerado aparecerá aqui."
    )


# =========================================================
# LIMITE DIÁRIO
# =========================================================

st.markdown("---")

st.markdown("### 📊 Limite diário")

st.progress(0)

st.caption(
    "0 de 2 vídeos utilizados hoje"
)


# =========================================================
# PLANO
# =========================================================

st.markdown("---")

st.markdown("### 💰 Plano DarkCut")

st.write(
    "Plano: R$ 30/mês"
)

st.write(
    "🎬 Até 2 vídeos por dia"
)


# =========================================================
# RODAPÉ
# =========================================================

st.markdown("---")

st.caption(
    "🎬 DarkCut AI — Ferramenta para criadores de conteúdo"
)
