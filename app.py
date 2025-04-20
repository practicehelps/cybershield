import time
import streamlit as st
import pytesseract
from PIL import Image

st.title("CyberShield")
st.write("Upload an image containing IP addresses. Let the agent use multiple data sources/tools like virus total, shodan to answer questions like malaciousness or ip reputation")

input_file_present = st.selectbox('Image Input file?', ('No', 'Yes'))
st.write('You selected:', input_file_present)

input_txt = ""
if input_file_present == "Yes":
    image_file = st.file_uploader('Upload the image')

    # wait until resume is uploaded
    while image_file is None:
        time.sleep(1)

    im = Image.open(image_file)
    text = pytesseract.image_to_string(im)
    #st.write("\nconverted text = %s\n" % text)

    input_prompt = st.text_area(
        "Ask a question from the uploaded image:",
        "Pick any IP address from the image and detect if it is malicious",
    )
    st.button("Submit", type="primary")
    if st.button("Submit"):
        st.write("Logic to detect the maliciousness of the IP is in progress. Please check back in a while. Thank you.")

