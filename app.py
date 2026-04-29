import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import networkx as nx
import zipfile
import io
import re
import os

# --- ΡΥΘΜΙΣΕΙΣ ΣΕΛΙΔΑΣ ---
st.set_page_config(
    page_title="1821GBFR | Greek Revolution Press Corpus",
    page_icon="🏛️",
    layout="wide"
)

# ==========================================
# 🌍 ΛΕΞΙΚΟ ΠΟΛΥΓΛΩΣΣΙΚΟΥ UI (Internationalization)
# ==========================================
LANG_UI = {
    'EL': {
        'nav_title': "🏛️ 1821GBFR: Γαλλοβρετανικό Corpus Τύπου για την Ελληνική Επανάσταση, 1821–1832",
        'active_corpus': "Ενεργό Corpus",
        'filters_header': "🎛️ Φίλτρα",
        'filter_country': "Χώρες:",
        'filter_period': "Περίοδος:",
        'tab_overview': "📊 Επισκόπηση",
        'tab_press': "📰 Εκδοτικό Τοπίο",
        'tab_topics': "🧠 Θεματολογία",
        'tab_flows': "🌍 Ροές",
        'tab_entities': "👥 Οντότητες",
        'tab_waves': "🌊 Κύματα Ειδήσεων",
        'metric_articles': "Συνολικά Άρθρα",
        'metric_papers': "Μοναδικοί Τίτλοι Εφημερίδων",
        'ov_sub': "### 🔭 Επισκόπηση του Corpus",
        'ov_relevance': "Αξιολόγηση Σχετικότητας (AI)",
        'ov_country': "Κατανομή ανά Χώρα (Ενεργό)",
        'ov_top_topics': "Top 5 Κυρίαρχα Θέματα",
        'ov_timeline': "📈 Εξέλιξη Όγκου Δημοσιεύσεων (1821-1832)",
        'press_sub': "📰 Πολιτική Γραμμή των 15 κυριότερων Εφημερίδων",
        'topics_sub': "🧠 Εξέλιξη Κυρίαρχων Θεμάτων",
        'flows_sub': "🌍 Ροές Ειδήσεων και Δίκτυα (Βεβαιωμένες Ροές)",
        'ent_sub': "👥 Ανάλυση Οντοτήτων",
        'ent_top_p': "Top 20 Πρόσωπα",
        'ent_top_l': "Top 20 Τοποθεσίες",
        'waves_sub': "🌊 Ανάλυση Ειδησεογραφικών Κυμάτων",
        'waves_note': "Η ανάλυση βασίζεται σε AI-assisted annotation εγγραφών με τεκμηριωμένο news_origin_norm. Τα αποτελέσματα είναι πειραματικά και προορίζονται για διερευνητική χρήση.",
        'waves_select': "Επιλογή συνόλου:",
        'waves_records': "Εγγραφές",
        'waves_newspapers': "Εφημερίδες",
        'waves_origins': "Προελεύσεις Ειδήσεων",
        'waves_rumor': "Κατάσταση Πληροφορίας",
        'waves_medium': "Μέσο Μετάδοσης",
        'waves_frame': "Ρητορικό Πλαίσιο",
        'waves_type': "Τύπος Γεγονότος",
        'waves_phase': "Φάση Ειδησεογραφικού Κύματος",
        'waves_sample': "Δείγμα εγγραφών",
        'unknown': "Άγνωστο"
    },
    'EN': {
        'nav_title': "🏛️ 1821GBFR: Franco-British Press Corpus on the Greek Revolution, 1821–1832",
        'active_corpus': "Active Corpus",
        'filters_header': "🎛️ Filters",
        'filter_country': "Countries:",
        'filter_period': "Period:",
        'tab_overview': "📊 Overview",
        'tab_press': "📰 Publishing Landscape",
        'tab_topics': "🧠 Topics",
        'tab_flows': "🌍 Flows & Networks",
        'tab_entities': "👥 Entities",
        'tab_waves': "🌊 News Waves",
        'metric_articles': "Total Articles",
        'metric_papers': "Unique Newspaper Titles",
        'ov_sub': "### 🔭 Corpus Overview",
        'ov_relevance': "Relevance Assessment (AI)",
        'ov_country': "Distribution by Country (Active)",
        'ov_top_topics': "Top 5 Dominant Topics",
        'ov_timeline': "📈 Publication Volume Evolution (1821-1832)",
        'press_sub': "📰 Editorial Stance of Top 15 Newspapers",
        'topics_sub': "🧠 Dominant Topics Evolution",
        'flows_sub': "🌍 News Flows & Networks (Confirmed Origins)",
        'ent_sub': "👥 Entity Analysis",
        'ent_top_p': "Top 20 Persons",
        'ent_top_l': "Top 20 Locations",
        'waves_sub': "🌊 News-Wave Analysis",
        'waves_note': "This analysis is based on AI-assisted annotation of records with documented news_origin_norm. Results are experimental and intended for exploratory use.",
        'waves_select': "Select dataset:",
        'waves_records': "Records",
        'waves_newspapers': "Newspapers",
        'waves_origins': "News Origins",
        'waves_rumor': "Information Status",
        'waves_medium': "Transmission Medium",
        'waves_frame': "Rhetorical Frame",
        'waves_type': "Event Type",
        'waves_phase': "News-Wave Phase",
        'waves_sample': "Sample records",
        'unknown': "Unknown"
    },
    'FR': {
        'nav_title': "🏛️ 1821GBFR : Corpus franco-britannique de presse sur la Révolution grecque, 1821–1832",
        'active_corpus': "Corpus Actif",
        'filters_header': "🎛️ Filtres",
        'filter_country': "Pays:",
        'filter_period': "Période:",
        'tab_overview': "📊 Aperçu",
        'tab_press': "📰 Paysage éditorial",
        'tab_topics': "🧠 Thématiques",
        'tab_flows': "🌍 Flux & Réseaux",
        'tab_entities': "👥 Entités",
        'tab_waves': "🌊 Vagues d'information",
        'metric_articles': "Total des articles",
        'metric_papers': "Titres de journaux uniques",
        'ov_sub': "### 🔭 Aperçu du Corpus",
        'ov_relevance': "Évaluation de la pertinence (IA)",
        'ov_country': "Répartition par pays (Actif)",
        'ov_top_topics': "Top 5 des thèmes dominants",
        'ov_timeline': "📈 Évolution du volume des publications (1821-1832)",
        'press_sub': "📰 Ligne politique des 15 principaux journaux",
        'topics_sub': "🧠 Évolution des thèmes dominants",
        'flows_sub': "🌍 Flux d'informations et Réseaux",
        'ent_sub': "👥 Analyse des entités",
        'ent_top_p': "Top 20 Personnes",
        'ent_top_l': "Top 20 Lieux",
        'waves_sub': "🌊 Analyse des vagues d'information",
        'waves_note': "Cette analyse repose sur une annotation assistée par IA des entrées disposant d’un news_origin_norm documenté. Les résultats sont expérimentaux et destinés à un usage exploratoire.",
        'waves_select': "Choisir un ensemble:",
        'waves_records': "Entrées",
        'waves_newspapers': "Journaux",
        'waves_origins': "Origines de l'information",
        'waves_rumor': "Statut de l'information",
        'waves_medium': "Moyen de transmission",
        'waves_frame': "Cadre rhétorique",
        'waves_type': "Type d'événement",
        'waves_phase': "Phase de la vague d'information",
        'waves_sample': "Exemples d'entrées",
        'unknown': "Inconnu"
    }
}

