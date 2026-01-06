import streamlit as st
st.set_page_config(layout="wide")

# from markdownlit import mdlit
def matchups_sandbox():
    home_header, mid_header, away_header = st.columns(3)
    with home_header:
        st.markdown('''
        **Shadowkami**''')
    with mid_header:
        st.markdown('''
        vs''')
    with away_header:
        st.markdown('''
        **Slime Time**''')
    home_body, mid_body, away_body = st.columns(3)
    with home_body:
        st.markdown('<span style="font-size:10px; font-weight:400">HOME $\cdot$</span> <span style="font-size:20px; font-weight:600">SDK</span>',
    unsafe_allow_html=True
)
        st.markdown('''
            :red[164.04 pts] <span style="font-size:12px; font-weight:600; color:white">(proj 122,67, + 37,33)</span>''',unsafe_allow_html=True)
left, right = st.columns(2)
with left:
    matchups_sandbox()
with right:
    matchups_sandbox()