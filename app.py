import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import zipfile
import io
import re

# --- ΡΥΘΜΙΣΕΙΣ ΣΕΛΙΔΑΣ ---
st.set_page_config(page_title="Thesis Dashboard - 1821 Info Flows", page_icon="🏛️", layout="wide")

# ==========================================
# 📚 ΛΕΞΙΚΑ ΚΑΝΟΝΙΚΟΠΟΙΗΣΗΣ ΟΝΤΟΤΗΤΩΝ (NER)
# ==========================================
PERSON_ALIASES = {
    'Ibrahim Pasha': ['ibrahim', 'ibrahim pacha', 'ibrahim pasha', 'ibrahim pascha', 'pacha of egypt'],
    'Theodoros Kolokotronis': ['kolokotronis', 'colocotroni', 'colocotronis', 'kolokotroni'],
    'Sultan Mahmud II': ['mahmud', 'mahmoud', 'sultan', 'grand signior', 'mahmud ii'],
    'Lord Byron': ['byron', 'lord byron'],
    'Ioannis Kapodistrias': ['capodistrias', 'capo d\'istria', 'kapodistrias', 'count capodistrias'],
    'Admiral Codrington': ['codrington', 'edward codrington', 'admiral codrington'],
    'Reshid Pasha (Kiutahi)': ['reshid', 'kiutahi', 'redschid', 'redschid pacha'],
    'Alexander Ypsilantis': ['ypsilanti', 'ypsilantis', 'hypsilantes']
}

LOC_ALIASES = {
    'Missolonghi': ['missolonghi', 'mesolongi', 'missolongi', 'micsolonghi'],
    'Navarino': ['navarino', 'navarin'],
    'Constantinople': ['constantinople', 'istanbul', 'stamboul'],
    'Athens': ['athens', 'athènes'],
    'Peloponnese': ['peloponnese', 'morea', 'morée', 'peloponnesus'],
    'Smyrna': ['smyrna', 'izmir'],
    'London': ['london', 'londres']
}

def normalize_entities(entity_str, alias_dict):
    if pd.isna(entity_str) or not isinstance(entity_str, str):
        return ""
    entities = [e.strip() for e in entity_str.split(',')]
    cleaned = []
    for e in entities:
        e_lower = e.lower()
        matched = False
        for main_name, aliases in alias_dict.items():
            if e_lower in aliases:
                cleaned.append(main_name)
                matched = True
                break
        if not matched and e_lower != '':
            cleaned.append(e.title())
    return ", ".join(sorted(list(set(cleaned))))

# --- ΣΥΝΑΡΤΗΣΕΙΣ ΦΟΡΤΩΣΗΣ ΔΕΔΟΜΕΝΩΝ ---
@st.cache_data
def load_main_data():
    try:
        with zipfile.ZipFile("THESIS_RECLASSIFIED_FINAL.csv.zip", 'r') as z:
            csv_files = [name for name in z.namelist() if not name.startswith('__MACOSX') and not name.startswith('._') and name.endswith('.csv')]
            if not csv_files:
                return pd.DataFrame(), pd.Series()
            real_file_name = csv_files[0]
            with z.open(real_file_name) as f:
                content_bytes = f.read()
        
        text_content = content_bytes.decode('utf-8', errors='replace')
        df = pd.read_csv(io.StringIO(text_content), sep=',', low_memory=False, on_bad_lines='skip')
        if len(df.columns) < 3:
            df = pd.read_csv(io.StringIO(text_content), sep=';', low_memory=False, on_bad_lines='skip')
        
        df.columns = df.columns.str.lower().str.strip()
        
        if 'ai_relevance' in df.columns:
            raw_relevance = df['ai_relevance'].astype(str).str.lower().str.strip().value_counts()
            df = df[df['ai_relevance'].astype(str).str.lower().str.strip() == 'directly_relevant'].copy()
        else:
            raw_relevance = pd.Series()
            
        if 'ai_stance' in df.columns:
            df['ai_stance'] = df['ai_stance'].astype(str).fillna('Άγνωστη Στάση')
            df.loc[df['ai_stance'].str.lower().str.contains('relevant|irrelevant|unknown'), 'ai_stance'] = 'Άγνωστη Στάση'
        if 'ai_topic' in df.columns:
            df['ai_topic'] = df['ai_topic'].astype(str).fillna('Άγνωστο Θέμα')
            df.loc[df['ai_topic'].str.lower().str.contains('relevant|irrelevant|unknown'), 'ai_topic'] = 'Άγνωστο Θέμα'

        if 'country' in df.columns:
            df['country'] = df['country'].astype(str).str.strip().str.upper()
            country_map = {'UK': 'GB', 'GBR': 'GB', 'UNITED KINGDOM': 'GB', 'FRANCE': 'FR', 'NAN': 'ΑΓΝΩΣΤΗ'}
            df['country'] = df['country'].replace(country_map)
            
        df['year_val'] = 0
        if 'year' in df.columns:
            df['year_val'] = pd.to_numeric(df['year'], errors='coerce').fillna(0)
        if 'date' in df.columns:
            mask_zero = df['year_val'] == 0
            if mask_zero.any():
                extracted = df.loc[mask_zero, 'date'].astype(str).str.extract(r'(18[23]\d)')[0]
                df.loc[mask_zero, 'year_val'] = pd.to_numeric(extracted, errors='coerce').fillna(0)
        df.loc[(df['year_val'] < 1821) | (df['year_val'] > 1832), 'year_val'] = 0
        
        if 'entities_persons' in df.columns:
            df['entities_persons'] = df['entities_persons'].apply(lambda x: normalize_entities(x, PERSON_ALIASES))
        if 'entities_locations' in df.columns:
            df['entities_locations'] = df['entities_locations'].apply(lambda x: normalize_entities(x, LOC_ALIASES))
            
        return df, raw_relevance
    except Exception as e:
        st.error(f"Σφάλμα: {e}")
        return pd.DataFrame(), pd.Series()

