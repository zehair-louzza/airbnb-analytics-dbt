"""
Airbnb Analytics Dashboard - Berlin
Pipeline : DuckDB + dbt + Streamlit
Auteur : Zehair LOUZZA - MBA ESG Big Data & AI 2026
"""
import streamlit as st
import duckdb
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

# ============================================================
# CONFIGURATION
# ============================================================
st.set_page_config(
    page_title="Airbnb Analytics - Berlin",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded",
)

DB_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "data",
    "airbnb.duckdb",
)

# Palette chaleureuse (terracotta / safran / creme)
COLOR_PRIMARY = "#E85D3C"      # Terracotta
COLOR_ACCENT = "#F4A93B"       # Safran / miel
COLOR_SECONDARY = "#A0522D"    # Brun chaud
COLOR_BG = "#FBF5EC"           # Creme / parchemin
COLOR_SURFACE = "#FFFFFF"      # Cartes blanches
COLOR_SURFACE_ALT = "#FFF3E4"  # Surface alternative cremeuse
COLOR_TEXT = "#2B1810"         # Brun fonce
COLOR_MUTED = "#7A6354"        # Taupe chaud
COLOR_BORDER = "rgba(139, 69, 19, 0.12)"
PLOTLY_TEMPLATE = "plotly_white"
# Palette Plotly chaude pour les categories
WARM_PALETTE = ["#E85D3C", "#F4A93B", "#A0522D", "#D4A373", "#8B4513"]

