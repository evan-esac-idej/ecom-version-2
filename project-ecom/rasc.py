import streamlit as st

if "show_dialog" not in st.session_state:
    st.session_state.show_dialog = False

def open_dialog():
    st.session_state.show_dialog = True

def close_dialog():
    st.session_state.show_dialog = False

st.button("Abrir diálogo", on_click=open_dialog)

if st.session_state.show_dialog:
    # Simula um diálogo
    st.markdown("### Confirmação")
    st.write("Deseja realmente realizar esta ação?")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Sim"):
            st.success("Ação confirmada!")
            close_dialog()
    with col2:
        if st.button("Não"):
            st.info("Ação cancelada")
            close_dialog()
