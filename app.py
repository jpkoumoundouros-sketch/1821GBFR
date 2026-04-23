import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import zipfile
import io
import re

# --- ΡΥΘΜΙΣΕΙΣ ΣΕΛΙΔΑΣ ---
st.set_page_config(page_title="Thesis Dashboard - 1821 Info Flows", page_icon="🏛️", layout="wide")

# --- ΣΥΝΑΡΤΗΣΕΙΣ ΦΟΡΤΩΣΗΣ ΔΕΔΟΜΕΝΩΝ ---
@st.cache_data
def load_main_data():
    try:
        # Άνοιγμα του ZIP
        with zipfile.ZipFile("THESIS_WITH_ORIENTATION.zip", 'r') as z:
            csv_files = [name for name in z.namelist() if not name.startswith('__MACOSX') and not name.startswith('._') and name.endswith('.csv')]
            if not csv_files:
                return pd.DataFrame()
                
            real_file_name = csv_files[0]
            with z.open(real_file_name) as f:
                content_bytes = f.read()
        
        # Αποκωδικοποίηση με προστασία χαρακτήρων
        text_content = content_bytes.decode('utf-8', errors='replace')
        
        # Δοκιμή διαχωριστικού (κόμμα ή ερωτηματικό)
        df = pd.read_csv(io.StringIO(text_content), sep=',', low_memory=False, on_bad_lines='skip')
        if len(df.columns) < 3:
            df = pd.read_csv(io.StringIO(text_content), sep=';', low_memory=False, on_bad_lines='skip')
        
        # Καθαρισμός στηλών
        df.columns = df.columns.str.lower().str.strip()
        
        # Φιλτράρισμα Directly Relevant
        if 'ai_relevance' in df.columns:
            df = df[df['ai_relevance'].astype(str).str.lower().str.strip() == 'directly_relevant'].copy()
        
        # --- 1. ΑΥΣΤΗΡΟΣ ΚΑΘΑΡΙΣΜΟΣ ΧΩΡΑΣ ---
        if 'country' in df.columns:
            df['country'] = df['country'].astype(str).str.strip().str.upper()
            # Mapping για όλες τις πιθανές γραφές
            country_map = {
                'UK': 'GB', 'GBR': 'GB', 'UNITED KINGDOM': 'GB', 'GREAT BRITAIN': 'GB',
                'FR': 'FR', 'FRA': 'FR', 'FRANCE': 'FR',
                'NAN': 'ΑΓΝΩΣΤΗ', 'NONE': 'ΑΓΝΩΣΤΗ'
            }
            df['country'] = df['country'].replace(country_map)
            
        # --- 2. ΑΥΣΤΗΡΟΣ ΚΑΘΑΡΙΣΜΟΣ ΕΤΟΥΣ (THE FIX) ---
        df['year_val'] = 0
        
        # Προσπάθεια Α: Από έτοιμη στήλη 'year'
        if 'year' in df.columns:
            df['year_val'] = pd.to_numeric(df['year'], errors='coerce').fillna(0)
            
        # Προσπάθεια Β: Από τη στήλη 'date' με Regex (ψάχνουμε 4 νούμερα που ξεκινούν με 18)
        if 'date' in df.columns:
            mask_zero = df['year_val'] == 0
            if mask_zero.any():
                # Εξαγωγή του πρώτου 4ψήφιου που μοιάζει με έτος 18xx
                extracted = df.loc[mask_zero, 'date'].astype(str).str.extract(r'(18[23]\d)')[0]
                df.loc[mask_zero, 'year_val'] = pd.to_numeric(extracted, errors='coerce').fillna(0)
        
        # Περιορισμός στα έτη της διατριβής (1821-1832)
        df.loc[(df['year_val'] < 1821) | (df['year_val'] > 1832), 'year_val'] = 0
        
        # Καθαρισμός Stance/Topic
        df['ai_stance'] = df['ai_stance'].fillna('Άγνωστη').astype(str).replace('nan', 'Άγνωστη')
        df['ai_topic'] = df['ai_topic'].fillna('Άγνωστο').astype(str).replace('nan', 'Άγνωστο')
            
        return df
    except Exception as e:
        st.error(f"Σφάλμα: {e}")
        return pd.DataFrame()

df_main = load_main_data()

# --- SIDEBAR ---
st.sidebar.header("🎛️ Φίλτρα")
if not df_main.empty:
    countries = sorted(df_main['country'].unique().tolist())
    sel_countries = st.sidebar.multiselect("Χώρες:", countries, default=countries)
    
    # Μόνο έτη > 0 για το slider
    valid_years = df_main[df_main['year_val'] > 0]['year_val']
    min_y, max_y = int(valid_years.min()), int(valid_years.max())
    sel_years = st.sidebar.slider("Έτη:", min_y, max_y, (min_y, max_y))
    
    # Εφαρμογή
    df_filtered = df_main[
        (df_main['country'].isin(sel_countries)) & 
        (df_main['year_val'] >= sel_years[0]) & 
        (df_main['year_val'] <= sel_years[1])
    ]
    
    st.sidebar.download_button("Λήψη Δεδομένων", df_filtered.to_csv(index=False), "data.csv")

# --- MAIN UI ---
st.title("🏛️ Ψηφιακό Παράρτημα Διατριβής")
st.markdown(f"**Σύνολο Άρθρων:** {len(df_filtered):,} (Directly Relevant)")
st.divider()

tab1, tab2, tab3 = st.tabs(["📊 Επισκόπηση", "🌍 Ροές Πληροφορίας", "🔍 Αρχείο"])

with tab1:
    col1, col2 = st.columns([2, 1])
    with col1:
        st.subheader("📈 Όγκος Δημοσιεύσεων ανά Έτος & Χώρα")
        # Εμφανίζουμε μόνο έτη > 0
        df_chart = df_filtered[df_filtered['year_val'] > 0].groupby(['year_val', 'country']).size().reset_index(name='count')
        fig = px.line(df_chart, x='year_val', y='count', color='country', markers=True,
                      color_discrete_map={'GB': '#1f77b4', 'FR': '#d62728'})
        st.plotly_chart(fig, use_container_width=True)
        
    with col2:
        st.subheader("⚖️ Πολιτική Στάση")
        fig_sun = px.sunburst(df_filtered, path=['country', 'ai_stance'], color='country',
                               color_discrete_map={'GB': '#1f77b4', 'FR': '#d62728'})
        st.plotly_chart(fig_sun, use_container_width=True)

with tab2:
    st.subheader("🌍 Διακρατικές Ροές (Top 100)")
    if 'news_origin' in df_filtered.columns and 'publication_place' in df_filtered.columns:
        flows = df_filtered.dropna(subset=['news_origin', 'publication_place']).groupby(['news_origin', 'publication_place']).size().reset_index(name='c')
        top = flows.sort_values('c', ascending=False).head(100)
        nodes = list(pd.concat([top['news_origin'], top['publication_place']]).unique())
        n_map = {n: i for i, n in enumerate(nodes)}
        fig_sk = go.Figure(go.Sankey(node=dict(label=nodes), link=dict(source=top['news_origin'].map(n_map), target=top['publication_place'].map(n_map), value=top['c'])))
        st.plotly_chart(fig_sk, use_container_width=True)

with tab3:
    search = st.text_input("Αναζήτηση στο κείμενο:")
    if search:
        res = df_filtered[df_filtered['content'].astype(str).str.contains(search, case=False, na=False)]
        st.dataframe(res[['newspaper_title', 'date', 'country', 'ai_topic']].head(50))
