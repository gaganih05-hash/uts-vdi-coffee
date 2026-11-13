import streamlit as st
import pandas as pd
import sqlite3
import json
import plotly.express as px

# Konfigurasi Halaman Web
st.set_page_config(page_title="Coffee Shop Data Pipeline & Viz", layout="wide")

st.title("☕ Multi-DBMS Data Pipeline & Web Visualization")
st.markdown("**Mata Kuliah:** Visualisasi Data dan Informasi | **Studi Kasus:** Coffee Shop Sales")
st.markdown("---")

# --- 1. INISIALISASI & DATA PIPELINE MULTI-DBMS ---
@st.cache_data
def load_and_process_data():
    # Membaca dataset CSV asli
    df = pd.read_csv('coffee-shop-sales-sample.csv', comment='#')
    
    # DBMS 1 (Relational - SQLite)
    conn = sqlite3.connect(':memory:') # Menggunakan SQLite in-memory untuk demo cepat
    df[['transaction_id', 'transaction_date', 'transaction_time', 'store_location', 'unit_price', 'quantity']].to_sql(
        'transactions', conn, if_exists='replace', index=False
    )
    df_trans_db = pd.read_sql("SELECT * FROM transactions", conn)
    conn.close()
    
    # DBMS 2 (NoSQL / Document - Simulasi JSON/MongoDB)
    df_products = df[['product_category', 'product_type']].drop_duplicates().reset_index(drop=True)
    df_products['product_id'] = [f"PRD-{i+1:03d}" for i in range(len(df_products))]
    
    # Hubungkan ID produk ke tabel transaksi untuk simulasi data pipeline
    df_trans_db['product_id'] = [f"PRD-{(i % len(df_products)) + 1:03d}" for i in range(len(df_trans_db))]
    
    # Melakukan Data Joining (Federation) antara DBMS 1 dan DBMS 2 via Pandas
    df_merged = pd.merge(df_trans_db, df_products, on='product_id', how='left')
    df_merged['total_sales'] = df_merged['unit_price'] * df_merged['quantity']
    
    return df_merged

# Panggil fungsi data pipeline
df_merged = load_and_process_data()

# --- 2. INTERAKTIVITAS ANTAR MUKA (SIDEBAR FILTER) ---
st.sidebar.header("🎛️ Panel Kontrol & Filter")
selected_location = st.sidebar.multiselect(
    "Pilih Lokasi Toko:",
    options=df_merged['store_location'].unique(),
    default=df_merged['store_location'].unique()
)

# Filter data berdasarkan pilihan sidebar
filtered_df = df_merged[df_merged['store_location'].isin(selected_location)]

# --- 3. TAMPILAN UTAMA & TABEL DATA GABUNGAN ---
st.subheader("📊 Pratinjau Data Gabungan (Multi-DBMS Pipeline)")
st.dataframe(filtered_df.head(10), use_container_width=True)

# --- 4. VISUALISASI GRAFIK INTERAKTIF (PLOTLY) ---
col1, col2 = st.columns(2)

with col1:
    st.markdown("### Total Penjualan per Kategori")
    cat_sales = filtered_df.groupby('product_category')['total_sales'].sum().reset_index()
    fig_bar = px.bar(
        cat_sales, 
        x='product_category', 
        y='total_sales', 
        color='product_category',
        title="Penjualan Berdasarkan Kategori Produk"
    )
    st.plotly_chart(fig_bar, use_container_width=True)

with col2:
    st.markdown("### Tren Penjualan Harian")
    date_sales = filtered_df.groupby('transaction_date')['total_sales'].sum().reset_index()
    fig_line = px.line(
        date_sales, 
        x='transaction_date', 
        y='total_sales', 
        markers=True,
        title="Grafik Tren Waktu Transaksi"
    )
    st.plotly_chart(fig_line, use_container_width=True)

# --- 5. INFORMASI SITASI & ARSITEKTUR ---
st.markdown("---")
st.markdown("### 📌 Informasi Arsitektur & Sitasi Sumber Data")
st.markdown("- **Sumber Data Asli:** [Datavix Coffee Shop Sales](https://www.datavix.in/datasets/coffee-shop-sales)")
st.markdown("- **DBMS 1 (Relational):** SQLite (Menyimpan data transaksi operasional)")
st.markdown("- **DBMS 2 (NoSQL / Document):** JSON / MongoDB (Menyimpan metadata produk)")