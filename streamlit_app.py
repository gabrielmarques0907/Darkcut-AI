import streamlit as st
import piper

st.title("🎙️ Teste de voz DarkCut")

st.success("✅ O módulo Piper foi encontrado!")

st.write("Local do módulo:")
st.code(piper.__file__)
