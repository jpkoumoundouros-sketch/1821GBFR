import streamlit as st
import pandas as pd
import zipfile
import io

@st.cache_data
def load_main_data():
    try:
        with zipfile.ZipFile("THESIS_WITH_ORIENTATION.csv.zip", 'r') as z:
            csv_files = [
                name for name in z.namelist()
                if not name.startswith('__MACOSX')
                and not name.startswith('._')
                and name.endswith('.csv')
            ]
            if not csv_files:
                st.error("No CSV found in zip.")
                return pd.DataFrame()
            with z.open(csv_files[0]) as f:
                raw_bytes = f.read()

        df = pd.read_csv(
            io.BytesIO(raw_bytes), sep=',',
            low_memory=False, encoding='utf-8-sig', on_bad_lines='skip'
        )
        if len(df.columns) < 3:
            df = pd.read_csv(
                io.BytesIO(raw_bytes), sep=';',
                low_memory=False, encoding='utf-8-sig', on_bad_lines='skip'
            )

        return df  # RAW - no processing yet

    except Exception as e:
        st.error(f"Load error: {e}")
        return pd.DataFrame()


def main():
    st.set_page_config(page_title="Debug", layout="wide")

    df = load_main_data()
    if df.empty:
        st.stop()

    st.write("Total rows raw:", len(df))
    st.write("Num columns:", len(df.columns))
    st.write("First 25 column names:", list(df.columns[:25]))
    st.write("First 5 column repr:", [repr(c) for c in df.columns[:5]])

    rel_cols = [c for c in df.columns if 'relev' in str(c).lower()]
    st.write("Relevance-like columns:", rel_cols)

    if rel_cols:
        col = rel_cols[0]
        st.write(f"Value counts of '{col}':", df[col].value_counts().to_dict())


if __name__ == "__main__":
    main()