# ==========================================
# 📚 NORMALIZATION DICTIONARIES (NER)
# ==========================================
PERSON_ALIASES = {
    'Ibrahim Pasha': ['ibrahim-pacha', 'ibrahim', 'ibrahim pacha', 'pacha of egypt', 'pacha', 'ibrahim pasha', 'ibrahim pascha', 'i-brahim pacha', 'ibrahian-pacha', 'ibrahim-packa'],
    'Ioannis Kapodistrias': ["count capo d'istria", "count capo d'istrias", "capo d'istria", "capo d'istrias", "comte capo-d'istria", "comte capo-d'istrias", 'president of greece', 'president', 'kapodistrias'],
    'Lord Cochrane': ['lord cochrane', 'cochrane', 'thomas cochrane', 'lords cochrane'],
    'Sultan Mahmud II': ['sultan', 'mahmoud', 'le sultan', 'grand-seigneur', 'mahmud', 'mahmud ii'],
    'Lord Byron': ['lord byron', 'byron'],
    'Andreas Miaoulis': ['miaulis', 'amiral miaulis', 'admiral miaulis', 'miaoulis'],
    'Theodoros Kolokotronis': ['colocotroni', 'kolokotronis', 'kolokotroni', 'colocotronis'],
    'Alexander / Demetrios Ypsilantis': ['ypsilanti', 'prince ypsilanti', 'démétrius ypsilanti', 'ypsilantis', 'démétrius-ipsilanty'],
    'General Richard Church': ['general church', 'général church', 'church', 'richard church'],
    'Jean-Gabriel Eynard': ['m. eynard', 'eynard'],
    'Reshid Pasha': ['reschid-pacha', 'reshid', 'kiutahi', 'teschid-pacha'],
    'Charles Fabvier': ['colonel fabvier', 'fabvier', 'général fabvier'],
    'Duke of Wellington': ['duke of wellington', 'wellington'],
    'George Canning': ['canning', 'mr. canning', 'm. canning'],
    'Georgios Karaiskakis': ['karaiskaki', 'karaiskakis', 'goaras'],
    'Alexandros Mavrokordatos': ['maurocordato', 'mavrocordato', 'prince mavrocordato', 'condurietti'],
    'Constantine Kanaris': ['canaris', 'kanaris']
}

