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
        # Ψάχνουμε ΜΟΝΟ για το CSV (αγνοώντας φακέλους και κρυφά αρχεία του Mac)
        with zipfile.ZipFile("THESIS_WITH_ORIENTATION.csv.zip", 'r') as z:
            csv_files = [name for name in z.namelist() if not name.startswith('__MACOSX') and not name.startswith('._') and name.endswith('.csv')]
            
            if not csv_files:
                st.error("Δεν βρέθηκε κανένα αρχείο .csv μέσα στο ZIP!")
                return pd.DataFrame()
                
            real_file_name = csv_files[0]
            
            with z.open(real_file_name) as f:
                df = pd.read_csv(f, low_memory=False, encoding='utf-8', on_bad_lines='skip')
        
        # Καθαρισμός ονομάτων στηλών
        df.columns = df.columns.str.lower().str.strip()
        
        # Φιλτράρισμα 55k (ΜΟΝΟ αν υπάρχει η στήλη)
        if 'ai_relevance' in df.columns:
            df = df[df['ai_relevance'].astype(str).str.lower().str.strip() == 'directly_relevant'].copy()
        
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'], errors='coerce')
            
        return df
    except Exception as e:
        st.error(f"Σφάλμα φόρτωσης δεδομένων: {e}")
        return pd.DataFrame()

df_main = load_main_data()

# --- ΕΡΓΑΛΕΙΟ ΔΙΑΓΝΩΣΗΣ (DEBUG) ---
with st.expander("🛠️ Εργαλείο Διάγνωσης (Δες ποιες στήλες βρήκε)"):
    if not df_main.empty:
        st.write("Το αρχείο περιέχει τις εξής στήλες:", df_main.columns.tolist())
    else:
        st.write("Το αρχείο είναι άδειο ή δεν φορτώθηκε.")

# --- ΕΠΙΚΕΦΑΛΙΔΑ ---
st.title("🏛️ Ψηφιακό Παράρτημα: Διακρατικές Ροές Πληροφορίας")
if not df_main.empty:
    st.markdown(f"### Ανάλυση Corpus: **{len(df_main):,}** Άρθρα")
st.divider()

# --- ΚΑΡΤΕΛΕΣ ---
tab_stats, tab_flows = st.tabs(["📊 Στατιστικά Διατριβής", "🌍 Top 100 Ροές Ειδήσεων (Origins)"])

# ==========================================
# ΚΑΡΤΕΛΑ 1: ΣΤΑΤΙΣΤΙΚΑ 
# ==========================================
with tab_stats:
    if not df_main.empty:
        col1, col2, col3 = st.columns(3)
        col1.metric("Άρθρα στο Dashboard", f"{len(df_main):,}")
        
        # Safe Check για Εφημερίδες
        if 'newspaper_title' in df_main.columns:
            col2.metric("Εφημερίδες", df_main['newspaper_title'].nunique())
        else:
            col2.metric("Εφημερίδες", "Λείπει η στήλη")
            
        # Safe Check για Χώρες
        if 'country' in df_main.columns:
            col3.metric("Χώρες", df_main['country'].nunique())
        else:
            col3.metric("Χώρες", "Λείπει η στήλη")

        st.divider()
        
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("📅 Ένταση Αρθρογραφίας ανά Έτος")
            if 'date' in df_main.columns and 'country' in df_main.columns:
                df_main['year_val'] = df_main['date'].dt.year
                df_chart = df_main[(df_main['year_val'] >= 1821) & (df_main['year_val'] <= 1832)]
                fig_year = px.histogram(df_chart, x="year_val", color="country", barmode="group",
                                         color_discrete_map={'gb': '#1f77b4', 'fr': '#d62728', 'GB': '#1f77b4', 'FR': '#d62728'})
                st.plotly_chart(fig_year, use_container_width=True)
            else:
                st.info("Λείπουν οι στήλες 'date' ή 'country'.")
        
        with c2:
            st.subheader("⚖️ Πολιτική Στάση ανά Χώρα")
            if 'ai_stance' in df_main.columns and 'country' in df_main.columns:
                fig_sun = px.sunburst(df_main.dropna(subset=['ai_stance', 'country']), 
                                         path=['country', 'ai_stance'], 
                                         color='country',
                                         color_discrete_map={'gb': '#1f77b4', 'fr': '#d62728', 'GB': '#1f77b4', 'FR': '#d62728'})
                st.plotly_chart(fig_sun, use_container_width=True)
            else:
                st.info("Λείπει η στήλη 'ai_stance'.")
    else:
        st.warning("Τα δεδομένα δεν είναι διαθέσιμα.")

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
        
        source = top_100['news_origin'].map(node_map)
        target = top_100['publication_place'].map(node_map)
        value = top_100['counts']
        
        fig_sankey = go.Figure(data=[go.Sankey(
            node = dict(pad = 15, thickness = 20, line = dict(color = "black", width = 0.5), label = all_nodes, color = "blue"),
            link = dict(source = source, target = target, value = value, color = "rgba(100, 100, 255, 0.4)")
        )])
        
        fig_sankey.update_layout(height=700)
        st.plotly_chart(fig_sankey, use_container_width=True)
        st.dataframe(top_100, use_container_width=True)
    else:
        st.error("Δεν βρέθηκαν δεδομένα για τις στήλες 'news_origin' ή 'publication_place'.")
