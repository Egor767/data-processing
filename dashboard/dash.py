import streamlit as st
import pandas as pd
import plotly.express as px
import psycopg2
from datetime import datetime
import os
from pathlib import Path


# ✅ Подключение к БД (как в вашем проекте)
def get_db_connection():
    """Подключение с параметрами из вашего .env"""
    return psycopg2.connect(
        host="localhost",
        port="5433",      # ✅ Ваш порт из .env!
        user="postgres",
        password="postgres",
        database="etl"
    )


def load_dq_data():
    """Загрузка данных DQ из PostgreSQL"""
    conn = get_db_connection()
    try:
        query = """
        SELECT check_type, status, records_checked, records_failed, 
               execution_date, table_name
        FROM s_sql_dds.t_dq_check_results 
        ORDER BY execution_date DESC LIMIT 100
        """
        df = pd.read_sql_query(query, conn)
        return df
    finally:
        conn.close()


def get_summary(df):
    """Расчет сводки"""
    total = len(df)
    passed = len(df[df['status'] == 'passed'])
    failed = len(df[df['status'] == 'failed'])
    success_rate = (passed / total * 100) if total > 0 else 0
    return {
        'total_checks': total,
        'passed': passed,
        'failed': failed,
        'success_rate': success_rate
    }


# ✅ Streamlit Dashboard
st.set_page_config(page_title="Data Quality Dashboard", layout="wide")
st.title("📊 Data Quality Dashboard")


# Загрузка данных
@st.cache_data(ttl=300)  # Кэш 5 минут
def load_data():
    return load_dq_data()


df = load_data()

if df.empty:
    st.warning("Нет данных проверок качества!")
else:
    summary = get_summary(df)

    # ✅ KPI метрики
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Всего проверок", summary['total_checks'])
    col2.metric("✅ Пройдено", summary['passed'], delta=None)
    col3.metric("❌ Failed", summary['failed'], delta=None)
    col4.metric("Успешность", f"{summary['success_rate']:.1f}%")

    # ✅ Графики
    col1, col2 = st.columns(2)
    with col1:
        fig_pie = px.pie(df, names='check_type', values='records_failed',
                         title="Failed по типам проверок")
        st.plotly_chart(fig_pie, use_container_width=True)

    with col2:
        fig_trend = px.line(df, x='execution_date', y='records_failed',
                            color='status', title="Динамика failed")
        st.plotly_chart(fig_trend, use_container_width=True)

    # ✅ Таблица
    st.subheader("Последние проверки")
    st.dataframe(df[['execution_date', 'check_type', 'status', 'records_failed']].head(20))

    # ✅ Алерты
    st.subheader("🚨 Алерты")
    if summary['success_rate'] < 60:
        st.error(f"🔴 КРИТИЧЕСКИЙ! {summary['success_rate']:.1f}% успешности")
    else:
        st.success("🟢 Качество данных в норме")
