import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import zipfile

# --- ΡΥΘΜΙΣΕΙΣ ΣΕΛΙΔΑΣ ---
st.set_page_config(page_title="Thesis Dashboard - 1821 Info Flows", page_icon="📈", layout="wide")

# --- ΣΥΝΑΡΤΗΣΕΙΣ ΦΟΡΤΩΣΗΣ ΔΕΔΟΜΕΝΩΝ ---
@st.cache_data
def load_main_data():
    try:
        with zipfile.ZipFile("THESIS_WITH_ORIENTATION.csv.zip", 'r') as z:
            csv_files = [name for name in z.namelist() if not name.startswith('__MACOSX') and not name.startswith('._') and name.endswith('.csv')]
            if not csv_files:
                return pd.DataFrame()
                
            real_file_name = csv_files[0]
            with z.open(real_file_name) as f:
                # Χρήση sep=None και engine='python' για αυτόματη ανίχνευση (comma ή semicolon)
                df = pd.read_csv(f, sep=None, engine='python', low_memory=False, encoding='utf-8-sig', on_bad_lines='skip')
        
        # Καθαρισμός ονομάτων στηλών
        df.columns = df.columns.str.lower().str.strip()
        
        # 1. Φιλτράρισμα για το Τελικό Corpus (Directly Relevant) -> Στόχος: 55k+
        if 'ai_relevance' in df.columns:
            df = df[df['ai_relevance'].astype(str).str.lower().str.strip() == 'directly_relevant'].copy()
        
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'], errors='coerce')
            
        return df
    except Exception as e:
        st.error(f"Σφάλμα φόρτωσης: {e}")
        return pd.DataFrame()

df_main = load_main_data()

# --- ΕΠΙΚΕΦΑΛΙΔΑ ---
st.title("🏛️ Ψηφιακό Παράρτημα: Διακρατικές Ροές Πληροφορίας")
if not df_main.empty:
    # Εδώ θα εμφανιστεί το 55.000+ αν το φιλτράρισμα δουλέψει
    st.markdown(f"### Ανάλυση Τελικού Corpus: **{len(df_main):,}** Άρθρα (Directly Relevant)")
else:
    st.markdown("### Αναμονή για φόρτωση δεδομένων...")
st.divider()

# --- ΚΑΡΤΕΛΕΣ ---
tab_stats, tab_flows = st.tabs(["📊 Στατιστικά Διατριβής", "🌍 Top 100 Ροές Ειδήσεων (Origins)"])

# ==========================================
# ΚΑΡΤΕΛΑ 1: ΣΤΑΤΙΣΤΙΚΑ (55k+)
# ==========================================
with tab_stats:
    if not df_main.empty:
        col1, col2, col3 = st.columns(3)
        col1.metric("Τελικό Corpus (AI Filtered)", f"{len(df_main):,}")
        
        # Έλεγχος αν υπάρχουν οι στήλες για τα metrics
        col2.metric("Εφημερίδες", df_main['newspaper_title'].nunique() if 'newspaper_title' in df_main.columns else "N/A")
        col3.metric("Χώρες", df_main['country'].nunique() if 'country' in df_main.columns else "N/A")

        st.divider()
        
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("📅 Ένταση Αρθρογραφίας ανά Έτος")
            if 'date' in df_main.columns:
                df_main['year_val'] = df_main['date'].dt.year
                df_chart = df_main[(df_main['year_val'] >= 1821) & (df_main['year_val'] <= 1832)]
                fig_year = px.histogram(df_chart, x="year_val", color="country" if 'country' in df_main.columns else None, 
                                         barmode="group", color_discrete_map={'gb': '#1f77b4', 'fr': '#d62728'})
                st.plotly_chart(fig_year, use_container_width=True)
        
        with c2:
            st.subheader("⚖️ Πολιτική Στάση ανά Χώρα")
            if 'ai_stance' in df_main.columns and 'country' in df_main.columns:
                fig_sun = px.sunburst(df_main.dropna(subset=['ai_stance', 'country']), 
                                         path=['country', 'ai_stance'], color='country',
                                         color_discrete_map={'gb': '#1f77b4', 'fr': '#d62728'})
                st.plotly_chart(fig_sun, use_container_width=True)
    else:
        st.warning("Παρακαλώ ελέγξτε αν οι στήλες newspaper_title, date, κλπ υπάρχουν στο αρχείο.")

# ==========================================
# ΚΑΡΤΕΛΑ 2: TOP 100 INFO FLOWS
# ==========================================
with tab_flows:
    st.subheader("Χαρτογράφηση Ροής: Από την Πηγή (Origin) στο Κέντρο Έκδοσης")
    
    if not df_main.empty and 'news_origin' in df_main.columns and 'publication_place' in df_main.columns:
        flow_df = df_main.dropna(subset=['news_origin', 'publication_place'])
        flows = flow_df.groupby(['news_origin', 'publication_place']).size().reset_index(name='counts')
        top_100 = flows.sort_values(by='counts', ascending=False).head(100)
        
        all_nodes = list(pd.concat([top_100['news_origin'], top_100['publication_place']]).unique())
        node_map = {node: i for i, node in enumerate(all_nodes)}
        
        fig_sankey = go.Figure(data=[go.Sankey(
            node = dict(pad = 15, thickness = 20, label = all_nodes, color = "blue"),
            link = dict(source = top_100['news_origin'].map(node_map), 
                        target = top_100['publication_place'].map(node_map), 
                        value = top_100['counts'], color = "rgba(100, 100, 255, 0.4)")
        )])
        
        st.plotly_chart(fig_sankey, use_container_width=True)
    else:
        st.info("Δεν βρέθηκαν οι στήλες news_origin ή publication_place για την απεικόνιση των ροών.")
