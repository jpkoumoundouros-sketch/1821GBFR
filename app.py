import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import json

# --- ΡΥΘΜΙΣΕΙΣ ΣΕΛΙΔΑΣ ---
st.set_page_config(page_title="Thesis Dashboard - Greek Revolution", page_icon="📈", layout="wide")

# Εύρεση του φακέλου στον οποίο βρίσκεται το app.py
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# --- ΣΥΝΑΡΤΗΣΕΙΣ ΦΟΡΤΩΣΗΣ ΔΕΔΟΜΕΝΩΝ (ΜΕ BASE_DIR) ---
@st.cache_data
def load_main_data():
    try:
        file_path = os.path.join(BASE_DIR, "THESIS_WITH_ORIENTATION.csv")
        df = pd.read_csv(file_path, low_memory=False)
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        return df
    except Exception:
        return pd.DataFrame()

@st.cache_data
def load_network_data():
    try:
        file_path = os.path.join(BASE_DIR, "Palladio_Network_Data.csv")
        df = pd.read_csv(file_path)
        df[['Source_Lat', 'Source_Lon']] = df['Source_LatLon'].str.split(',', expand=True).astype(float)
        df[['Target_Lat', 'Target_Lon']] = df['Target_LatLon'].str.split(',', expand=True).astype(float)
        return df
    except:
        return pd.DataFrame()

@st.cache_data
def load_slim_data():
    try:
        file_path = os.path.join(BASE_DIR, "THESIS_SLIM_FOR_NOTEBOOKLM.csv")
        df = pd.read_csv(file_path)
        return df
    except:
        return pd.DataFrame()

@st.cache_data
def load_waves_data():
    try:
        file_path = os.path.join(BASE_DIR, "news_wave_streamlit_slim.csv")
        df = pd.read_csv(file_path, low_memory=False)
        return df
    except:
        return pd.DataFrame()

@st.cache_data
def load_waves_cards():
    try:
        file_path = os.path.join(BASE_DIR, "streamlit_news_wave_cards.json")
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return []

# Φόρτωση όλων των δεδομένων
df_main = load_main_data()
df_network = load_network_data()
df_slim = load_slim_data()
df_waves = load_waves_data()
wave_cards = load_waves_cards()

# --- ΕΠΙΚΕΦΑΛΙΔΑ ---
st.title("🏛️ Ψηφιακό Παράρτημα Διδακτορικής Διατριβής")
st.markdown("### Ανάλυση του Ευρωπαϊκού Τύπου κατά την Ελληνική Επανάσταση (1821-1829)")
st.divider()

# --- ΚΥΡΙΕΣ ΚΑΡΤΕΛΕΣ (TABS) ---
tab_stats, tab_network, tab_archive, tab_waves = st.tabs([
    "📊 Στατιστικά Διατριβής", 
    "🌍 Γεωχωρική Ανάλυση (Media Lag)", 
    "🔍 Ψηφιακό Αρχείο",
    "🌊 Κύματα Ειδήσεων (News Waves)"
])

# ==========================================
# ΚΑΡΤΕΛΑ 1: ΣΤΑΤΙΣΤΙΚΑ ΟΛΗΣ ΤΗΣ ΔΙΑΤΡΙΒΗΣ
# ==========================================
with tab_stats:
    if not df_main.empty:
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Συνολικά Άρθρα", len(df_main))
        m2.metric("Εφημερίδες", df_main['newspaper_title'].nunique() if 'newspaper_title' in df_main.columns else "N/A")
        m3.metric("Χώρες", df_main['country'].nunique() if 'country' in df_main.columns else "2")
        m4.metric("Directly Relevant", len(df_main[df_main['ai_relevance'] == 'directly_relevant']) if 'ai_relevance' in df_main.columns else "N/A")
        st.divider()
        
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("📅 Χρονική Κατανομή")
            df_main['year'] = df_main['date'].dt.year
            fig_year = px.histogram(df_main.dropna(subset=['year']), x="year", color="country" if 'country' in df_main.columns else None, barmode="group")
            st.plotly_chart(fig_year, use_container_width=True)
            
        with c2:
            st.subheader("🏛️ Μερίδιο ανά Χώρα")
            if 'country' in df_main.columns:
                fig_pie = px.pie(df_main, names='country', hole=0.4)
                st.plotly_chart(fig_pie, use_container_width=True)
        st.divider()
        
        c3, c4 = st.columns(2)
        with c3:
            st.subheader("⚖️ Πολιτική Στάση (Stance)")
            if 'ai_stance' in df_main.columns:
                stance_counts = df_main['ai_stance'].value_counts().reset_index()
                stance_counts.columns = ['ai_stance', 'count']
                stance_fig = px.bar(stance_counts, x='ai_stance', y='count', color='ai_stance')
                st.plotly_chart(stance_fig, use_container_width=True)
            else:
                st.info("Η στήλη ai_stance δεν βρέθηκε.")
                
        with c4:
            st.subheader("🏷️ Κυρίαρχη Θεματολογία (Topics)")
            if 'ai_topic' in df_main.columns:
                topic_fig = px.treemap(df_main.dropna(subset=['ai_topic']), path=['ai_topic'])
                st.plotly_chart(topic_fig, use_container_width=True)
            else:
                st.info("Η στήλη ai_topic δεν βρέθηκε.")
    else:
        st.error("❌ Το αρχείο THESIS_WITH_ORIENTATION.csv δεν βρέθηκε.")

