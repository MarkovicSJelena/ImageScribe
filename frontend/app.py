import httpx
import streamlit as st

from services.api_client import describe_image, fetch_styles
from utils.constants import FALLBACK_STYLES

st.set_page_config(page_title="ImageScribe", layout="centered")

st.title("ImageScribe")
st.caption("Upload an image to generate a description.")

try:
    style_options = fetch_styles()
except Exception:
    style_options = FALLBACK_STYLES

selected_style = st.selectbox(
    "Description style",
    options=style_options,
    index=style_options.index("Standard") if "Standard" in style_options else 0,
)

uploaded_file = st.file_uploader(
    "Choose an image",
    type=["jpg", "jpeg", "png", "webp"],
    help="Supported formats: JPG, JPEG, PNG, WEBP",
)

if uploaded_file is not None:
    st.image(uploaded_file, caption=uploaded_file.name, use_container_width=True)
    st.write(f"Selected style: {selected_style}")

    if st.button("Generate description", disabled=uploaded_file is None):
        try:
            with st.spinner("Generating description..."):
                result = describe_image(uploaded_file.getvalue(), uploaded_file.name, selected_style)
            st.subheader("Generated description")
            st.write(result)
        except httpx.HTTPStatusError as exc:
            status_code = exc.response.status_code
            detail = exc.response.json().get("detail", "Request failed.") if exc.response.headers.get("content-type", "").startswith("application/json") else str(exc)
            if status_code == 422:
                st.warning(f"Validation error: {detail}")
            elif status_code == 429:
                st.warning("Rate limit reached. Please wait a moment before trying again.")
            else:
                st.error(f"Backend returned an error ({status_code}). {detail}")
        except httpx.RequestError:
            st.error("The backend is unreachable. Please make sure the API is running.")
        except Exception as exc:
            st.error(f"Something went wrong: {exc}")
    else:
        st.info("Upload an image and click Generate description.")
else:
    st.info("Upload an image to begin.")
