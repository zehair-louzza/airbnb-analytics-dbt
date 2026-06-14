import streamlit as st
import duckdb
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os

st.set_page_config(page_title="Airbnb Analytics - Berlin", page_icon="house", layout="wide", initial_sidebar_state="expanded")

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "airbnb.duckdb")

@st.cache_resource
def get_con():
    return duckdb.connect(DB_PATH, read_only=True)

@st.cache_data(ttl=300)
def q(sql):
    return get_con().execute(sql).df()

df_listings = q("SELECT * FROM main_gold.dim_listings")
df_hosts    = q("SELECT * FROM main_gold.dim_hosts")
df_reviews  = q("SELECT * FROM main_gold.fact_reviews")
df_moon     = q("SELECT * FROM main_gold.full_moon_reviews")

st.sidebar.title("Filtres")
neighbourhoods = sorted(df_listings["neighbourhood"].dropna().unique().tolist())
selected_nb = st.sidebar.multiselect("Quartier(s)", options=neighbourhoods, default=[])
price_min = float(df_listings["price"].min())
price_max = float(df_listings["price"].max())
selected_price = st.sidebar.slider("Prix moyen (EUR/nuit)", min_value=price_min, max_value=price_max, value=(price_min, price_max), step=5.0)
room_types = sorted(df_listings["room_type"].dropna().unique().tolist())
selected_rt = st.sidebar.multiselect("Type de logement", options=room_types, default=[])
full_moon_only = st.sidebar.checkbox("Pleine lune uniquement", value=False)

df_f = df_listings.copy()
if selected_nb:
    df_f = df_f[df_f["neighbourhood"].isin(selected_nb)]
df_f = df_f[(df_f["price"] >= selected_price[0]) & (df_f["price"] <= selected_price[1])]
if selected_rt:
    df_f = df_f[df_f["room_type"].isin(selected_rt)]
df_rev_f = df_reviews.copy()
if selected_nb:
    df_rev_f = df_rev_f[df_rev_f["neighbourhood"].isin(selected_nb)]
if selected_rt:
    df_rev_f = df_rev_f[df_rev_f["room_type"].isin(selected_rt)]
df_moon_f = df_moon[df_moon["is_full_moon_review"]==True].copy() if full_moon_only else df_moon.copy()

st.info("Auteur unique : LOUZZA Zehair | MBA ESG Big Data & IA | MBAESG_EVALUATION_MANAGEMENT_OPERATIONNEL_2026")
st.title("Airbnb Analytics Dashboard - Berlin")
st.markdown("**Pipeline : DBT + DuckDB + Streamlit**")
st.divider()

k1,k2,k3,k4,k5 = st.columns(5)
total_listings = len(df_f)
avg_price = df_f["price"].mean() if total_listings>0 else 0
avg_rating = df_f["review_scores_rating"].mean() if total_listings>0 else 0
total_reviews = len(df_rev_f)
hc = df_f.groupby("host_name").size()
multi_host_ratio = ((hc>1).sum()/hc.count()*100) if hc.count()>0 else 0
k1.metric("Logements", f"{total_listings:,}")
k2.metric("Prix moyen/nuit", f"{avg_price:.0f} EUR")
k3.metric("Note moyenne", f"{avg_rating:.2f}/5")
k4.metric("Avis total", f"{total_reviews:,}")
k5.metric("Multi-annonces", f"{multi_host_ratio:.1f}%")

r1,r2,r3,r4,r5 = st.columns(5)
sh = int(df_hosts["is_superhost"].sum()) if "is_superhost" in df_hosts.columns else 0
sh_ratio = sh/len(df_hosts)*100 if len(df_hosts)>0 else 0
occ = (df_f["number_of_reviews"]>=10).mean()*100 if total_listings>0 else 0
pq = (df_f["price"]/df_f["review_scores_rating"].replace(0,pd.NA)).mean() if total_listings>0 else 0
moon_r = df_moon[df_moon["is_full_moon_review"]==True].shape[0]
moon_pct = moon_r/len(df_moon)*100 if len(df_moon)>0 else 0
minn = df_f["minimum_nights"].mean() if total_listings>0 else 0
r1.metric("Superhosts", f"{sh_ratio:.1f}%")
r2.metric("Taux occupation", f"{occ:.1f}%")
r3.metric("Prix/Qualite", f"{pq:.1f} EUR/pt")
r4.metric("Avis pleine lune", f"{moon_pct:.1f}%")
r5.metric("Nuits min moy", f"{minn:.1f}")
st.divider()

tab1,tab2,tab3,tab4 = st.tabs(["Vue par quartier","Analyse des prix","Avis et Ratings","Pleine Lune"])

