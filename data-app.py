import streamlit as st
import pandas as pd
import os
from io import BytesIO
from PIL import Image

st.set_page_config(page_title="Data & Image Converter", layout="wide")

st.title("Universal File Converter")
st.write("Transform your files between different formats, including CSV, Excel, PNG, JPEG, WEBP, and more.")

uploaded_files = st.file_uploader(
    "Upload your files (CSV, Excel, PNG, JPEG, WEBP, BMP, TIFF, GIF):",
    type=["csv", "xlsx", "png", "jpeg", "jpg", "webp", "bmp", "tiff", "gif"],
    accept_multiple_files=True
)

processing_done = False

if uploaded_files:
    for file in uploaded_files:
        file_extension = os.path.splitext(file.name)[-1].lower()

        if file_extension in [".csv", ".xlsx"]:
            try:
                if file_extension == ".csv":
                    df = pd.read_csv(file)
                elif file_extension == ".xlsx":
                    df = pd.read_excel(file, engine='openpyxl')

                st.write(f"📄 File Name: {file.name}")
                st.write(f"📏 File Size: {file.size / 1024:.2f} KB")
                st.write("🔍 Preview of the Uploaded File:")
                st.dataframe(df.head())

                st.subheader("🛠️ Data Cleaning Options")
                if st.checkbox(f"Clean Data for {file.name}"):
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button(f"Remove Duplicates from {file.name}"):
                            df.drop_duplicates(inplace=True)
                            st.write("✅ Duplicates Removed!")
                    with col2:
                        if st.button(f"Fill Missing Values for {file.name}"):
                            numeric_cols = df.select_dtypes(include=['number']).columns
                            df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].mean())
                            st.write("✅ Missing Values in Numeric Columns Filled with Column Means!")

                st.subheader("🎯 Select Columns to Convert")
                columns = st.multiselect(f"Choose Columns for {file.name}", df.columns, default=df.columns)
                df = df[columns]

                st.subheader("📊 Data Visualization")
                if st.checkbox(f"Show Visualization for {file.name}"):
                    st.bar_chart(df.select_dtypes(include='number').iloc[:, :2])

                st.subheader("🔄 Conversion Options")
                conversion_type = st.radio(f"Convert {file.name} to:", ["CSV", "Excel"], key=file.name)
                if st.button(f"Convert {file.name}"):
                    buffer = BytesIO()
                    if conversion_type == "CSV":
                        df.to_csv(buffer, index=False)
                        file_name = file.name.replace(file_extension, ".csv")
                        mime_type = "text/csv"
                    elif conversion_type == "Excel":
                        df.to_excel(buffer, index=False, engine='openpyxl')
                        file_name = file.name.replace(file_extension, ".xlsx")
                        mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    buffer.seek(0)

                    st.download_button(
                        label=f"⬇️ Download {file.name} as {conversion_type}",
                        data=buffer,
                        file_name=file_name,
                        mime=mime_type
                    )
                    processing_done = True
            except Exception as e:
                st.error(f"Error processing {file.name}: {e}")

        elif file_extension in [".png", ".jpeg", ".jpg", ".webp", ".bmp", ".tiff", ".gif"]:
            try:
                image = Image.open(file)
                st.image(image, caption=f"Preview: {file.name}", use_container_width=True)  # ✅ Fixed warning

                st.subheader("🔄 Convert Image To")
                img_conversion_type = st.radio(
                    f"Convert {file.name} to:", ["PNG", "JPEG", "WEBP", "BMP", "TIFF", "GIF"], key=file.name
                )

                if st.button(f"Convert {file.name}"):
                    buffer = BytesIO()
                    file_name = file.name.rsplit(".", 1)[0] + f".{img_conversion_type.lower()}"

                    # 🔥 FIX: Convert RGBA to RGB for JPEG format
                    if img_conversion_type.upper() == "JPEG" and image.mode == "RGBA":
                        image = image.convert("RGB")

                    image.save(buffer, format=img_conversion_type.upper())
                    mime_type = f"image/{img_conversion_type.lower()}"
                    buffer.seek(0)

                    st.download_button(
                        label=f"⬇️ Download {file.name} as {img_conversion_type}",
                        data=buffer,
                        file_name=file_name,
                        mime=mime_type
                    )
                    processing_done = True
            except Exception as e:
                st.error(f"Error processing {file.name}: {e}")

        else:
            st.error(f"Unsupported file type: {file_extension}")

if processing_done:
    st.success("🎉 All files processed successfully!")