df_main, raw_relevance = load_main_data()

# --- SIDEBAR ---
st.sidebar.header("🎛️ Φίλτρα")
valid_countries = sorted([c for c in df_main['country'].unique() if c != 'ΑΓΝΩΣΤΗ'])
sel_countries = st.sidebar.multiselect("Χώρες:", valid_countries, default=valid_countries)
v_years = df_main[df_main['year_val'] > 0]['year_val']
sel_years = st.sidebar.slider("Περίοδος:", int(v_years.min()), int(v_years.max()), (int(v_years.min()), int(v_years.max())))

df_filt = df_main[(df_main['country'].isin(sel_countries)) & (df_main['year_val'] >= sel_years[0]) & (df_main['year_val'] <= sel_years[1])]

# --- MAIN UI ---
st.title("🏛️ Ψηφιακό Παράρτημα: Διακρατικές Ροές Πληροφορίας")
st.divider()

t1, t2, t3, t4, t5 = st.tabs(["📊 Επισκόπηση", "📰 Εκδοτικό Τοπίο", "🧠 Θεματολογία", "🌍 Ροές", "👥 Οντότητες"])

with t1:
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Άρθρα", f"{len(df_filt):,}")
    col2.metric("Εφημερίδες", df_filt['newspaper_title'].nunique())
    
    # ΝΕΑ ΛΟΓΙΚΗ: Μοναδικά Πρόσωπα & Τοποθεσίες (Unique Counts)
    unique_persons = df_filt['entities_persons'].str.split(',').explode().str.strip().replace('', pd.NA).dropna().nunique()
    unique_locs = df_filt['entities_locations'].str.split(',').explode().str.strip().replace('', pd.NA).dropna().nunique()
    
    col3.metric("Μοναδικά Πρόσωπα", f"{unique_persons:,}")
    col4.metric("Μοναδικές Τοποθεσίες", f"{unique_locs:,}")
    
    st.divider()
    c_pie, c_line = st.columns([1, 2])
    with c_pie:
        st.subheader("📊 Σχετικότητα")
        fig_p = px.pie(values=raw_relevance.values, names=raw_relevance.index, hole=0.4)
        st.plotly_chart(fig_p, use_container_width=True)
    with c_line:
        st.subheader("📈 Όγκος ανά Έτος")
        df_v = df_filt[df_filt['year_val'] > 0].groupby(['year_val', 'country']).size().reset_index(name='c')
        fig_v = px.line(df_v, x='year_val', y='c', color='country', markers=True)
        st.plotly_chart(fig_v, use_container_width=True)

with t5:
    st.markdown("Top 20 Συχνότερες Αναφορές (Κανονικοποιημένες)")
    c7, c8 = st.columns(2)
    def plot_ner(column, color):
        items = df_filt[column].str.split(',').explode().str.strip().replace('', pd.NA).dropna()
        if not items.empty:
            t = items.value_counts().head(20).reset_index()
            t.columns = ['Οντότητα', 'Αναφορές']
            return px.bar(t, x='Αναφορές', y='Οντότητα', orientation='h', color_continuous_scale=color, color='Αναφορές')
    
    with c7:
        st.plotly_chart(plot_ner('entities_persons', 'Teal'), use_container_width=True)
    with c8:
        st.plotly_chart(plot_ner('entities_locations', 'Oranges'), use_container_width=True)
