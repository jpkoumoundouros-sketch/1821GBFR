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
        
        if 'ai_relevance' in df.columns:
            df = df[df['ai_relevance'].astype(str).str.lower().str.strip() == 'directly_relevant'].copy()
        
        if 'country' in df.columns:
            # Τα κάνουμε όλα ΚΕΦΑΛΑΙΑ και μετατρέπουμε το UK σε GB για ομοιομορφία
            df['country'] = df['country'].astype(str).str.strip().str.upper()
            df['country'] = df['country'].replace({'UK': 'GB', 'NAN': 'ΑΓΝΩΣΤΗ'})
            
        if 'ai_stance' in df.columns:
            df['ai_stance'] = df['ai_stance'].fillna('Άγνωστη Στάση').astype(str).replace('nan', 'Άγνωστη Στάση')

        if 'ai_topic' in df.columns:
            df['ai_topic'] = df['ai_topic'].fillna('Άγνωστο Θέμα').astype(str).replace('nan', 'Άγνωστο Θέμα')
        
        if 'date' in df.columns:
            # ΜΑΓΕΙΑ: Το dayfirst=True λέει στην Python να διαβάζει Ευρωπαϊκές ημερομηνίες!
            df['date'] = pd.to_datetime(df['date'], dayfirst=True, errors='coerce')
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

available_countries = sorted(df_main['country'].unique().tolist())
selected_countries = st.sidebar.multiselect("Επιλογή Χώρας:", available_countries, default=available_countries)

valid_years = df_main[df_main['year_val'] > 0]['year_val']
min_year = int(valid_years.min()) if not valid_years.empty else 1821
max_year = int(valid_years.max()) if not valid_years.empty else 1832
selected_years = st.sidebar.slider("Επιλογή Περιόδου (Έτη):", min_value=min_year, max_value=max_year, value=(min_year, max_year))

if 'ai_stance' in df_main.columns:
    available_stances = sorted(df_main['ai_stance'].unique().tolist())
    selected_stances = st.sidebar.multiselect("Πολιτική Στάση:", available_stances, default=available_stances)
else:
    selected_stances = []

# Εφαρμογή Φίλτρων
year_filter = (df_main['year_val'] >= selected_years[0]) & (df_main['year_val'] <= selected_years[1])
if selected_years[0] == min_year and selected_years[1] == max_year:
    year_filter = year_filter | (df_main['year_val'] == 0)

df_filtered = df_main[(df_main['country'].isin(selected_countries)) & year_filter]
if selected_stances:
    df_filtered = df_filtered[df_filtered['ai_stance'].isin(selected_stances)]

# --- ΚΟΥΜΠΙ ΕΞΑΓΩΓΗΣ (DOWNLOAD) ---
st.sidebar.divider()
st.sidebar.markdown("### 💾 Εξαγωγή Δεδομένων")
csv_export = df_filtered.to_csv(index=False, encoding='utf-8-sig')
st.sidebar.download_button("Λήψη Φιλτραρισμένων Δεδομένων (CSV)", data=csv_export, file_name="Filtered_Thesis_Data.csv", mime="text/csv")

# --- ΕΠΙΚΕΦΑΛΙΔΑ ---
st.title("🏛️ Ψηφιακό Παράρτημα: Διακρατικές Ροές Πληροφορίας")
st.markdown(f"### Ενεργό Corpus: **{len(df_filtered):,}** / {len(df_main):,} Άρθρα")
st.divider()

# --- ΚΑΡΤΕΛΕΣ ---
tab_overview, tab_deepdive, tab_flows, tab_entities, tab_archive = st.tabs([
    "📊 Επισκόπηση", 
    "🧠 Βάθος Ανάλυσης (Topics & Stance)", 
    "🌍 Δίκτυα (Flows)", 
    "👥 Οντότητες (NER)",
    "🔍 Ψηφιακό Αρχείο"
])

color_map = {'GB': '#1f77b4', 'FR': '#d62728', 'ΑΓΝΩΣΤΗ': '#7f7f7f'}