# ============================================================
# CSS GLOBAL
# ============================================================
GLOBAL_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,700;12..96,800&family=DM+Sans:wght@400;500;600&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif !important;
    color: #2B1810;
}
.stApp {
    background: linear-gradient(180deg, #FBF5EC 0%, #FCEFE0 100%);
}
h1, h2, h3, h4 {
    font-family: 'Bricolage Grotesque', sans-serif !important;
    letter-spacing: -0.02em;
    color: #2B1810 !important;
}
section[data-testid="stSidebar"] {
    background: #FFF3E4 !important;
    border-right: 1px solid rgba(139, 69, 19, 0.12);
}
section[data-testid="stSidebar"] * {
    color: #2B1810 !important;
}
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 {
    color: #E85D3C !important;
}
section[data-testid="stSidebar"] label {
    color: #7A6354 !important;
    font-weight: 600;
}
.stTabs [data-baseweb="tab-list"] {
    gap: 10px;
    background: transparent;
    margin-top: 1.5rem;
    border-bottom: none !important;
}
.stTabs [data-baseweb="tab"] {
    background: #FFFFFF;
    color: #7A6354;
    border-radius: 12px;
    padding: 10px 22px;
    border: 1px solid rgba(139, 69, 19, 0.12);
    font-family: 'DM Sans', sans-serif;
    font-weight: 600;
    transition: all .25s ease;
}
.stTabs [data-baseweb="tab"]:hover {
    background: #FFF3E4;
    color: #E85D3C;
    border-color: rgba(232, 93, 60, 0.3);
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #E85D3C 0%, #F4A93B 100%) !important;
    color: #FFFFFF !important;
    border-color: transparent !important;
    box-shadow: 0 4px 12px rgba(232, 93, 60, 0.25);
}
.stTabs [aria-selected="true"] * { color: #FFFFFF !important; }
[data-testid="stMetric"] {
    background: #FFFFFF;
    border: 1px solid rgba(139, 69, 19, 0.10);
    border-radius: 16px;
    padding: 20px;
    transition: transform .25s ease, box-shadow .25s ease, border-color .25s ease;
    box-shadow: 0 2px 6px rgba(139, 69, 19, 0.04);
}
[data-testid="stMetric"]:hover {
    transform: translateY(-4px);
    border-color: rgba(232, 93, 60, 0.35);
    box-shadow: 0 12px 24px rgba(232, 93, 60, 0.12);
}
[data-testid="stMetricLabel"] {
    color: #7A6354 !important;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    font-size: 0.78rem !important;
    font-weight: 600;
}
[data-testid="stMetricValue"] {
    font-family: 'Bricolage Grotesque', sans-serif !important;
    color: #2B1810 !important;
    font-size: 1.9rem !important;
    font-weight: 800 !important;
}
[data-testid="stMetricValue"] > div {
    color: #E85D3C !important;
}
.block-container {
    padding-top: 4rem;
    padding-bottom: 3rem;
    max-width: 1400px;
}
hr {
    border-color: rgba(139, 69, 19, 0.12);
}
.stButton > button {
    background: linear-gradient(135deg, #E85D3C 0%, #F4A93B 100%);
    color: white;
    border: none;
    border-radius: 999px;
    padding: 0.65rem 1.5rem;
    font-family: 'DM Sans', sans-serif;
    font-weight: 600;
    letter-spacing: 0.02em;
    transition: all 0.25s ease;
    box-shadow: 0 4px 12px rgba(232, 93, 60, 0.25);
}
.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 20px rgba(232, 93, 60, 0.35);
    color: white;
}
/* DataFrame styling */
[data-testid="stDataFrame"] {
    background: #FFFFFF;
    border: 1px solid rgba(139, 69, 19, 0.10);
    border-radius: 12px;
    overflow: hidden;
}
/* Markdown text general */
.stMarkdown, .stMarkdown p, .stMarkdown li {
    color: #2B1810;
}
.stMarkdown strong { color: #2B1810; }
/* Slider thumb */
[data-testid="stSlider"] [role="slider"] {
    background: #E85D3C !important;
    border-color: #E85D3C !important;
}
/* Multi-select tags */
[data-baseweb="tag"] {
    background: #E85D3C !important;
    color: white !important;
}
</style>
"""

HERO_HTML = """
<div class="e1-hero-container" data-testid="landing-hero">
  <div class="e1-hero-badge">Berlin Analytics Engine</div>
  <h1 class="e1-hero-title">Décoder Berlin via<br><span>les annonces Airbnb.</span></h1>
  <p class="e1-hero-subtitle">Une plateforme analytique haute performance qui transforme 17 499 logements et 409 695 avis en insights actionnables : prix, tendances, sentiment et un focus original sur l'effet pleine lune.</p>
  <div class="e1-tech-stack">
    <span class="e1-tech-badge">DuckDB</span>
    <span class="e1-tech-badge">dbt</span>
    <span class="e1-tech-badge">Streamlit</span>
    <span class="e1-tech-badge">Plotly</span>
    <span class="e1-tech-badge">Python</span>
  </div>
  <div class="e1-hero-author">Réalisé par <strong>Zehair LOUZZA</strong> &bull; MBA ESG Big Data & IA — Promotion 2026</div>
</div>
<style>
.e1-hero-container {
    position: relative;
    width: 100%;
    min-height: 55vh;
    border-radius: 24px;
    overflow: hidden;
    display: flex;
    flex-direction: column;
    justify-content: center;
    padding: 4rem;
    background:
      linear-gradient(135deg, rgba(232, 93, 60, 0.92) 0%, rgba(244, 169, 59, 0.85) 50%, rgba(160, 82, 45, 0.78) 100%),
      url('https://images.unsplash.com/photo-1560930950-5cc20e80e392?crop=entropy&cs=srgb&fm=jpg') center/cover;
    font-family: 'DM Sans', sans-serif;
    color: #FFFFFF;
    box-shadow: 0 20px 50px rgba(232, 93, 60, 0.25);
    border: 1px solid rgba(255, 255, 255, 0.2);
    margin-bottom: 2.5rem;
    animation: heroFadeIn .9s ease-out;
}
@keyframes heroFadeIn {
    from { opacity: 0; transform: translateY(20px); }
    to   { opacity: 1; transform: translateY(0); }
}
.e1-hero-badge {
    display: inline-block;
    background: rgba(255, 255, 255, 0.18);
    backdrop-filter: blur(8px);
    border: 1px solid rgba(255, 255, 255, 0.4);
    color: #FFFFFF;
    padding: 0.5rem 1rem;
    border-radius: 999px;
    font-weight: 700;
    font-size: 0.8rem;
    margin-bottom: 1.5rem;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    width: fit-content;
}
.e1-hero-title {
    font-family: 'Bricolage Grotesque', sans-serif;
    font-size: clamp(2.5rem, 5vw, 4.5rem);
    font-weight: 800;
    line-height: 1.05;
    margin: 0 0 1.5rem 0;
    letter-spacing: -0.03em;
    color: #FFFFFF;
    text-shadow: 0 2px 24px rgba(43, 24, 16, 0.25);
}
.e1-hero-title span {
    color: #FFF3E4;
    font-style: italic;
}
.e1-hero-subtitle {
    font-size: 1.1rem;
    color: #FFF3E4;
    max-width: 640px;
    line-height: 1.6;
    margin: 0 0 2rem 0;
}
.e1-hero-author {
    font-size: 0.85rem;
    color: rgba(255, 255, 255, 0.85);
    border-top: 1px solid rgba(255, 255, 255, 0.25);
    padding-top: 1.2rem;
    margin-top: 2rem;
}
.e1-hero-author strong { color: #FFFFFF; }
.e1-tech-stack {
    display: flex;
    gap: 0.6rem;
    margin-bottom: 1rem;
    flex-wrap: wrap;
}
.e1-tech-badge {
    background: rgba(255, 255, 255, 0.18);
    backdrop-filter: blur(8px);
    border: 1px solid rgba(255, 255, 255, 0.3);
    padding: 0.35rem 0.9rem;
    border-radius: 8px;
    font-size: 0.78rem;
    color: #FFFFFF;
    font-weight: 600;
    transition: all .25s ease;
}
.e1-tech-badge:hover {
    background: rgba(255, 255, 255, 0.3);
    border-color: rgba(255, 255, 255, 0.6);
    transform: translateY(-2px);
}
</style>
"""

PIPELINE_HTML = """
<div class="e1-pipeline-wrapper" data-testid="pipeline-diagram">
  <div class="e1-pipeline-header">Architecture Medallion — Bronze → Silver → Gold</div>
  <div class="e1-pipeline-container">
    <div class="e1-pipeline-node" data-tier="bronze">
      <div class="e1-pipeline-title" style="color: #B8702E">Bronze</div>
      <div class="e1-pipeline-desc">Ingestion brute<br>raw_listings, raw_hosts,<br>raw_reviews</div>
    </div>
    <div class="e1-pipeline-arrow"></div>
    <div class="e1-pipeline-node" data-tier="silver">
      <div class="e1-pipeline-title" style="color: #A0522D">Silver</div>
      <div class="e1-pipeline-desc">Nettoyage & typage<br>prix, dates,<br>sentiment</div>
    </div>
    <div class="e1-pipeline-arrow"></div>
    <div class="e1-pipeline-node" data-tier="gold">
      <div class="e1-pipeline-title" style="color: #D4922A">Gold</div>
      <div class="e1-pipeline-desc">Agrégations métier<br>dim_listings, fact_reviews,<br>full_moon_reviews</div>
    </div>
  </div>
</div>
<style>
.e1-pipeline-wrapper {
    background: linear-gradient(135deg, #FFF8EE 0%, #FFEFD9 100%);
    padding: 2.5rem;
    border-radius: 20px;
    border: 1px solid rgba(139, 69, 19, 0.12);
    margin: 1.5rem 0 2rem 0;
    box-shadow: 0 4px 16px rgba(139, 69, 19, 0.06);
}
.e1-pipeline-header {
    font-family: 'Bricolage Grotesque', sans-serif;
    color: #2B1810;
    font-size: 1.4rem;
    font-weight: 700;
    margin-bottom: 2rem;
    text-align: center;
    letter-spacing: -0.01em;
}
.e1-pipeline-container {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 1rem;
    overflow-x: auto;
    padding-bottom: .5rem;
}
.e1-pipeline-node {
    background: #FFFFFF;
    border: 1px solid rgba(139, 69, 19, 0.10);
    border-radius: 14px;
    padding: 1.5rem;
    min-width: 200px;
    text-align: center;
    position: relative;
    z-index: 2;
    transition: transform .3s ease, box-shadow .3s ease;
    box-shadow: 0 2px 8px rgba(139, 69, 19, 0.05);
}
.e1-pipeline-node:hover {
    transform: translateY(-5px);
    box-shadow: 0 12px 28px rgba(232, 93, 60, 0.15);
}
.e1-pipeline-node[data-tier="bronze"] { border-top: 4px solid #B8702E; }
.e1-pipeline-node[data-tier="silver"] { border-top: 4px solid #A0522D; }
.e1-pipeline-node[data-tier="gold"]   { border-top: 4px solid #D4922A; }
.e1-pipeline-title {
    font-family: 'Bricolage Grotesque', sans-serif;
    font-size: 1.3rem;
    font-weight: 800;
    margin-bottom: 0.6rem;
    text-transform: uppercase;
    letter-spacing: 0.06em;
}
.e1-pipeline-desc {
    font-family: 'DM Sans', sans-serif;
    font-size: 0.85rem;
    color: #7A6354;
    line-height: 1.5;
}
.e1-pipeline-arrow {
    height: 2px;
    flex-grow: 1;
    background: linear-gradient(90deg, rgba(139, 69, 19, 0.1) 0%, rgba(232, 93, 60, 0.7) 50%, rgba(139, 69, 19, 0.1) 100%);
    position: relative;
    min-width: 40px;
}
.e1-pipeline-arrow::after {
    content: '';
    position: absolute;
    right: -2px;
    top: 50%;
    transform: translateY(-50%) rotate(-45deg);
    border: solid #E85D3C;
    border-width: 0 2px 2px 0;
    display: inline-block;
    padding: 5px;
}
@media (max-width: 800px) {
    .e1-pipeline-container { flex-direction: column; }
    .e1-pipeline-arrow { width: 2px; height: 30px; min-width: 2px; transform: rotate(0); }
    .e1-pipeline-arrow::after { right: 50%; transform: translate(50%, -50%) rotate(45deg); top: 100%; }
}
</style>
"""

# ============================================================
# DATA LOADING
# ============================================================
@st.cache_resource
def get_con():
    return duckdb.connect(DB_PATH, read_only=True)

@st.cache_data(ttl=300)
def q(sql: str) -> pd.DataFrame:
    return get_con().execute(sql).df()

if not os.path.exists(DB_PATH):
    st.error(
        f"Base DuckDB introuvable ({DB_PATH}).\n\n"
        "Lance d'abord :\n"
        "1. `python scripts/load_data.py --data-dir ./data/raw`\n"
        "2. `dbt seed && dbt run`"
    )
    st.stop()

df_listings = q("SELECT * FROM main_gold.dim_listings")
df_hosts = q("SELECT * FROM main_gold.dim_hosts")
df_reviews = q("SELECT * FROM main_gold.fact_reviews")
df_moon = q("SELECT * FROM main_gold.full_moon_reviews")

# Injection CSS global
st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

# ============================================================
# SIDEBAR - FILTRES
# ============================================================
st.sidebar.markdown("### Filtres")
st.sidebar.markdown("---")

room_types = sorted(df_listings["room_type"].dropna().unique().tolist())
selected_rt = st.sidebar.multiselect(
    "Type de logement", options=room_types, default=[]
)

price_min = float(df_listings["price"].min())
price_max = float(min(df_listings["price"].max(), 1000.0))  # cap visuel a 1000
selected_price = st.sidebar.slider(
    "Prix (EUR / nuit)",
    min_value=price_min,
    max_value=price_max,
    value=(price_min, price_max),
    step=5.0,
)

full_moon_only = st.sidebar.checkbox("Pleine lune uniquement", value=False)

st.sidebar.markdown("---")
st.sidebar.markdown(
    "<div style='color:#7A6354;font-size:0.78rem;line-height:1.5;'>"
    "<strong style='color:#E85D3C'>Auteur</strong><br>"
    "Zehair LOUZZA<br>"
    "MBA ESG Big Data & IA<br>"
    "Promotion 2026"
    "</div>",
    unsafe_allow_html=True,
)

# Application des filtres
df_f = df_listings.copy()
df_f = df_f[(df_f["price"] >= selected_price[0]) & (df_f["price"] <= selected_price[1])]
if selected_rt:
    df_f = df_f[df_f["room_type"].isin(selected_rt)]

df_rev_f = df_reviews.copy()
if selected_rt:
    df_rev_f = df_rev_f[df_rev_f["room_type"].isin(selected_rt)]
df_rev_f = df_rev_f[
    df_rev_f["listing_id"].isin(df_f["listing_id"])
]

df_moon_f = df_moon.copy()
if selected_rt:
    df_moon_f = df_moon_f[df_moon_f["room_type"].isin(selected_rt)]
df_moon_f = df_moon_f[df_moon_f["listing_id"].isin(df_f["listing_id"])]

# ============================================================
# TABS
# ============================================================
tab_home, tab_overview, tab_prices, tab_reviews, tab_moon = st.tabs(
    ["Accueil", "Vue d'ensemble", "Analyse des prix", "Avis & Sentiment", "Pleine Lune"]
)

# ------------------------------------------------------------
# TAB 1 - LANDING PAGE
# ------------------------------------------------------------
with tab_home:
    st.markdown(HERO_HTML, unsafe_allow_html=True)

    # KPIs principaux (depuis les donnees reelles, non filtrees)
    total_listings = len(df_listings)
    avg_price_all = df_listings["price"].mean()
    avg_rating_all = df_listings["review_scores_rating"].mean()
    total_reviews_all = len(df_reviews)
    superhost_pct = df_hosts["is_superhost"].mean() * 100
    multi_host_pct = df_hosts["is_multi_host"].mean() * 100
    moon_reviews = len(df_moon)
    moon_pct = (moon_reviews / total_reviews_all * 100) if total_reviews_all else 0

    st.markdown("### Indicateurs clés")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Logements actifs", f"{total_listings:,}".replace(",", " "))
    c2.metric("Prix moyen / nuit", f"{avg_price_all:.0f} €")
    c3.metric("Note moyenne", f"{avg_rating_all:.2f} / 5")
    c4.metric("Avis analysés", f"{total_reviews_all/1000:.0f}K")

    c5, c6, c7, c8 = st.columns(4)
    c5.metric("Superhosts", f"{superhost_pct:.1f}%")
    c6.metric("Multi-annonces", f"{multi_host_pct:.1f}%")
    c7.metric("Avis pleine lune", f"{moon_pct:.1f}%")
    c8.metric("Période couverte", "2009 → 2021")

    st.markdown(PIPELINE_HTML, unsafe_allow_html=True)

    # Section descriptive
    desc_c1, desc_c2 = st.columns([1.2, 1])
    with desc_c1:
        st.markdown("### À propos du projet")
        st.markdown(
            """
Cette plateforme analytique implémente l'intégralité d'un pipeline data moderne sur les annonces
**Airbnb de Berlin**. Elle s'appuie sur trois piliers :

- **DuckDB** comme moteur analytique embarqué — ultra-rapide sur fichiers locaux.
- **dbt** pour orchestrer les transformations SQL en couches *Bronze / Silver / Gold*.
- **Streamlit + Plotly** pour livrer une expérience interactive et exploratoire.

Au-delà des KPIs classiques (prix, satisfaction, multi-annonces), une **analyse originale**
explore l'effet de la **pleine lune** sur les avis publiés — un clin d'œil aux théories
comportementales lunaires.
            """
        )
    with desc_c2:
        st.markdown("### Quatre angles d'analyse")
        st.markdown(
            """
1. **Vue d'ensemble** — Cartographie globale du marché par type de logement.
2. **Analyse des prix** — Distribution, outliers, segmentation tarifaire.
3. **Avis & Sentiment** — Évolution temporelle, polarité des commentaires.
4. **Pleine Lune** — Recherche d'un signal saisonnier-lunaire dans les reviews.
            """
        )

    st.markdown("---")
    st.markdown(
        "<div style='text-align:center;color:#7A6354;font-size:0.85rem;padding:1rem 0;'>"
        "Naviguez via les onglets ci-dessus pour explorer les analyses détaillées."
        "</div>",
        unsafe_allow_html=True,
    )

# ------------------------------------------------------------
# TAB 2 - VUE D'ENSEMBLE
# ------------------------------------------------------------
with tab_overview:
    st.markdown("## Vue d'ensemble du marché")
    st.markdown(
        f"<div style='color:#7A6354;margin-bottom:1.5rem'>"
        f"Sélection actuelle : <strong style='color:#E85D3C'>{len(df_f):,}</strong> logements"
        f"</div>",
        unsafe_allow_html=True,
    )

    if len(df_f) > 0:
        # Repartition par type de logement
        c1, c2 = st.columns(2)
        with c1:
            rt_counts = df_f.groupby("room_type").size().reset_index(name="count")
            fig = px.bar(
                rt_counts,
                x="room_type",
                y="count",
                title="Répartition par type de logement",
                color="room_type",
                color_discrete_sequence=WARM_PALETTE,
                template=PLOTLY_TEMPLATE,
            )
            fig.update_layout(showlegend=False, height=380)
            st.plotly_chart(fig, use_container_width=True)
        with c2:
            fig2 = px.pie(
                rt_counts,
                values="count",
                names="room_type",
                title="Parts de marché par type",
                color_discrete_sequence=WARM_PALETTE,
                template=PLOTLY_TEMPLATE,
                hole=0.4,
            )
            fig2.update_layout(height=380)
            st.plotly_chart(fig2, use_container_width=True)

        # Stats par type
        st.markdown("### Statistiques par type de logement")
        stats = df_f.groupby("room_type").agg(
            logements=("listing_id", "count"),
            prix_moyen=("price", "mean"),
            prix_median=("price", "median"),
            note_moyenne=("review_scores_rating", "mean"),
            avis_total=("number_of_reviews", "sum"),
            nuits_min_moy=("minimum_nights", "mean"),
        ).round(2).reset_index()
        st.dataframe(stats, use_container_width=True, hide_index=True)

        # Top hosts
        st.markdown("### Top 10 hôtes par nombre d'annonces")
        top_hosts = df_hosts[df_hosts["total_listings"] > 0].nlargest(10, "total_listings")[
            ["host_name", "total_listings", "avg_price", "total_reviews", "is_superhost"]
        ]
        top_hosts.columns = ["Hôte", "Annonces", "Prix moyen (€)", "Avis total", "Superhost"]
        top_hosts["Prix moyen (€)"] = top_hosts["Prix moyen (€)"].round(0)
        st.dataframe(top_hosts, use_container_width=True, hide_index=True)
    else:
        st.info("Aucune donnée pour les filtres sélectionnés.")

# ------------------------------------------------------------
# TAB 3 - ANALYSE DES PRIX
# ------------------------------------------------------------
with tab_prices:
    st.markdown("## Analyse des prix")

    if len(df_f) > 0:
        c1, c2 = st.columns(2)
        with c1:
            # Histogramme prix (filtre les outliers > 500 pour visu)
            df_viz = df_f[df_f["price"] <= 500]
            fig = px.histogram(
                df_viz,
                x="price",
                nbins=50,
                title=f"Distribution des prix (≤ 500€) — n={len(df_viz):,}",
                color_discrete_sequence=["#E85D3C"],
                template=PLOTLY_TEMPLATE,
            )
            fig.update_layout(height=400, bargap=0.05)
            st.plotly_chart(fig, use_container_width=True)
        with c2:
            fig2 = px.box(
                df_f[df_f["price"] <= 500],
                x="room_type",
                y="price",
                title="Boxplot prix par type de logement (≤ 500€)",
                color="room_type",
                color_discrete_sequence=WARM_PALETTE,
                template=PLOTLY_TEMPLATE,
            )
            fig2.update_layout(height=400, showlegend=False)
            st.plotly_chart(fig2, use_container_width=True)

        # Quartiles
        st.markdown("### Statistiques de prix")
        p1, p2, p3, p4, p5 = st.columns(5)
        p1.metric("Min", f"{df_f['price'].min():.0f} €")
        p2.metric("Q1 (25%)", f"{df_f['price'].quantile(0.25):.0f} €")
        p3.metric("Médiane", f"{df_f['price'].median():.0f} €")
        p4.metric("Q3 (75%)", f"{df_f['price'].quantile(0.75):.0f} €")
        p5.metric("Max", f"{df_f['price'].max():.0f} €")

        # Correlation prix / note
        st.markdown("### Corrélation prix vs note moyenne")
        df_corr = df_f.dropna(subset=["review_scores_rating"])
        df_corr = df_corr[df_corr["price"] <= 500]
        if len(df_corr) > 0:
            fig3 = px.scatter(
                df_corr.sample(min(3000, len(df_corr)), random_state=42),
                x="price",
                y="review_scores_rating",
                color="room_type",
                title="Prix vs Note (échantillon)",
                opacity=0.5,
                template=PLOTLY_TEMPLATE,
                color_discrete_sequence=WARM_PALETTE,
            )
            fig3.update_layout(height=420)
            st.plotly_chart(fig3, use_container_width=True)
    else:
        st.info("Aucune donnée pour les filtres sélectionnés.")

# ------------------------------------------------------------
# TAB 4 - AVIS & SENTIMENT
# ------------------------------------------------------------
with tab_reviews:
    st.markdown("## Avis & Sentiment")

    if len(df_rev_f) > 0:
        # KPIs sentiment
        sent_counts = df_rev_f["sentiment"].value_counts()
        total = sent_counts.sum()
        pos_pct = sent_counts.get("positive", 0) / total * 100
        neu_pct = sent_counts.get("neutral", 0) / total * 100
        neg_pct = sent_counts.get("negative", 0) / total * 100

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Avis total", f"{total:,}".replace(",", " "))
        m2.metric("Positifs", f"{pos_pct:.1f}%")
        m3.metric("Neutres", f"{neu_pct:.1f}%")
        m4.metric("Négatifs", f"{neg_pct:.1f}%")

        c1, c2 = st.columns(2)
        with c1:
            # Evolution temporelle
            df_rev_f_copy = df_rev_f.copy()
            df_rev_f_copy["month"] = pd.to_datetime(
                df_rev_f_copy["review_date"], errors="coerce"
            ).dt.to_period("M").astype(str)
            monthly = df_rev_f_copy.groupby("month").size().reset_index(name="count").tail(60)
            fig = px.line(
                monthly,
                x="month",
                y="count",
                title="Volume d'avis par mois (60 derniers)",
                markers=True,
                color_discrete_sequence=["#E85D3C"],
                template=PLOTLY_TEMPLATE,
            )
            fig.update_layout(xaxis_tickangle=-45, height=400)
            st.plotly_chart(fig, use_container_width=True)
        with c2:
            # Distribution sentiment
            sent_df = sent_counts.reset_index()
            sent_df.columns = ["sentiment", "count"]
            color_map = {"positive": "#5A8F3E", "neutral": "#F4A93B", "negative": "#E85D3C"}
            fig2 = px.pie(
                sent_df,
                values="count",
                names="sentiment",
                title="Répartition du sentiment",
                color="sentiment",
                color_discrete_map=color_map,
                template=PLOTLY_TEMPLATE,
                hole=0.5,
            )
            fig2.update_layout(height=400)
            st.plotly_chart(fig2, use_container_width=True)

        # Sentiment par type
        st.markdown("### Sentiment moyen par type de logement")
        sent_by_rt = df_rev_f.groupby("room_type")["sentiment_score"].mean().reset_index()
        sent_by_rt.columns = ["room_type", "score_sentiment"]
        fig3 = px.bar(
            sent_by_rt.sort_values("score_sentiment", ascending=False),
            x="room_type",
            y="score_sentiment",
            title="Score moyen de sentiment (−1 = négatif, +1 = positif)",
            color="score_sentiment",
            color_continuous_scale=[[0, "#E85D3C"], [0.5, "#F4A93B"], [1, "#5A8F3E"]],
            template=PLOTLY_TEMPLATE,
        )
        fig3.update_layout(height=400)
        st.plotly_chart(fig3, use_container_width=True)

        # Echantillon d'avis
        st.markdown("### Échantillon d'avis récents")
        sample_cols = ["review_date", "room_type", "sentiment", "review_text"]
        sample = df_rev_f.sort_values("review_date", ascending=False).head(10)[sample_cols]
        st.dataframe(sample, use_container_width=True, hide_index=True)
    else:
        st.info("Aucune donnée d'avis pour les filtres sélectionnés.")

# ------------------------------------------------------------
# TAB 5 - PLEINE LUNE
# ------------------------------------------------------------
with tab_moon:
    st.markdown("## Analyse Pleine Lune")
    st.markdown(
        "<div style='color:#7A6354;margin-bottom:1rem;font-size:0.95rem'>"
        "Croisement des avis avec les dates de pleine lune (J ou J+1). "
        "Y a-t-il un pattern lunaire dans la satisfaction Airbnb ?"
        "</div>",
        unsafe_allow_html=True,
    )

    df_for_moon = df_moon_f if full_moon_only else df_moon_f
    total_moon = len(df_for_moon)
    total_all_reviews = len(df_rev_f) if len(df_rev_f) > 0 else 1
    pct_moon = total_moon / total_all_reviews * 100

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Avis pleine lune", f"{total_moon:,}".replace(",", " "))
    m2.metric("% du total filtré", f"{pct_moon:.2f}%")
    # Sentiment pleine lune vs nuit normale
    moon_sent = df_for_moon["sentiment_score"].mean() if total_moon else 0
    normal_reviews = df_rev_f[~df_rev_f["listing_id"].isin(df_for_moon["listing_id"]) | True]
    normal_sent = df_rev_f["sentiment_score"].mean() if len(df_rev_f) else 0
    m3.metric("Sentiment lune", f"{moon_sent:.3f}")
    m4.metric("Sentiment global", f"{normal_sent:.3f}")

    if total_moon > 0:
        c1, c2 = st.columns(2)
        with c1:
            # Par type de logement
            moon_rt = df_for_moon.groupby("room_type").size().reset_index(name="avis")
            fig = px.bar(
                moon_rt,
                x="room_type",
                y="avis",
                title="Avis pleine lune par type de logement",
                color="avis",
                color_continuous_scale="Oranges",
                template=PLOTLY_TEMPLATE,
            )
            fig.update_layout(height=380)
            st.plotly_chart(fig, use_container_width=True)
        with c2:
            # Sentiment pleine lune
            moon_sent_df = df_for_moon["sentiment"].value_counts().reset_index()
            moon_sent_df.columns = ["sentiment", "count"]
            color_map = {"positive": "#5A8F3E", "neutral": "#F4A93B", "negative": "#E85D3C"}
            fig2 = px.pie(
                moon_sent_df,
                values="count",
                names="sentiment",
                title="Sentiment des avis pleine lune",
                color="sentiment",
                color_discrete_map=color_map,
                template=PLOTLY_TEMPLATE,
                hole=0.4,
            )
            fig2.update_layout(height=380)
            st.plotly_chart(fig2, use_container_width=True)

        # Evolution annuelle des avis pleine lune
        df_for_moon_copy = df_for_moon.copy()
        df_for_moon_copy["year"] = pd.to_datetime(
            df_for_moon_copy["review_date"], errors="coerce"
        ).dt.year
        yearly = df_for_moon_copy.groupby("year").size().reset_index(name="count")
        fig3 = px.area(
            yearly,
            x="year",
            y="count",
            title="Évolution des avis pleine lune par année",
            color_discrete_sequence=["#F4A93B"],
            template=PLOTLY_TEMPLATE,
        )
        fig3.update_layout(height=380)
        st.plotly_chart(fig3, use_container_width=True)

        st.markdown("### Échantillon d'avis pleine lune")
        cols = ["review_date", "full_moon_date", "room_type", "sentiment", "review_text"]
        cols = [c for c in cols if c in df_for_moon.columns]
        st.dataframe(
            df_for_moon[cols].sort_values("review_date", ascending=False).head(15),
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info("Aucun avis de pleine lune pour les filtres sélectionnés.")

# ============================================================
# FOOTER
# ============================================================
st.markdown("---")
st.markdown(
    "<div style='text-align:center;color:#7A6354;font-size:0.8rem;padding:1rem 0;'>"
    "Airbnb Analytics Platform &bull; dbt + DuckDB + Streamlit &bull; "
    "<strong style='color:#E85D3C'>MBA ESG Big Data & IA — Promotion 2026</strong>"
    "</div>",
    unsafe_allow_html=True,
)