LOC_ALIASES = {
    'Greece': ['greece', 'grèce', 'western greece', 'eastern greece', 'grecs', 'greeks', 'greek'],
    'Ottoman Empire': ['turkey', 'turquie', 'porte', 'ottoman empire'],
    'Peloponnese (Morea)': ['morée', 'morea', 'pélopόννησος', 'peloponnesus', 'peloponnese', 'moree'],
    'Russia': ['russia', 'russie'],
    'Great Britain': ['london', 'londres', 'england', 'angleterre', 'great britain'],
    'France': ['france', 'paris', 'marseille', 'marseilles', 'toulon'],
    'Missolonghi': ['missolonghi', 'mesolongi', 'missolongi'],
    'Navarino': ['navarin', 'navarino'],
    'Constantinople': ['constantinople', 'istanbul'],
    'Egypt': ['egypt', 'égypte', 'egypte', 'alexandrie', 'alexandria'],
    'Nafplion': ['napoli', 'napoli de romanie', 'napoli di romania', 'nafplion'],
    'Crete': ['candie', 'candia', 'crete'],
    'Smyrna': ['smyrne', 'smyrna', 'izmir'],
    'Athens': ['athens', 'athènes']
}

def normalize_entities(entity_str, alias_dict):
    if pd.isna(entity_str) or not isinstance(entity_str, str) or entity_str.strip() == "":
        return ""
    e_clean = re.sub(r'["\[\]]', '', entity_str)
    entities = [e.strip() for e in e_clean.split(',')]
    cleaned = []
    for e in entities:
        val = re.sub(r'\s+', ' ', e).strip()
        val_lower = val.lower().replace('’', "'").replace('`', "'")
        matched = False
        for main_name, aliases in alias_dict.items():
            if val_lower in aliases:
                cleaned.append(main_name)
                matched = True
                break
        if not matched and val != '':
            cleaned.append(val.title())
    return ", ".join(sorted(list(set(cleaned))))