with tab1:
    st.subheader("Distribution par quartier")
    if len(df_f)>0:
        nb = df_f.groupby("neighbourhood").agg(total=("price","count"),avg_price=("price","mean"),avg_rating=("review_scores_rating","mean")).reset_index().sort_values("total",ascending=False).head(15)
        c1,c2 = st.columns(2)
        with c1:
            fig=px.bar(nb,x="neighbourhood",y="total",color="avg_price",title="Logements par quartier",color_continuous_scale="Reds")
            fig.update_layout(xaxis_tickangle=-45);st.plotly_chart(fig,width='stretch')
        with c2:
            fig2=px.bar(nb,x="neighbourhood",y="avg_price",color="avg_rating",title="Prix moyen par quartier",color_continuous_scale="Blues")
            fig2.update_layout(xaxis_tickangle=-45);st.plotly_chart(fig2,width='stretch')
        st.subheader("Ratio Prix/Qualite par quartier")
        nb["pq_ratio"]=nb["avg_price"]/nb["avg_rating"]
        fig3=px.bar(nb.sort_values("pq_ratio"),x="neighbourhood",y="pq_ratio",title="Prix par point de note (EUR)",color="pq_ratio",color_continuous_scale="RdYlGn_r")
        fig3.update_layout(xaxis_tickangle=-45);st.plotly_chart(fig3,width='stretch')
    else:
        st.info("Aucune donnee pour les filtres selectionnes")

with tab2:
    st.subheader("Analyse des prix")
    if len(df_f)>0:
        c1,c2 = st.columns(2)
        with c1:
            fig=px.histogram(df_f,x="price",nbins=50,title="Distribution des prix",color_discrete_sequence=["#FF5A5F"])
            st.plotly_chart(fig,width='stretch')
        with c2:
            fig2=px.box(df_f,x="room_type",y="price",title="Prix par type de logement",color="room_type")
            st.plotly_chart(fig2,width='stretch')
        st.subheader("Ratio Multi-annonces par quartier")
        mlt=df_f.groupby("neighbourhood").apply(lambda x: (x.groupby("host_name").size()>1).mean()*100).reset_index()
        mlt.columns=["neighbourhood","multi_pct"]
        fig3=px.bar(mlt.sort_values("multi_pct",ascending=False),x="neighbourhood",y="multi_pct",title="% Hosts multi-annonces par quartier",color="multi_pct",color_continuous_scale="Oranges")
        fig3.update_layout(xaxis_tickangle=-45);st.plotly_chart(fig3,width='stretch')
    else:
        st.info("Aucune donnee")

with tab3:
    st.subheader("Avis et Ratings")
    if len(df_rev_f)>0:
        c1,c2 = st.columns(2)
        with c1:
            if "review_date" in df_rev_f.columns:
                df_rev_f["month"]=pd.to_datetime(df_rev_f["review_date"],errors="coerce").dt.to_period("M").astype(str)
                monthly=df_rev_f.groupby("month").size().reset_index(name="count").tail(24)
                fig=px.line(monthly,x="month",y="count",title="Avis par mois",markers=True,color_discrete_sequence=["#FF5A5F"])
                fig.update_layout(xaxis_tickangle=-45);st.plotly_chart(fig,width='stretch')
        with c2:
            if "review_scores_rating" in df_f.columns:
                rt_rating=df_f.groupby("room_type")["review_scores_rating"].mean().reset_index()
                fig2=px.bar(rt_rating,x="room_type",y="review_scores_rating",title="Note moyenne par type",color="review_scores_rating",color_continuous_scale="Greens")
                st.plotly_chart(fig2,width='stretch')
        st.subheader("Top 10 logements les mieux notes")
        top10=df_f[["host_name","neighbourhood","room_type","price","review_scores_rating","number_of_reviews"]].sort_values("review_scores_rating",ascending=False).head(10)
        st.dataframe(top10,width='stretch')
    else:
        st.info("Aucune donnee")

with tab4:
    st.subheader("Analyse Pleine Lune")
    if len(df_moon_f)>0:
        c1,c2 = st.columns(2)
        with c1:
            moon_nb=df_moon_f.groupby("neighbourhood").size().reset_index(name="avis").sort_values("avis",ascending=False).head(10)
            fig=px.bar(moon_nb,x="neighbourhood",y="avis",title="Avis pleine lune par quartier",color="avis",color_continuous_scale="Purples")
            fig.update_layout(xaxis_tickangle=-45);st.plotly_chart(fig,width='stretch')
        with c2:
            moon_rt=df_moon_f.groupby("room_type").size().reset_index(name="avis")
            fig2=px.pie(moon_rt,values="avis",names="room_type",title="Avis pleine lune par type")
            st.plotly_chart(fig2,width='stretch')
        st.subheader("Comparaison : pleine lune vs nuit normale")
        cmp=df_moon.groupby("is_full_moon_review").size().reset_index(name="count")
        cmp["label"]=cmp["is_full_moon_review"].map({True:"Pleine Lune",False:"Nuit normale"})
        fig3=px.bar(cmp,x="label",y="count",title="Volume d avis : pleine lune vs normal",color="label")
        st.plotly_chart(fig3,width='stretch')
        st.subheader("Derniers avis pleine lune")
        cols=[c for c in ["listing_name","neighbourhood","review_date","reviewer_name","review_text"] if c in df_moon_f.columns]
        st.dataframe(df_moon_f[cols].head(20),width='stretch')
    else:
        st.info("Aucun avis de pleine lune trouve")

st.divider()
st.caption("Airbnb Analytics Platform | DBT + DuckDB + Streamlit | MBA ESG 2026")
