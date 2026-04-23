import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import zipfile
import io

# --- ΡΥΘΜΙΣΕΙΣ ΣΕΛΙΔΑΣ ---
st.set_page_config(page_title="Thesis Dashboard - 1821 Info Flows", page_icon="🏛️", layout="wide")

# --- ΣΥΝΑΡΤΗΣΕΙΣ ΦΟΡΤΩΣΗΣ ΔΕΔΟΜΕΝΩΝ ---
@st.cache_data
def load_main_data():
    try:
        with zipfile.ZipFile("THESIS_WITH_ORIENTATION.zip", 'r') as z:
            csv_files = [name for name in z.namelist() if not name.startswith('__MACOSX') and not name.startswith('._') and name.endswith('.csv')]
            if not csv_files:
                return pd.DataFrame()
                
            real_file_name = csv_files[0]
            with z.open(real_file_name) as f:
                content_bytes = f.read()
        
        text_content = content_bytes.decode('utf-8', errors='replace')
        df = pd.read_csv(io.StringIO(text_content), sep=',', low_memory=False, on_bad_lines='skip')
        if len(df.columns) < 3:
            df = pd.read_csv(io.StringIO(text_content), sep=';', low_memory=False, on_bad_lines='skip')
        
        df.columns = df.columns.str.lower().str.strip()
        
        # 1. Φιλτράρισμα στα 55k (Directly Relevant)
        if 'ai_relevance' in df.columns:
            df = df[df['ai_relevance'].astype(str).str.lower().str.strip() == 'directly_relevant'].copy()
        
        # 2. ΔΙΟΡΘΩΣΗ: Ασφαλής διαχείριση κενών κελιών (NaN) & Κεφαλαίων
        if 'country' in df.columns:
            # Μετατροπή σε κεφαλαία (GB, FR) και προστασία κενών
            df['country'] = df['country'].astype(str).str.upper().replace('NAN', 'ΑΓΝΩΣΤΗ')
            
        if 'ai_stance' in df.columns:
            df['ai_stance'] = df['ai_stance'].fillna('Άγνωστη Στάση').astype(str).replace('nan', 'Άγνωστη Στάση')

        if 'ai_topic' in df.columns:
            df['ai_topic'] = df['ai_topic'].fillna('Άγνωστο Θέμα').astype(str).replace('nan', 'Άγνωστο Θέμα')
        
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'], errors='coerce')
            # Όσα άρθρα δεν έχουν σωστό έτος, παίρνουν το 0 για να μην διαγραφούν
            df['year_val'] = df['date'].dt.year.fillna(0) 
            
        return df
    except Exception as e:
        st.error(f"Σφάλμα φόρτωσης: {e}")
        return pd.DataFrame()

df_main = load_main_data()

if df_main.empty:
    st.title("🏛️ Ψηφιακό Παράρτημα")
    st.warning("Αναμονή για φόρτωση δεδομένων...")
    st.stop()

# --- ΠΛΑΪΝΗ ΜΠΑΡΑ (SIDEBAR) ΦΙΛΤΡΩΝ ---
st.sidebar.header("🎛️ Φίλτρα Ανάλυσης")
st.sidebar.markdown("Προσάρμοσε τα δεδομένα σε πραγματικό χρόνο:")

# Φίλτρο Χώρας
available_countries = sorted(df_main['country'].unique().tolist())
selected_countries = st.sidebar.multiselect("Επιλογή Χώρας (Country):", available_countries, default=available_countries)

# Φίλτρο Έτους
valid_years = df_main[df_main['year_val'] > 0]['year_val']
min_year = int(valid_years.min()) if not valid_years.empty else 1821
max_year = int(valid_years.max()) if not valid_years.empty else 1832
selected_years = st.sidebar.slider("Επιλογή Περιόδου (Έτη):", min_value=min_year, max_value=max_year, value=(min_year, max_year))

# Φίλτρο Στάσης
if 'ai_stance' in df_main.columns:
    available_stances = sorted(df_main['ai_stance'].unique().tolist())
    selected_stances = st.sidebar.multiselect("Πολιτική Στάση (Stance):", available_stances, default=available_stances)
else:
    selected_stances = []

# Εφαρμογή Φίλτρων
# Κρατάμε και τα άρθρα χωρίς έτος (0) αν ο χρήστης δεν έχει πειράξει το slider
year_filter = (df_main['year_val'] >= selected_years[0]) & (df_main['year_val'] <= selected_years[1])
if selected_years[0] == min_year and selected_years[1] == max_year:
    year_filter = year_filter | (df_main['year_val'] == 0)

df_filtered = df_main[
    (df_main['country'].isin(selected_countries)) &
    year_filter
]

if selected_stances:
    df_filtered = df_filtered[df_filtered['ai_stance'].isin(selected_stances)]

# --- ΕΠΙΚΕΦΑΛΙΔΑ ---
st.title("🏛️ Ψηφιακό Παράρτημα: Διακρατικές Ροές Πληροφορίας")
st.markdown(f"### Ενεργό Corpus: **{len(df_filtered):,}** / {len(df_main):,} Άρθρα")
st.divider()

# --- ΚΑΡΤΕΛΕΣ ---
tab_stats, tab_flows, tab_archive = st.tabs(["📊 Στατιστικά & Θεματολογία", "🌍 Ροές Ειδήσεων (Sankey)", "🔍 Ψηφιακό Αρχείο (Αναζήτηση)"])

