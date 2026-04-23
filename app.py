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

        df.columns = df.columns.str.lower().str.strip()

        if 'ai_relevance' in df.columns:
            df = df[
                df['ai_relevance']
                .astype(str).str.lower().str.strip()
                .str.replace('_', '', regex=False)
                == 'directlyrelevant'
            ].copy()

        if 'year' in df.columns:
            df['year'] = pd.to_numeric(df['year'], errors='coerce').astype('Int64')

        if 'date' in df.columns:
            df['date_clean'] = df['date'].astype(str).str.replace(
                r'^(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)\s+',
                '', regex=True
            )
            df['date_parsed'] = pd.to_datetime(
                df['date_clean'], format='%d %B %Y', errors='coerce'
            )
            mask = df['date_parsed'].isna()
            df.loc[mask, 'date_parsed'] = pd.to_datetime(
                df.loc[mask, 'date'], errors='coerce'
            )
            df.drop(columns=['date_clean'], inplace=True)

        return df

    except FileNotFoundError:
        st.error("Zip file not found.")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Load error: {e}")
        return pd.DataFrame()


def main():
    st.set_page_config(page_title="Greek Revolution Press Dashboard", layout="wide")

    df = load_main_data()

    if df.empty:
        st.stop()

    st.write("Rows after filter:", len(df))
    st.write("ai_relevance values:", df['ai_relevance'].value_counts().to_dict())
    st.write("Columns found:", list(df.columns))


if __name__ == "__main__":
    main()