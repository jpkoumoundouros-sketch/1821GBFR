import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# --- ΡΥΘΜΙΣΕΙΣ ΣΕΛΙΔΑΣ ---
st.set_page_config(page_title="Thesis Dashboard - Greek Revolution", page_icon="📈", layout="wide")

# --- ΣΥΝΑΡΤΗΣΕΙΣ ΦΟΡΤΩΣΗΣ ΔΕΔΟΜΕΝΩΝ ---
@st.cache_data
def load_main_data():
    try:
        # ΜΑΓΕΙΑ: Διαβάζει απευθείας το ZIP αρχείο!
        df = pd.read_csv("THESIS_WITH_ORIENTATION.csv.zip", low_memory=False, encoding='utf-8', on_bad_lines='skip')
        df.columns = df.columns.str.lower().str.strip()
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'], errors='coerce')
        return df
    except Exception as e:
        st.error(f"Σφάλμα φόρτωσης Δεδομένων Διατριβής: {e}")
        return pd.DataFrame()

@st.cache_data
def load_network_data():
    try:
        df = pd.read_csv("Palladio_Network_Data.csv")
        df.columns = df.columns.str.lower().str.strip() 
        if 'source_latlon' in df.columns:
            df[['source_lat', 'source_lon']] = df['source_latlon'].str.split(',', expand=True).astype(float)
            df[['target_lat', 'target_lon']] = df['target_latlon'].str.split(',', expand=True).astype(float)
        return df
    except Exception as e:
        st.error(f"Σφάλμα φόρτωσης Palladio: {e}")
        return pd.DataFrame()

df_main = load_main_data()
df_network = load_network_data()

# --- ΕΠΙΚΕΦΑΛΙΔΑ ---
st.title("🏛️ Ψηφιακό Παράρτημα Διδακτορικής Διατριβής")
st.markdown("### Ανάλυση του Ευρωπαϊκού Τύπου κατά την Ελληνική Επανάσταση (1821-1829)")
st.divider()

tab_stats, tab_network = st.tabs(["📊 Στατιστικά Διατριβής", "🌍 Γεωχωρική Ανάλυση (Media Lag)"])

# ==========================================
# ΚΑΡΤΕΛΑ 1: ΣΤΑΤΙΣΤΙΚΑ ΟΛΗΣ ΤΗΣ ΔΙΑΤΡΙΒΗΣ
# ==========================================
with tab_stats:
    if not df_main.empty:
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Συνολικά Άρθρα", len(df_main))
        m2.metric("Εφημερίδες", df_main['newspaper_title'].nunique() if 'newspaper_title' in df_main.columns else "N/A")
        m3.metric("Χώρες", df_main['country'].nunique() if 'country' in df_main.columns else "N/A")
        m4.metric("Απευθείας Σχετικά (Relevant)", len(df_main[df_main['ai_relevance'] == 'directly_relevant']) if 'ai_relevance' in df_main.columns else "N/A")
        
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("📅 Χρονική Κατανομή")
            if 'date' in df_main.columns:
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
            st.subheader("⚖️ Πολιτική Στάση (AI Stance)")
            if 'ai_stance' in df_main.columns:
                fig_stance = px.bar(df_main['ai_stance'].value_counts().reset_index(), x='ai_stance', y='count', color='ai_stance')
                st.plotly_chart(fig_stance, use_container_width=True)
        
        with c4:
            st.subheader("🏷️ Θεματολογία (AI Topics)")
            if 'ai_topic' in df_main.columns:
                df_topics = df_main.dropna(subset=['ai_topic'])
                if not df_topics.empty:
                    fig_topic = px.treemap(df_topics, path=['ai_topic'], color='ai_topic')
                    st.plotly_chart(fig_topic, use_container_width=True)
    else:
        st.warning("Τα δεδομένα δεν φορτώθηκαν σωστά.")

# ==========================================
# ΚΑΡΤΕΛΑ 2: ΓΕΩΧΩΡΙΚΗ ΑΝΑΛΥΣΗ
# ==========================================
with tab_network:
    if not df_network.empty and 'target_label' in df_network.columns:
        st.header("Χαρτογράφηση Δικτύου & Media Lag")
        
        avg_lon = df_network[df_network['target_label'].str.contains('London', case=False, na=False)]['media_lag'].mean()
        avg_par = df_network[df_network['target_label'].str.contains('Paris', case=False, na=False)]['media_lag'].mean()
        
        col_l, col_p = st.columns(2)
        col_l.metric("Μέσος Χρόνος Λονδίνο", f"{avg_lon:.1f} ημέρες" if pd.notnull(avg_lon) else "N/A")
        col_p.metric("Μέσος Χρόνος Παρίσι", f"{avg_par:.1f} ημέρες" if pd.notnull(avg_par) else "N/A")

        fig_map = go.Figure()
        for i in range(len(df_network)):
            fig_map.add_trace(go.Scattergeo(
                lon = [df_network['source_lon'][i], df_network['target_lon'][i]],
                lat = [df_network['source_lat'][i], df_network['target_lat'][i]],
                mode = 'lines',
                line = dict(width = 1.5, color = 'red' if 'Paris' in str(df_network['target_label'][i]) else 'blue'),
                opacity = 0.4
            ))
        fig_map.update_layout(geo=dict(scope='europe', showland=True, landcolor="lightgray"), height=600)
        st.plotly_chart(fig_map, use_container_width=True)
    else:
        st.warning("⚠️ Πρόβλημα με τα δεδομένα του χάρτη (Palladio).")