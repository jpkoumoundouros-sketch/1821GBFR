import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import zipfile

# --- ΡΥΘΜΙΣΕΙΣ ΣΕΛΙΔΑΣ ---
st.set_page_config(page_title="Thesis Dashboard - 1821 Info Flows", page_icon="📈", layout="wide")

# --- ΣΥΝΑΡΤΗΣΕΙΣ ΦΟΡΤΩΣΗΣ ---
@st.cache_data
def load_main_data():
    try:
        with zipfile.ZipFile("THESIS_WITH_ORIENTATION.csv.zip", 'r') as z:
            real_file_name = [name for name in z.namelist() if not name.startswith('__MACOSX') and not name.startswith('._')][0]
            with z.open(real_file_name) as f:
                df = pd.read_csv(f, low_memory=False, encoding='utf-8', on_bad_lines='skip')
        
        df.columns = df.columns.str.lower().str.strip()
        # Φιλτράρισμα για το Τελικό Corpus (Directly Relevant)
        if 'ai_relevance' in df.columns:
            df = df[df['ai_relevance'].astype(str).str.lower().str.strip() == 'directly_relevant']
        
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'], errors='coerce')
        return df
    except Exception as e:
        st.error(f"Σφάλμα φόρτωσης: {e}")
        return pd.DataFrame()

df_main = load_main_data()

# --- ΕΠΙΚΕΦΑΛΙΔΑ ---
st.title("🏛️ Ψηφιακό Παράρτημα: Διακρατικές Ροές Πληροφορίας")
st.markdown(f"### Ανάλυση Τελικού Corpus: {len(df_main):,} Άρθρα (Directly Relevant)")
st.divider()

tab_stats, tab_flows = st.tabs(["📊 Στατιστικά Διατριβής", "🌍 Top 100 Ροές Ειδήσεων"])

# ==========================================
# ΚΑΡΤΕΛΑ 1: ΣΤΑΤΙΣΤΙΚΑ (55k+)
# ==========================================
with tab_stats:
    col1, col2, col3 = st.columns(3)
    col1.metric("Τελικό Corpus (AI Filtered)", f"{len(df_main):,}")
    col2.metric("Εφημερίδες", df_main['newspaper_title'].nunique())
    col3.metric("Χώρες", df_main['country'].nunique())

    st.divider()
    
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("📅 Ένταση Αρθρογραφίας (Relevant Only)")
        df_main['year'] = df_main['date'].dt.year
        fig_year = px.histogram(df_main.dropna(subset=['year']), x="year", color="country", barmode="group",
                                 color_discrete_map={'gb': 'blue', 'fr': 'red'})
        st.plotly_chart(fig_year, use_container_width=True)
    
    with c2:
        st.subheader("⚖️ Πολιτική Στάση ανά Χώρα")
        fig_stance = px.sunburst(df_main.dropna(subset=['ai_stance', 'country']), 
                                 path=['country', 'ai_stance'], color='country')
        st.plotly_chart(fig_stance, use_container_width=True)

# ==========================================
# ΚΑΡΤΕΛΑ 2: TOP 100 INFO FLOWS
# ==========================================
with tab_flows:
    st.subheader("Ανάλυση Προέλευσης Ειδήσεων (news_origin -> publication_place)")
    
    # Δημιουργία των Flows
    if 'news_origin' in df_main.columns and 'publication_place' in df_main.columns:
        # Μετράμε τις συχνότητες των ζευγαριών
        flows = df_main.groupby(['news_origin', 'publication_place']).size().reset_index(name='counts')
        # Παίρνουμε τις Top 100 ροές
        top_100_flows = flows.sort_values(by='counts', ascending=False).head(100)
        
        # Οπτικοποίηση με Sankey Diagram (προαιρετικά) ή Bar Chart
        fig_flow = px.bar(top_100_flows, x='news_origin', y='counts', color='publication_place',
                          title="Κυρίαρχες Πηγές Προέλευσης Ειδήσεων (Top 100 Διαδρομές)",
                          labels={'news_origin': 'Πόλη Προέλευσης (Origin)', 'counts': 'Πλήθος Άρθρων'})
        st.plotly_chart(fig_flow, use_container_width=True)
        
        # Πίνακας Δεδομένων
        st.write("### Λεπτομερή Στοιχεία Ροών")
        st.dataframe(top_100_flows, use_container_width=True)
    else:
        st.warning("Δεν βρέθηκαν οι στήλες news_origin ή publication_place.")        if col in df.columns:
            df[col] = df[col].astype(str).replace("nan", pd.NA).str.strip()

    if "year" not in df.columns and "date" in df.columns:
        df["year"] = df["date"].dt.year

    return df