# ==========================================
# ΚΑΡΤΕΛΑ 2: ΓΕΩΧΩΡΙΚΗ ΑΝΑΛΥΣΗ (Media Lag)
# ==========================================
with tab_network:
    st.header("Χαρτογράφηση Δικτύου & Media Lag")
    if not df_network.empty:
        col_m1, col_m2 = st.columns(2)
        avg_lon = df_network[df_network['Target_Label'] == 'London']['Media_Lag'].mean()
        avg_par = df_network[df_network['Target_Label'] == 'Paris']['Media_Lag'].mean()
        col_m1.metric("Media Lag Λονδίνο (Μ.Ο.)", f"{avg_lon:.1f} ημέρες", "+ Πιο αργό", delta_color="inverse")
        col_m2.metric("Media Lag Παρίσι (Μ.Ο.)", f"{avg_par:.1f} ημέρες", "- Ταχύτερο", delta_color="inverse")
        
        fig_map = go.Figure()
        for i in range(len(df_network)):
            fig_map.add_trace(go.Scattergeo(
                lon = [df_network['Source_Lon'][i], df_network['Target_Lon'][i]],
                lat = [df_network['Source_Lat'][i], df_network['Target_Lat'][i]],
                mode = 'lines',
                line = dict(width = 1.5, color = 'red' if df_network['Target_Label'][i] == 'Paris' else 'blue'),
                opacity = 0.5,
                hoverinfo = 'text',
                text = f"Από: {df_network['Source_Label'][i]} -> Προς: {df_network['Target_Label'][i]}<br>Καθυστέρηση: {df_network['Media_Lag'][i]} ημέρες"
            ))
        fig_map.update_layout(
            title_text='Διαδρομές Ειδήσεων (Κόκκινο: Παρίσι | Μπλε: Λονδίνο)', 
            showlegend=False, 
            geo=dict(scope='europe', showland=True, landcolor='rgb(243, 243, 243)'), 
            height=600
        )
        st.plotly_chart(fig_map, use_container_width=True)
    else:
        st.warning("⚠️ Το αρχείο Palladio_Network_Data.csv δεν βρέθηκε.")

# ==========================================
# ΚΑΡΤΕΛΑ 3: ΨΗΦΙΑΚΟ ΑΡΧΕΙΟ
# ==========================================
with tab_archive:
    st.header("Εξερεύνηση Ιστορικών Πηγών")
    if not df_slim.empty:
        search = st.text_input("🔍 Αναζήτηση λέξης-κλειδιού στο περιεχόμενο (π.χ. Κολοκοτρώνης, Missolonghi):")
        filtered = df_slim.copy()
        
        if search:
            filtered = filtered[filtered['content'].astype(str).str.contains(search, case=False, na=False)]
        
        st.write(f"Βρέθηκαν **{len(filtered)}** σχετικά άρθρα.")
        
        columns_to_show = ['newspaper_title', 'date', 'publication_place', 'news_origin']
        existing_cols = [c for c in columns_to_show if c in filtered.columns]
        st.dataframe(filtered[existing_cols], use_container_width=True)
        
        st.markdown("### 📖 Ανάγνωση Πλήρους Άρθρου")
        article_option = st.selectbox("Επίλεξε άρθρο για ανάγνωση:", filtered['newspaper_title'].astype(str) + " (" + filtered['date'].astype(str) + ")")
        
        if article_option and not filtered.empty:
            idx = filtered.index[filtered['newspaper_title'].astype(str) + " (" + filtered['date'].astype(str) + ")" == article_option].tolist()[0]
            st.info(filtered.loc[idx, 'content'])
    else:
        st.warning("⚠️ Το αρχείο THESIS_SLIM_FOR_NOTEBOOKLM.csv δεν βρέθηκε.")

