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
    "Escolha o tema, a voz e a duração. "
    "A IA cuidará do restante."
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

st.markdown("### 🎙️ Escolha sua voz")

vozes = [
    "👨 Masculina 1 — Natural",
    "👨 Masculina 2 — Grave",
    "👨 Masculina 3 — Dramática",
    "👩 Feminina 1 — Natural",
    "👩 Feminina 2 — Suave",
    "👩 Feminina 3 — Dramática"
]


for voz_item in vozes:

    col1, col2 = st.columns([4, 1])

    with col1:
        st.write(voz_item)

    with col2:
        st.button(
            "▶️",
            key="ouvir_" + voz_item
        )


voz = st.selectbox(
    "Selecione a voz para o vídeo",
    vozes
)


# =========================================================
# DURAÇÃO
# =========================================================

st.markdown("### ⏱️ Duração")

duracao = st.selectbox(
    "Escolha a duração do vídeo",
    [
        "30 segundos",
        "60 segundos",
        "90 segundos"
    ]
)


# =========================================================
# HISTÓRIA
# =========================================================

st.markdown("### 📚 Como a história será criada?")

tipo_historia = st.radio(
    "Escolha o modo",
    [
        "🔎 Procurar uma história como referência",
        "🤖 Criar uma história original",
        "🎲 Automático"
    ]
)


# =========================================================
# GERAR
# =========================================================

st.markdown("---")

if st.button(
    "✨ GERAR MEU VÍDEO",
    use_container_width=True
):

    st.success(
        "🚀 Configuração recebida!"
    )

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
        "📚 Modo: " + tipo_historia
    )

    st.info(
        "🧠 O gerador de histórias será conectado "
        "na próxima etapa."
    )


# =========================================================
# LIMITE
# =========================================================

st.markdown("---")

st.markdown("### 📊 Seu limite diário")

st.progress(0)

st.caption(
    "0 de 2 vídeos utilizados hoje"
)


# =========================================================
# PLANO
# =========================================================

st.markdown("---")

st.markdown("### 💰 Plano DarkCut")

st.write("R$ 30/mês")

st.write(
    "🎬 Até 2 vídeos por dia"
)


# =========================================================
# ÁREA DO VÍDEO
# =========================================================

st.markdown("---")

st.markdown("### 🎬 Seus vídeos")

st.info(
    "Depois da geração, seu vídeo aparecerá aqui "
    "para você assistir e baixar."
)


# =========================================================
# RODAPÉ
# =========================================================

st.markdown("---")

st.caption(
    "🎬 DarkCut AI — Ferramenta para criadores"
)