# ==========================================
# ΚΑΡΤΕΛΑ 1: ΣΤΑΤΙΣΤΙΚΑ 
# ==========================================
with tab_stats:
    col1, col2, col3 = st.columns(3)
    col1.metric("Άρθρα (Βάσει Φίλτρων)", f"{len(df_filtered):,}")
    col2.metric("Εφημερίδες", df_filtered['newspaper_title'].nunique() if 'newspaper_title' in df_filtered.columns else "N/A")
    col3.metric("Χώρες", df_filtered['country'].nunique() if 'country' in df_filtered.columns else "N/A")

    st.divider()
    
    # Χρώματα για τις χώρες (GB μπλε, FR κόκκινο, ΑΓΝΩΣΤΗ γκρι)
    color_map = {'GB': '#1f77b4', 'FR': '#d62728', 'ΑΓΝΩΣΤΗ': '#7f7f7f'}

    c1, c2 = st.columns(2)
    with c1:
        st.subheader("📅 Αρθρογραφία ανά Έτος")
        if not df_filtered.empty:
            df_chart = df_filtered[df_filtered['year_val'] > 0] # Κρύβουμε τα μηδενικά από το γράφημα
            fig_year = px.histogram(df_chart, x="year_val", color="country", barmode="group", color_discrete_map=color_map)
            st.plotly_chart(fig_year, use_container_width=True)
    
    with c2:
        st.subheader("⚖️ Πολιτική Στάση ανά Χώρα")
        if 'ai_stance' in df_filtered.columns and not df_filtered.empty:
            fig_sun = px.sunburst(df_filtered, path=['country', 'ai_stance'], color='country', color_discrete_map=color_map)
            st.plotly_chart(fig_sun, use_container_width=True)

    st.divider()

    st.subheader("🏷️ Κυρίαρχη Θεματολογία (AI Topics)")
    if 'ai_topic' in df_filtered.columns and not df_filtered.empty:
        top_topics = df_filtered['ai_topic'].value_counts().nlargest(15).reset_index()
        top_topics.columns = ['Θέμα', 'Πλήθος Άρθρων']
        fig_topics = px.bar(top_topics, x='Πλήθος Άρθρων', y='Θέμα', orientation='h', color='Πλήθος Άρθρων', color_continuous_scale='Blues')
        fig_topics.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig_topics, use_container_width=True)

# ==========================================
# ΚΑΡΤΕΛΑ 2: TOP 100 INFO FLOWS
# ==========================================
with tab_flows:
    st.subheader("Χαρτογράφηση Ροής: Πηγή (Origin) ➔ Κέντρο Έκδοσης")
    st.caption("Τα δεδομένα προσαρμόζονται βάσει των φίλτρων που έχεις επιλέξει αριστερά.")
    
    if not df_filtered.empty and 'news_origin' in df_filtered.columns and 'publication_place' in df_filtered.columns:
        flow_df = df_filtered.dropna(subset=['news_origin', 'publication_place'])
        flows = flow_df.groupby(['news_origin', 'publication_place']).size().reset_index(name='counts')
        top_100 = flows.sort_values(by='counts', ascending=False).head(100)
        
        if not top_100.empty:
            all_nodes = list(pd.concat([top_100['news_origin'], top_100['publication_place']]).unique())
            node_map = {node: i for i, node in enumerate(all_nodes)}
            
            fig_sankey = go.Figure(data=[go.Sankey(
                node = dict(pad = 15, thickness = 20, label = all_nodes, color = "blue"),
                link = dict(source = top_100['news_origin'].map(node_map), 
                            target = top_100['publication_place'].map(node_map), 
                            value = top_100['counts'], 
                            color = "rgba(100, 100, 255, 0.4)")
            )])
            fig_sankey.update_layout(height=600)
            st.plotly_chart(fig_sankey, use_container_width=True)
        else:
            st.info("Δεν υπάρχουν αρκετά δεδομένα ροής για τα επιλεγμένα φίλτρα.")

# ==========================================
# ΚΑΡΤΕΛΑ 3: ΨΗΦΙΑΚΟ ΑΡΧΕΙΟ (ΑΝΑΖΗΤΗΣΗ)
# ==========================================
with tab_archive:
    st.subheader("🔍 Μηχανή Αναζήτησης στο Κείμενο των Εφημερίδων")
    st.caption("Ψάξε για πρόσωπα, τοποθεσίες ή γεγονότα μέσα στο καθαρισμένο κείμενο.")
    
    if 'content' in df_filtered.columns:
        search_query = st.text_input("Πληκτρολόγησε λέξη-κλειδί (π.χ. Ibrahim, Missolonghi, treaty):")
        
        if search_query:
            results = df_filtered[df_filtered['content'].astype(str).str.contains(search_query, case=False, na=False)]
            st.write(f"**Βρέθηκαν {len(results)} άρθρα που περιέχουν τη λέξη '{search_query}'.**")
            
            if not results.empty:
                display_cols = ['newspaper_title', 'date', 'country', 'ai_topic', 'ai_stance']
                available_cols = [c for c in display_cols if c in results.columns]
                st.dataframe(results[available_cols].head(100), use_container_width=True)
                
                st.markdown("### 📖 Ανάγνωση Άρθρου")
                selected_article = st.selectbox("Επίλεξε ένα άρθρο από τα αποτελέσματα:", 
                                                results['newspaper_title'].astype(str) + " (" + results['date'].astype(str) + ")")
                
                if selected_article:
                    idx = results['newspaper_title'].astype(str) + " (" + results['date'].astype(str) + ")" == selected_article
                    article_text = results[idx]['content'].values[0]
                    st.info(article_text)
    else:
        st.warning("Δεν βρέθηκε η στήλη 'content' για αναζήτηση.")