# ==========================================
# ΚΑΡΤΕΛΑ 4: ΚΥΜΑΤΑ ΕΙΔΗΣΕΩΝ (NEWS WAVES) 
# ==========================================
with tab_waves:
    st.header("🌊 Ανάλυση Ειδησεογραφικών Κυμάτων")
    
    if df_waves.empty or not wave_cards:
        st.error("⚠️ Λείπουν τα αρχεία 'news_wave_streamlit_slim.csv' ή 'streamlit_news_wave_cards.json'.")
    else:
        # Δημιουργία λίστας με τα Canonical Labels από το JSON
        event_options = [card['canonical_event_label'] for card in wave_cards]
        selected_event = st.selectbox("Επιλογή Ιστορικού Γεγονότος / Κύματος:", event_options)
        
        # Εύρεση της επιλεγμένης κάρτας
        card_data = next((c for c in wave_cards if c['canonical_event_label'] == selected_event), None)
        
        if card_data:
            cluster_id = card_data.get('canonical_story_cluster_id', '')
            
            # --- NARRATIVE CARD UI ---
            st.info(f"**Σύνοψη (AI):** {card_data.get('dashboard_card_el', 'Δεν βρέθηκε σύνοψη')}")
            
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Όγκος Άρθρων", card_data.get('count', 0))
            c2.metric("Κυρίαρχο Πλαίσιο", card_data.get('dominant_frame', '-'))
            c3.metric("Τύπος Γεγονότος", card_data.get('dominant_event_type', '-'))
            c4.metric("Μέσο Μετάδοσης", card_data.get('dominant_transmission_medium', '-'))
            
            st.markdown(f"**Προφίλ Βεβαιότητας:** {card_data.get('certainty_profile', '-')}")
            st.markdown(f"**Προφίλ Μετάδοσης:** {card_data.get('transmission_profile', '-')}")
            st.divider()
            
            # --- ΦΙΛΤΡΑΡΙΣΜΑ ΓΡΑΦΗΜΑΤΩΝ ΓΙΑ ΤΟ ΕΠΙΛΕΓΜΕΝΟ CLUSTER ---
            df_w = df_waves[df_waves["canonical_story_cluster_id"] == cluster_id].copy()
            
            def simple_bar(dataframe, column, title, color):
                if column in dataframe.columns:
                    temp = dataframe[column].fillna("Unknown").astype(str).str.strip()
                    temp = temp.replace({"": "Unknown", "nan": "Unknown", "None": "Unknown"})
                    counts = temp.value_counts().head(10).reset_index()
                    counts.columns = ["Category", "Count"]
                    fig = px.bar(
                        counts, x="Count", y="Category", orientation="h",
                        color_discrete_sequence=[color], title=title
                    )
                    fig.update_layout(yaxis={'categoryorder': 'total ascending'}, height=350, margin=dict(t=50, b=20, l=10, r=10))
                    return fig
                return None

            col_w1, col_w2 = st.columns(2)
            with col_w1:
                fig_r = simple_bar(df_w, "rumor_status", "Κατάσταση Πληροφορίας", "#3498db")
                if fig_r: st.plotly_chart(fig_r, use_container_width=True)
            with col_w2:
                fig_m = simple_bar(df_w, "transmission_medium", "Μέσο Μετάδοσης", "#2ecc71")
                if fig_m: st.plotly_chart(fig_m, use_container_width=True)
                
            col_w3, col_w4 = st.columns(2)
            with col_w3:
                fig_f = simple_bar(df_w, "rhetorical_frame_primary", "Ρητορικό Πλαίσιο", "#9b59b6")
                if fig_f: st.plotly_chart(fig_f, use_container_width=True)
            with col_w4:
                fig_t = simple_bar(df_w, "canonical_event_type", "Τύπος Γεγονότος", "#e67e22")
                if fig_t: st.plotly_chart(fig_t, use_container_width=True)
                
            st.divider()
            st.markdown(f"### Δείγμα Εγγραφών ({selected_event})")
            show_cols = ["newspaper_title", "date", "country", "publication_place", "news_origin_norm", "rumor_status", "transmission_medium", "rhetorical_frame_primary", "canonical_event_type"]
            show_cols = [c for c in show_cols if c in df_w.columns]
            st.dataframe(df_w[show_cols].head(100), use_container_width=True, hide_index=True)
