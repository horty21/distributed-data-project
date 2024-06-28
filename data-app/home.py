import streamlit as st
import pandas as pd
import altair as alt
import pymongo
from st_pages import Page, show_pages

# Configuration de la page
st.set_page_config(
    layout="wide",
    page_title="Analyse des config pc portable LDLC",
    page_icon=":computer:",
)

# show_pages(
#     [
#         Page("home.py", "Accueil", "🏠"),
#         Page("pages/statistics.py", "Statistiques", "📜"),
#     ],
# )

client = pymongo.MongoClient("mongodb://sdvroot:sdvroot@localhost:27017")
db = client.products
collection = db.computers
df = pd.DataFrame(list(collection.find()))
# df = pd.read_csv("/home/sdvbigdata/SDV-DonneesDistribuees/computers.csv")
st.title("Computers Sales")

col1, col2 = st.columns([0.5, 0.5])
with col1.container():
    # Donut chart: Top 5 brands
    filtered_df = df[df["STARS"] > 7]
    brand_counts = filtered_df["BRAND"].value_counts()
    top_5_brands = brand_counts.head(5).reset_index()
    top_5_brands.columns = ["BRAND", "COUNT"]
    st.markdown("## Top 5️⃣ Brands with STARS > 7")
    chart = (
        alt.Chart(top_5_brands)
        .mark_arc(innerRadius=50)
        .encode(
            theta=alt.Theta(field="COUNT", type="quantitative"),
            color=alt.Color(field="BRAND", type="nominal"),
            tooltip=["BRAND", "COUNT"],
        )
        .properties(title="Top 5 brands")
    )
    st.altair_chart(chart, theme="streamlit", use_container_width=True)

with col2:
    # Évaluation moyenne des marques
    average_stars = df.groupby("BRAND")["STARS"].mean().reset_index()
    average_stars.columns = ["BRAND", "AVERAGE STARS"]
    st.markdown("## Average ⭐ ratings")
    chart_b = (
        alt.Chart(average_stars)
        .mark_bar()
        .encode(x=alt.X("BRAND"), y=alt.Y("AVERAGE STARS"), color="BRAND")
    )
    st.altair_chart(chart_b, theme="streamlit", use_container_width=True)
    # st.bar_chart(average_stars.set_index('BRAND'), color="BRAND")

st.markdown("## Breakdown par marque 🔍")
brands = sorted(set(df["BRAND"]))
opt = st.selectbox("MARQUE", brands)
b_col1, b_col2 = st.columns([0.5, 0.5])

with b_col1:
    # Size screen repartition
    st.markdown("## Size screen repartition")
    screen_size_count = (
        df[df["BRAND"] == opt]["SIZE SCREEN"].value_counts().reset_index()
    )
    screen_size_count.columns = ["SIZE SCREEN", "COUNT"]
    screen_size_count = screen_size_count.sort_values(by=["COUNT"])
    st.bar_chart(screen_size_count.set_index("SIZE SCREEN"))

with b_col2:
    # Analyse des types de stockage
    storage_counts = df[df["BRAND"] == opt]["STORAGE"].value_counts().reset_index()
    storage_counts.columns = ["STORAGE", "COUNT"]
    st.markdown("## Storage repartition")
    storage_counts = storage_counts.sort_values(by=["COUNT"])
    st.bar_chart(storage_counts.set_index("STORAGE"))
