import streamlit as st
import pytesseract

st.title("CyberShield - Coming Soon!")

input_file_present = st.selectbox('PDF Input file?', ('No', 'Yes'))
st.write('You selected:', input_file_present)

input_txt = ""
if input_file_present == "Yes":
    image_file = st.file_uploader('Upload the image')

    # wait until resume is uploaded
    while image_file is None:
        time.sleep(1)

    text = pytesseract.image_to_string(image_file)
    st.write("\nconverted text = %s\n" % text)