# ==========================================
# ΚΑΡΤΕΛΑ 1: ΕΠΙΣΚΟΠΗΣΗ (Overview)
# ==========================================
with tab_overview:
    col1, col2, col3 = st.columns(3)
    col1.metric("Άρθρα (Βάσει Φίλτρων)", f"{len(df_filtered):,}")
    col2.metric("Εφημερίδες", df_filtered['newspaper_title'].nunique() if 'newspaper_title' in df_filtered.columns else "N/A")
    col3.metric("Χώρες", df_filtered['country'].nunique() if 'country' in df_filtered.columns else "N/A")
    
    st.divider()
    
    # ΝΕΟ: Πανοραμικό Διάγραμμα Όγκου Δημοσιεύσεων
    st.subheader("📈 Διαχρονική Εξέλιξη Όγκου Δημοσιεύσεων")
    if not df_filtered.empty:
        df_vol = df_filtered[df_filtered['year_val'] > 0].groupby(['year_val', 'country']).size().reset_index(name='count')
        fig_vol = px.line(df_vol, x='year_val', y='count', color='country', markers=True, color_discrete_map=color_map)
        fig_vol.update_layout(xaxis_title="Έτος", yaxis_title="Αριθμός Άρθρων (Όγκος)", margin=dict(t=10, b=10))
        st.plotly_chart(fig_vol, use_container_width=True)
    
    st.divider()
    
    c1, c2 = st.columns([2, 1])
    with c1:
        st.subheader("⚖️ Εξέλιξη Πολιτικής Στάσης")
        if not df_filtered.empty and 'ai_stance' in df_filtered.columns:
            df_time = df_filtered[df_filtered['year_val'] > 0].groupby(['year_val', 'ai_stance']).size().reset_index(name='count')
            fig_timeline = px.line(df_time, x='year_val', y='count', color='ai_stance', markers=True, labels={'year_val': 'Έτος', 'count': 'Αριθμός Άρθρων'})
            st.plotly_chart(fig_timeline, use_container_width=True)
            
    with c2:
        st.subheader("📰 Top 15 Εφημερίδες")
        if 'newspaper_title' in df_filtered.columns and not df_filtered.empty:
            top_papers = df_filtered['newspaper_title'].value_counts().nlargest(15).reset_index()
            top_papers.columns = ['Εφημερίδα', 'Άρθρα']
            fig_papers = px.bar(top_papers, x='Άρθρα', y='Εφημερίδα', orientation='h', color='Άρθρα', color_continuous_scale='Reds')
            fig_papers.update_layout(yaxis={'categoryorder':'total ascending'})
            st.plotly_chart(fig_papers, use_container_width=True)

# ==========================================
# ΚΑΡΤΕΛΑ 2: ΒΑΘΟΣ ΑΝΑΛΥΣΗΣ (Deep Dive)
# ==========================================
with tab_deepdive:
    st.markdown("Ανάλυση Συσχετίσεων μεταξύ Θεματολογίας (Topic) και Πολιτικής Στάσης (Stance).")
    
    if not df_filtered.empty and 'ai_topic' in df_filtered.columns and 'ai_stance' in df_filtered.columns:
        c3, c4 = st.columns(2)
        with c3:
            st.subheader("🌊 Διαχρονική Εξέλιξη Θεματολογίας")
            df_topic_time = df_filtered[df_filtered['year_val'] > 0].groupby(['year_val', 'ai_topic']).size().reset_index(name='count')
            if not df_topic_time.empty:
                top_8_topics = df_filtered['ai_topic'].value_counts().nlargest(8).index
                df_topic_time = df_topic_time[df_topic_time['ai_topic'].isin(top_8_topics)]
                fig_area = px.area(df_topic_time, x='year_val', y='count', color='ai_topic', labels={'year_val': 'Έτος', 'count': 'Όγκος Άρθρων'})
                st.plotly_chart(fig_area, use_container_width=True)
            else:
                st.info("Δεν υπάρχουν αρκετά δεδομένα για το γράφημα εξέλιξης.")

        with c4:
            st.subheader("🌡️ Heatmap: Στάση vs Θεματολογία")
            top_15_topics = df_filtered['ai_topic'].value_counts().nlargest(15).index
            df_heat = df_filtered[df_filtered['ai_topic'].isin(top_15_topics)]
            if not df_heat.empty and len(df_heat['ai_topic'].unique()) > 0:
                fig_heat = px.density_heatmap(df_heat, x='ai_stance', y='ai_topic', color_continuous_scale="viridis")
                fig_heat.update_layout(xaxis_title="Πολιτική Στάση", yaxis_title="Θέμα")
                st.plotly_chart(fig_heat, use_container_width=True)
            else:
                st.info("Δεν επαρκούν τα δεδομένα βάσει των φίλτρων σου για τη δημιουργία Heatmap.")
    else:
        st.info("Δεν υπάρχουν δεδομένα για αυτή την ανάλυση.")

