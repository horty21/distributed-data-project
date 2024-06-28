import streamlit as st
import pandas as pd
import altair as alt
import pymongo

client = pymongo.MongoClient("mongodb://sdvroot:sdvroot@localhost:27017")
db = client.products
collection = db.computers
df = pd.DataFrame(list(collection.find()))
df.pop("_id")
# df = pd.read_csv("/home/sdvbigdata/SDV-DonneesDistribuees/computers.csv")
st.title("Computers Sales")

st.markdown("## Description")
st.write(df.describe())

st.markdown("## Exploration")
st.dataframe(df)