# --- LOAD DATA FUNCTIONS ---
@st.cache_data
def load_thesis_data_v4():
    try:
        with zipfile.ZipFile("THESIS_RECLASSIFIED_FINAL.csv.zip", 'r') as z:
            csv_files = [name for name in z.namelist() if not name.startswith('__MACOSX') and name.endswith('.csv')]
            if not csv_files: return pd.DataFrame(), pd.Series()
            with z.open(csv_files[0]) as f:
                content = f.read().decode('utf-8', errors='replace')
                df = pd.read_csv(io.StringIO(content), sep=None, engine='python', on_bad_lines='skip')
        
        df.columns = df.columns.str.lower().str.strip()
        
        if 'newspaper_title' not in df.columns:
            possible_names = [c for c in df.columns if 'news' in c or 'title' in c or 'pub' in c]
            if possible_names: df = df.rename(columns={possible_names[0]: 'newspaper_title'})

        raw_relevance = df['ai_relevance'].value_counts() if 'ai_relevance' in df.columns else pd.Series()
        if 'ai_relevance' in df.columns:
            df = df[df['ai_relevance'].astype(str).str.lower().str.strip() == 'directly_relevant'].copy()

        for col in ['ai_stance', 'ai_topic']:
            if col in df.columns:
                df[col] = df[col].astype(str).fillna('Unknown').replace(['nan', 'unknown', 'None'], 'Unknown')

        if 'country' in df.columns:
            df['country'] = df['country'].astype(str).str.strip().str.upper().replace({'UK': 'GB', 'UNITED KINGDOM': 'GB', 'FRANCE': 'FR'})
            
        df['year_val'] = 0
        if 'year' in df.columns: df['year_val'] = pd.to_numeric(df['year'], errors='coerce').fillna(0)
        if 'date' in df.columns:
            mask = df['year_val'] == 0
            df.loc[mask, 'year_val'] = pd.to_numeric(df.loc[mask, 'date'].astype(str).str.extract(r'(18[23]\d)')[0], errors='coerce').fillna(0)
            
        df = df[(df['year_val'] >= 1821) & (df['year_val'] <= 1832)].copy()
        
        if 'entities_persons' in df.columns: df['entities_persons'] = df['entities_persons'].apply(lambda x: normalize_entities(x, PERSON_ALIASES))
        if 'entities_locations' in df.columns: df['entities_locations'] = df['entities_locations'].apply(lambda x: normalize_entities(x, LOC_ALIASES))
            
        return df, raw_relevance
    except Exception as e:
        st.error(f"Error loading main data: {e}")
        return pd.DataFrame(), pd.Series()

@st.cache_data
def load_news_wave_data():
    files = {
        "Chios 1822": "news_wave_chios_1822_v3.csv",
        "Missolonghi 1826": "news_wave_missolonghi_1826_v3.csv",
        "Navarino 1827": "news_wave_navarino_1827_v3.csv",
        "Random origin sample 2000": "news_wave_origin_random_2000_v3.csv",
    }
    frames = []
    missing_files = []

    for label, path in files.items():
        if os.path.exists(path):
            try:
                temp = pd.read_csv(path, encoding="utf-8-sig", on_bad_lines='skip', low_memory=False)
                temp["event_label"] = label
                frames.append(temp)
            except Exception as e:
                st.error(f"Σφάλμα ανάγνωσης στο {path}: {e}")
        else:
            missing_files.append(path)
    
    if missing_files:
        st.warning(f"Προσοχή: Τα παρακάτω αρχεία CSV δεν βρέθηκαν στον φάκελο:\n" + ", ".join(missing_files))
    
    if frames:
        df_waves = pd.concat(frames, ignore_index=True)
        df_waves.columns = df_waves.columns.str.strip()
        return df_waves
    return pd.DataFrame()

# Initial Data Load
df_main, raw_relevance = load_thesis_data_v4()

# --- SIDEBAR ---
if not df_main.empty:
    st.sidebar.header("🌐 Language / Γλώσσα")
    lang_choice = st.sidebar.selectbox("Select Language:", ["EL", "EN", "FR"])
    ui = LANG_UI[lang_choice]

    st.sidebar.divider()
    st.sidebar.header(ui['filters_header'])
    countries = sorted(df_main['country'].unique())
    sel_countries = st.sidebar.multiselect(ui['filter_country'], countries, default=countries)
    v_years = df_main['year_val']
    sel_years = st.sidebar.slider(ui['filter_period'], int(v_years.min()), int(v_years.max()), (int(v_years.min()), int(v_years.max())))
    df_filt = df_main[(df_main['country'].isin(sel_countries)) & (df_main['year_val'] >= sel_years[0]) & (df_main['year_val'] <= sel_years[1])]
else:
    st.stop()

# --- MAIN UI ---
st.title(ui['nav_title'])
st.markdown(f"**{ui['active_corpus']}:** {len(df_filt):,} {ui['metric_articles']}")
st.divider()

t1, t2, t3, t4, t5, t6 = st.tabs([
    ui['tab_overview'], 
    ui['tab_press'], 
    ui['tab_topics'], 
    ui['tab_flows'], 
    ui['tab_entities'], 
    ui['tab_waves']
])

