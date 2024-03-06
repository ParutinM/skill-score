from typing import Tuple, Literal
import streamlit as st


def styling(text: str,
            tag: Literal["h1", "h2", "h3", "h4", "h5", "h6", "p"] = "h2",
            text_align: Literal["left", "right", "center", "justify"] = "center",
            font_size: int = 32) -> Tuple[str, bool]:
    style = f"text-align: {text_align};" \
            f"font-size: {font_size}px;"

    styled_text = f'<{tag} style="{style}">{text}</{tag}>'
    return styled_text, True


def upload_button_style():
    style = """
<style>
    # div[data-testid="stFileUploader"]>section[data-testid="stFileUploadDropzone"]>button[data-testid="baseButton-secondary"] {
    #    visibility:hidden;
    # }
    # div[data-testid="stFileUploader"]>section[data-testid="stFileUploadDropzone"]>button[data-testid="baseButton-secondary"]::after {
    #     content: "Открыть";
    #     visibility:visible;
    # }
    # div[data-testid="stFileDropzoneInstructions"]>div>span {
    #    visibility:hidden;
    # }
    # div[data-testid="stFileDropzoneInstructions"]>div>span::after {
    #    content:"Загрузить файл";
    #    visibility:visible;
    #    display:block;
    # }
    #  div[data-testid="stFileDropzoneInstructions"]>div>small {
    #    visibility:hidden;
    # }
    # div[data-testid="stFileDropzoneInstructions"]>div>small::before {
    #    content:"До 200 МБ";
    #    visibility:visible;
    #    display:block;
    # }
</style>
"""
    st.markdown(style, True)


def footer():
    ft = """
<style>
a:link , a:visited{
color: #BFBFBF;  /* theme's text color hex code at 75 percent brightness*/
background-color: transparent;
text-decoration: none;
}

a:hover,  a:active {
color: #0283C3; /* theme's primary color*/
background-color: transparent;
text-decoration: underline;
}

#page-container {
  position: relative;
  min-height: 10vh;
}

footer{
    visibility:hidden;
}

.footer {
position: relative;
left: 0;
top:230px;
bottom: 0;
width: 100%;
background-color: transparent;
color: #808080; /* theme's text color hex code at 50 percent brightness*/
text-align: left; /* you can replace 'left' with 'center' or 'right' if you want*/
}
</style>

<div id="page-container">

<div class="footer">
<p style='font-size: 0.875em;'>Made with <a style='display: inline; text-align: left;' href="https://streamlit.io/" target="_blank">Streamlit</a><br 'style= top:3px;'>
with <img src="https://em-content.zobj.net/source/skype/289/red-heart_2764-fe0f.png" alt="heart" height= "10"/><a style='display: inline; text-align: left;' href="https://github.com/ParutinM" target="_blank"> by ParutinM</a></p>
</div>

</div>
    """
    st.markdown(ft, True)


def center_zoom_picture():
    st.markdown(
        """
        <style>
            button[title^=Exit]+div [data-testid=stImage]{
                text-align: center;
                display: block;
                margin-left: auto;
                margin-right: auto;
                width: 100%;
            }
        </style>
        """, unsafe_allow_html=True
    )


def hide_links():
    st.markdown("""
        <style>
        /* Hide the link button */
        .stApp a:first-child {
            display: none;
        }

        .css-15zrgzn {display: none}
        .css-eczf16 {display: none}
        .css-jn99sy {display: none}
        </style>
        """, unsafe_allow_html=True)