# ==========================================
# ΚΑΡΤΕΛΑ 3: ΔΙΚΤΥΑ ΡΟΩΝ (Flows)
# ==========================================
with tab_flows:
    st.subheader("Χαρτογράφηση Ροής: Πηγή (Origin) ➔ Κέντρο Έκδοσης")
    if not df_filtered.empty and 'news_origin' in df_filtered.columns and 'publication_place' in df_filtered.columns:
        flow_df = df_filtered.dropna(subset=['news_origin', 'publication_place'])
        flows = flow_df.groupby(['news_origin', 'publication_place']).size().reset_index(name='counts')
        top_100 = flows.sort_values(by='counts', ascending=False).head(100)
        
        if not top_100.empty:
            all_nodes = list(pd.concat([top_100['news_origin'], top_100['publication_place']]).unique())
            node_map = {node: i for i, node in enumerate(all_nodes)}
            
            fig_sankey = go.Figure(data=[go.Sankey(
                node = dict(pad = 15, thickness = 20, label = all_nodes, color = "#1f77b4"),
                link = dict(source = top_100['news_origin'].map(node_map), target = top_100['publication_place'].map(node_map), value = top_100['counts'], color = "rgba(100, 100, 255, 0.3)")
            )])
            fig_sankey.update_layout(height=650)
            st.plotly_chart(fig_sankey, use_container_width=True)

# ==========================================
# ΚΑΡΤΕΛΑ 4: ΟΝΤΟΤΗΤΕΣ (NER)
# ==========================================
with tab_entities:
    c5, c6 = st.columns(2)
    with c5:
        st.subheader("👤 Top 20 Πρόσωπα")
        if 'entities_persons' in df_filtered.columns and not df_filtered.empty:
            persons = df_filtered['entities_persons'].dropna().astype(str).str.split(',').explode().str.strip()
            persons = persons[(persons != '') & (~persons.str.lower().isin(['nan', 'none', 'unknown']))]
            if not persons.empty:
                top_pers = persons.value_counts().head(20).reset_index()
                top_pers.columns = ['Πρόσωπο', 'Αναφορές']
                fig_p = px.bar(top_pers, x='Αναφορές', y='Πρόσωπο', orientation='h', color='Αναφορές', color_continuous_scale='Teal')
                fig_p.update_layout(yaxis={'categoryorder':'total ascending'})
                st.plotly_chart(fig_p, use_container_width=True)
                
    with c6:
        st.subheader("📍 Top 20 Τοποθεσίες (Locations)")
        if 'entities_locations' in df_filtered.columns and not df_filtered.empty:
            locs = df_filtered['entities_locations'].dropna().astype(str).str.split(',').explode().str.strip()
            locs = locs[(locs != '') & (~locs.str.lower().isin(['nan', 'none', 'unknown']))]
            if not locs.empty:
                top_locs = locs.value_counts().head(20).reset_index()
                top_locs.columns = ['Τοποθεσία', 'Αναφορές']
                fig_l = px.bar(top_locs, x='Αναφορές', y='Τοποθεσία', orientation='h', color='Αναφορές', color_continuous_scale='Oranges')
                fig_l.update_layout(yaxis={'categoryorder':'total ascending'})
                st.plotly_chart(fig_l, use_container_width=True)

# ==========================================
# ΚΑΡΤΕΛΑ 5: ΨΗΦΙΑΚΟ ΑΡΧΕΙΟ 
# ==========================================
with tab_archive:
    st.subheader("🔍 Αναζήτηση Λέξεων-Κλειδιών στο Κείμενο")
    if 'content' in df_filtered.columns:
        search_query = st.text_input("Πληκτρολόγησε λέξη (π.χ. Missolonghi, treaty, massacre):")
        if search_query:
            results = df_filtered[df_filtered['content'].astype(str).str.contains(search_query, case=False, na=False)]
            st.write(f"**Βρέθηκαν {len(results)} άρθρα.**")
            if not results.empty:
                cols = ['newspaper_title', 'date', 'country', 'ai_topic', 'ai_stance']
                av_cols = [c for c in cols if c in results.columns]
                st.dataframe(results[av_cols].head(100), use_container_width=True)
                
                sel_art = st.selectbox("Επίλεξε άρθρο για ανάγνωση:", results['newspaper_title'].astype(str) + " (" + results['date'].astype(str) + ")")
                if sel_art:
                    idx = results['newspaper_title'].astype(str) + " (" + results['date'].astype(str) + ")" == sel_art
                    st.info(results[idx]['content'].values[0])