@st.cache_data(show_spinner=False)
def load_network() -> pd.DataFrame:
    if not NETWORK_CSV.exists():
        return pd.DataFrame()

    try:
        net = pd.read_csv(NETWORK_CSV)
        net.columns = net.columns.str.lower().str.strip()
        if "source_latlon" in net.columns and "target_latlon" in net.columns:
            net[["source_lat", "source_lon"]] = net["source_latlon"].str.split(",", expand=True)
            net[["target_lat", "target_lon"]] = net["target_latlon"].str.split(",", expand=True)
            for col in ["source_lat", "source_lon", "target_lat", "target_lon"]:
                net[col] = pd.to_numeric(net[col], errors="coerce")
        return net
    except Exception as e:
        st.warning(f"Το network file δεν φορτώθηκε: {e}")
        return pd.DataFrame()


df = load_data()
df_network = load_network()

st.title("🏛️ Ψηφιακό Παράρτημα Διδακτορικής Διατριβής")
st.caption("Ευρωπαϊκός Τύπος και Ελληνική Επανάσταση, 1821–1832")

if df.empty:
    st.stop()

# Sidebar filters
st.sidebar.header("Φίλτρα")
years = sorted([int(y) for y in df["year"].dropna().unique()]) if "year" in df.columns else []
countries = sorted(df["country"].dropna().unique().tolist()) if "country" in df.columns else []
topics = sorted(df["ai_topic"].dropna().unique().tolist()) if "ai_topic" in df.columns else []
stances = sorted(df["ai_stance"].dropna().unique().tolist()) if "ai_stance" in df.columns else []
orientations = sorted(df["political_orientation"].dropna().unique().tolist()) if "political_orientation" in df.columns else []

selected_years = st.sidebar.multiselect("Έτος", years, default=years)
selected_countries = st.sidebar.multiselect("Χώρα", countries, default=countries)
selected_topics = st.sidebar.multiselect("Θέμα", topics, default=topics)
selected_stances = st.sidebar.multiselect("Στάση", stances, default=stances)
selected_orientations = st.sidebar.multiselect("Political orientation", orientations, default=orientations)

filtered = df.copy()
if selected_years and "year" in filtered.columns:
    filtered = filtered[filtered["year"].isin(selected_years)]
if selected_countries and "country" in filtered.columns:
    filtered = filtered[filtered["country"].isin(selected_countries)]
if selected_topics and "ai_topic" in filtered.columns:
    filtered = filtered[filtered["ai_topic"].isin(selected_topics)]
if selected_stances and "ai_stance" in filtered.columns:
    filtered = filtered[filtered["ai_stance"].isin(selected_stances)]
if selected_orientations and "political_orientation" in filtered.columns:
    filtered = filtered[filtered["political_orientation"].isin(selected_orientations)]

# Metrics
m1, m2, m3, m4 = st.columns(4)
m1.metric("Συνολικά άρθρα", f"{len(filtered):,}")
m2.metric("Τίτλοι εφημερίδων", f"{filtered['newspaper_title'].nunique():,}" if "newspaper_title" in filtered.columns else "—")
m3.metric("Χώρες", f"{filtered['country'].nunique():,}" if "country" in filtered.columns else "—")
m4.metric("Origins", f"{filtered['news_origin_norm'].dropna().nunique():,}" if "news_origin_norm" in filtered.columns else "—")

tab1, tab2, tab3, tab4 = st.tabs(["📊 Επισκόπηση", "🧭 Θεματική/Στάση", "📰 Explorer", "🌍 Network"])