# ==========================================
# ΚΑΡΤΕΛΑ 1: ΕΠΙΣΚΟΠΗΣΗ
# ==========================================
with t1:
    st.markdown(ui['ov_sub'])
    c_m1, c_m2 = st.columns(2)
    c_m1.metric(ui['metric_articles'], f"{len(df_filt):,}")
    num_papers = df_filt['newspaper_title'].nunique() if 'newspaper_title' in df_filt.columns else 0
    c_m2.metric(ui['metric_papers'], num_papers)
    
    st.divider()
    
    c_pie1, c_pie2, c_bar = st.columns(3)
    with c_pie1:
        st.markdown(f"**{ui['ov_relevance']}**")
        if not raw_relevance.empty:
            fig_p = px.pie(values=raw_relevance.values, names=raw_relevance.index, hole=0.4,
                           color_discrete_sequence=['#2ecc71', '#e74c3c', '#95a5a6'])
            fig_p.update_layout(showlegend=False, margin=dict(t=10, b=10, l=10, r=10), height=300)
            st.plotly_chart(fig_p, use_container_width=True)
            
    with c_pie2:
        st.markdown(f"**{ui['ov_country']}**")
        df_c = df_filt['country'].value_counts().reset_index()
        df_c.columns = ['Country', 'Count']
        fig_c = px.pie(df_c, values='Count', names='Country', hole=0.4,
                       color='Country', color_discrete_map={'GB': '#1f77b4', 'FR': '#d62728'})
        fig_c.update_layout(showlegend=False, margin=dict(t=10, b=10, l=10, r=10), height=300)
        st.plotly_chart(fig_c, use_container_width=True)

    with c_bar:
        st.markdown(f"**{ui['ov_top_topics']}**")
        if 'ai_topic' in df_filt.columns:
            valid_topics = df_filt[~df_filt['ai_topic'].str.lower().isin(['unknown', 'άγνωστο', 'inconnu'])]
            df_top = valid_topics['ai_topic'].value_counts().head(5).reset_index()
            df_top.columns = ['Topic', 'Count']
            fig_t = px.bar(df_top, x='Count', y='Topic', orientation='h', color_discrete_sequence=['#9b59b6'])
            fig_t.update_layout(yaxis={'categoryorder':'total ascending'}, margin=dict(t=10, b=10, l=10, r=10), height=300)
            st.plotly_chart(fig_t, use_container_width=True)
            
    st.divider()
    st.markdown(f"**{ui['ov_timeline']}**")
    df_v = df_filt.groupby(['year_val', 'country']).size().reset_index(name='count')
    fig_v = px.line(df_v, x='year_val', y='count', color='country', markers=True, 
                    color_discrete_map={'GB': '#1f77b4', 'FR': '#d62728'})
    fig_v.update_layout(height=400)
    st.plotly_chart(fig_v, use_container_width=True)

# ==========================================
# ΚΑΡΤΕΛΑ 2: ΕΚΔΟΤΙΚΟ ΤΟΠΙΟ
# ==========================================
with t2:
    st.subheader(ui['press_sub'])
    if 'newspaper_title' in df_filt.columns:
        df_temp = df_filt[df_filt['newspaper_title'].notna() & (df_filt['newspaper_title'] != '')]
        top_np = df_temp['newspaper_title'].value_counts().nlargest(15).index
        df_np = df_temp[df_temp['newspaper_title'].isin(top_np)].groupby(['newspaper_title', 'ai_stance']).size().reset_index(name='count')
        fig_np = px.bar(df_np, x='count', y='newspaper_title', color='ai_stance', orientation='h', height=600)
        st.plotly_chart(fig_np, use_container_width=True)

# ==========================================
# ΚΑΡΤΕΛΑ 3: ΘΕΜΑΤΟΛΟΓΙΑ
# ==========================================
with t3:
    st.subheader(ui['topics_sub'])
    if 'ai_topic' in df_filt.columns:
        valid_topics_time = df_filt[~df_filt['ai_topic'].str.lower().isin(['unknown', 'άγνωστο', 'inconnu'])]
        top_t = valid_topics_time['ai_topic'].value_counts().nlargest(10).index
        df_t = valid_topics_time[valid_topics_time['ai_topic'].isin(top_t)].groupby(['year_val', 'ai_topic']).size().reset_index(name='count')
        st.plotly_chart(px.area(df_t, x='year_val', y='count', color='ai_topic', height=500), use_container_width=True)

# ==========================================
# ΚΑΡΤΕΛΑ 4: ΡΟΕΣ & ΔΙΚΤΥΑ
# ==========================================
with t4:
    st.subheader(ui['flows_sub'])
    c_src = next((c for c in df_filt.columns if 'origin' in c), None)
    c_dst = next((c for c in df_filt.columns if 'pub' in c or 'place' in c), None)
    
    if c_src and c_dst:
        bad_words = ['unknown', 'nan', 'none', 'άγνωστο', 'άγνωστη', 'inconnu', '[]']
        f_df = df_filt.dropna(subset=[c_src, c_dst])
        f_df = f_df[(~f_df[c_src].astype(str).str.lower().isin(bad_words)) & (~f_df[c_dst].astype(str).str.lower().isin(bad_words))]
        
        if not f_df.empty:
            # 1. Sankey Diagram
            st.markdown("**1. Sankey Flow (Information Volume)**")
            f_grp = f_df.groupby([c_src, c_dst]).size().reset_index(name='c').sort_values('c', ascending=False).head(40)
            nds = list(pd.concat([f_grp[c_src], f_grp[c_dst]]).unique())
            mapping = {n: i for i, n in enumerate(nds)}
            fig_s = go.Figure(go.Sankey(node=dict(label=nds, pad=15, thickness=20), link=dict(source=f_grp[c_src].map(mapping), target=f_grp[c_dst].map(mapping), value=f_grp['c'])))
            fig_s.update_layout(height=500)
            st.plotly_chart(fig_s, use_container_width=True)

            st.divider()

            # 2. Network Graph (NetworkX)
            st.markdown("**2. Network Graph (Node Centrality)**")
            G = nx.Graph()
            weights = f_df.groupby([c_src, c_dst]).size().reset_index(name='weight')
            
            for _, row in weights.iterrows():
                G.add_edge(row[c_src], row[c_dst], weight=row['weight'])

            pos = nx.spring_layout(G, k=0.5, iterations=50)

            edge_x, edge_y = [], []
            for edge in G.edges():
                x0, y0 = pos[edge[0]]
                x1, y1 = pos[edge[1]]
                edge_x.extend([x0, x1, None])
                edge_y.extend([y0, y1, None])

            edge_trace = go.Scatter(
                x=edge_x, y=edge_y,
                line=dict(width=1, color='#888'),
                hoverinfo='none',
                mode='lines'
            )

            node_x, node_y, node_adjacencies, node_text = [], [], [], []
            for node in G.nodes():
                x, y = pos[node]
                node_x.append(x)
                node_y.append(y)

            for node, adjacencies in enumerate(G.adjacency()):
                node_adjacencies.append(len(adjacencies[1]))
                node_text.append(f'{adjacencies[0]} (# connections: {len(adjacencies[1])})')

            node_trace = go.Scatter(
                x=node_x, y=node_y,
                mode='markers+text',
                text=[node for node in G.nodes()],
                textposition="top center",
                hoverinfo='text',
                hovertext=node_text,
                marker=dict(
                    showscale=True,
                    colorscale='YlGnBu',
                    size=[10 + (a * 2) for a in node_adjacencies],
                    color=node_adjacencies,
                    colorbar=dict(
                        thickness=15, 
                        title=dict(text='Node Connections', side='right'), 
                        xanchor='left'
                    )
                )

            fig_net = go.Figure(data=[edge_trace, node_trace],
                         layout=go.Layout(
                            showlegend=False,
                            hovermode='closest',
                            margin=dict(b=20,l=5,r=5,t=40),
                            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                            height=600)
                        )
            st.plotly_chart(fig_net, use_container_width=True)

# ==========================================
# ΚΑΡΤΕΛΑ 5: ΟΝΤΟΤΗΤΕΣ
# ==========================================
with t5:
    st.subheader(ui['ent_sub'])
    col_a, col_b = st.columns(2)
    def make_ner_chart(col_name, color, title):
        if col_name in df_filt.columns:
            data = df_filt[col_name].str.split(',').explode().str.strip().replace('', pd.NA).dropna()
            if not data.empty:
                counts = data.value_counts().head(20).reset_index()
                counts.columns = ['Entity', 'Count']
                fig = px.bar(counts, x='Count', y='Entity', orientation='h', color_discrete_sequence=[color], height=700)
                fig.update_layout(title=title, yaxis={'categoryorder':'total ascending'})
                return fig
        return None
    chart_p = make_ner_chart('entities_persons', "#1f77b4", ui['ent_top_p'])
    chart_l = make_ner_chart('entities_locations', "#ff7f0e", ui['ent_top_l'])
    if chart_p: col_a.plotly_chart(chart_p, use_container_width=True)
    if chart_l: col_b.plotly_chart(chart_l, use_container_width=True)

# ==========================================
# ΚΑΡΤΕΛΑ 6: NEWS WAVES
# ==========================================
with t6:
    st.subheader(ui['waves_sub'])
    st.info(ui['waves_note'])

    df_waves = load_news_wave_data()

    if df_waves.empty:
        st.error("⚠️ No news-wave data could be loaded. Please check if the CSV files exist in the directory.")
    else:
        events = sorted(df_waves["event_label"].dropna().unique())
        selected_event = st.selectbox(ui['waves_select'], events)

        df_w = df_waves[df_waves["event_label"] == selected_event].copy()

        c1, c2, c3 = st.columns(3)
        c1.metric(ui['waves_records'], f"{len(df_w):,}")
        
        if "newspaper_title" in df_w.columns:
            c2.metric(ui['waves_newspapers'], df_w["newspaper_title"].nunique())
        else:
            c2.metric(ui['waves_newspapers'], "-")

        if "news_origin_norm" in df_w.columns:
            c3.metric(ui['waves_origins'], df_w["news_origin_norm"].nunique())
        else:
            c3.metric(ui['waves_origins'], "-")

        st.divider()

        def simple_bar(dataframe, column, title, color):
            if column in dataframe.columns:
                temp = dataframe[column].fillna("Unknown").astype(str).str.strip()
                temp = temp.replace({"": "Unknown", "nan": "Unknown", "None": "Unknown"})
                counts = temp.value_counts().head(15).reset_index()
                counts.columns = ["Category", "Count"]

                fig = px.bar(
                    counts,
                    x="Count",
                    y="Category",
                    orientation="h",
                    color_discrete_sequence=[color],
                    title=title
                )
                fig.update_layout(
                    yaxis={'categoryorder': 'total ascending'},
                    height=420,
                    margin=dict(t=50, b=20, l=10, r=10)
                )
                return fig
            return None

        col_w1, col_w2 = st.columns(2)

        with col_w1:
            fig_r = simple_bar(df_w, "rumor_status", ui['waves_rumor'], "#3498db")
            if fig_r: st.plotly_chart(fig_r, use_container_width=True)

        with col_w2:
            fig_m = simple_bar(df_w, "transmission_medium", ui['waves_medium'], "#2ecc71")
            if fig_m: st.plotly_chart(fig_m, use_container_width=True)

        col_w3, col_w4 = st.columns(2)

        with col_w3:
            fig_f = simple_bar(df_w, "rhetorical_frame_primary", ui['waves_frame'], "#9b59b6")
            if fig_f: st.plotly_chart(fig_f, use_container_width=True)

        with col_w4:
            fig_t = simple_bar(df_w, "canonical_event_type", ui['waves_type'], "#e67e22")
            if fig_t: st.plotly_chart(fig_t, use_container_width=True)

        st.divider()

        fig_p = simple_bar(df_w, "event_phase", ui['waves_phase'], "#34495e")
        if fig_p:
            st.plotly_chart(fig_p, use_container_width=True)

        st.divider()

        st.markdown(f"### {ui['waves_sample']}")

        show_cols = [
            "newspaper_title",
            "date",
            "publication_place",
            "news_origin_norm",
            "rumor_status",
            "certainty_score",
            "transmission_medium",
            "transmission_formula",
            "rhetorical_frame_primary",
            "canonical_event_type",
            "event_phase",
            "source_criticism_note",
            "needs_review"
        ]

        show_cols = [c for c in show_cols if c in df_w.columns]

        st.dataframe(
            df_w[show_cols].head(100),
            use_container_width=True,
            hide_index=True
        )