with tab1:
    c1, c2 = st.columns(2)

    if "year" in filtered.columns:
        yearly = filtered.dropna(subset=["year"]).groupby(["year", "country"], dropna=False).size().reset_index(name="count")
        fig_year = px.bar(
            yearly,
            x="year",
            y="count",
            color="country" if "country" in yearly.columns else None,
            barmode="group",
            title="Αρθρογραφία ανά έτος"
        )
        c1.plotly_chart(fig_year, use_container_width=True)

    if "country" in filtered.columns:
        country_counts = filtered["country"].value_counts(dropna=False).reset_index()
        country_counts.columns = ["country", "count"]
        fig_country = px.pie(country_counts, names="country", values="count", title="Κατανομή ανά χώρα")
        c2.plotly_chart(fig_country, use_container_width=True)

with tab2:
    c1, c2 = st.columns(2)

    if "ai_topic" in filtered.columns:
        topic_counts = filtered["ai_topic"].dropna().value_counts().reset_index()
        topic_counts.columns = ["topic", "count"]
        fig_topic = px.bar(topic_counts, x="count", y="topic", orientation="h", title="Θεματικές κατηγορίες")
        c1.plotly_chart(fig_topic, use_container_width=True)

    if "ai_stance" in filtered.columns:
        stance_counts = filtered["ai_stance"].dropna().value_counts().reset_index()
        stance_counts.columns = ["stance", "count"]
        fig_stance = px.bar(stance_counts, x="stance", y="count", title="Κατανομή στάσης")
        c2.plotly_chart(fig_stance, use_container_width=True)

    if "political_orientation" in filtered.columns and "ai_stance" in filtered.columns:
        cross = (
            filtered.dropna(subset=["political_orientation", "ai_stance"])
            .groupby(["political_orientation", "ai_stance"])
            .size()
            .reset_index(name="count")
        )
        if not cross.empty:
            fig_cross = px.bar(
                cross,
                x="political_orientation",
                y="count",
                color="ai_stance",
                barmode="group",
                title="Political orientation × στάση"
            )
            st.plotly_chart(fig_cross, use_container_width=True)

with tab3:
    show_cols = [c for c in [
        "newspaper_title", "date", "country", "publication_place",
        "ai_topic", "ai_stance", "political_orientation", "news_origin_norm",
        "content", "summary_el", "source_url"
    ] if c in filtered.columns]

    st.dataframe(filtered[show_cols].head(200), use_container_width=True, height=500)

    if "content" in filtered.columns:
        choices = filtered.index.tolist()[:500]
        if choices:
            idx = st.selectbox("Διάλεξε εγγραφή για ανάγνωση", choices)
            row = filtered.loc[idx]
            st.markdown(f"**Εφημερίδα:** {row.get('newspaper_title', '—')}")
            st.markdown(f"**Ημερομηνία:** {row.get('date', '—')}")
            st.markdown(f"**Θέμα:** {row.get('ai_topic', '—')}  |  **Στάση:** {row.get('ai_stance', '—')}")
            st.markdown(f"**Political orientation:** {row.get('political_orientation', '—')}")
            st.markdown("**Απόσπασμα:**")
            st.write(row.get("content", "—"))
            if pd.notna(row.get("summary_el", None)):
                st.markdown("**Σύνοψη (EL):**")
                st.write(row.get("summary_el"))

with tab4:
    if df_network.empty:
        st.info("Δεν βρέθηκε `Palladio_Network_Data.csv`. Μπορούμε να ανεβάσουμε πρώτα το MVP χωρίς network view.")
    else:
        needed = {"source_lat", "source_lon", "target_lat", "target_lon"}
        if needed.issubset(df_network.columns):
            net = df_network.dropna(subset=list(needed)).copy()

            fig = px.line_geo(
                net,
                lat="source_lat",
                lon="source_lon",
                hover_name="source_label" if "source_label" in net.columns else None
            )
            # Simpler fallback note
            st.dataframe(net.head(100), use_container_width=True)
            st.caption("Για production network map προτείνεται ξεχωριστή βελτιστοποίηση του Palladio/network dataset.")
        else:
            st.warning("Το network file υπάρχει αλλά λείπουν οι απαραίτητες στήλες lat/lon.")

st.divider()
st.caption("MVP Streamlit dashboard για διερεύνηση corpus, χρονικών τάσεων, στάσης και πολιτικού προσανατολισμού.")
