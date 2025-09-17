import pandas as pd
from supabase import create_client, Client
import streamlit as st
from typing import Callable, List, Optional


def get_supabase_client() -> Client:
    """
    Erstellt einen Supabase Client aus den Streamlit-Secrets.
    """
    url: str = st.secrets["supabase"]["url"]
    key: str = st.secrets["supabase"]["key"]
    return create_client(url, key)


supabase: Client = get_supabase_client()


def fetch_all(
    table: str,
    filters: Optional[List[Callable]] = None,
    page_size: int = 1000
) -> pd.DataFrame:
    """
    Lädt alle Datensätze aus einer Supabase-Tabelle über Paging.

    :param table: Tabellenname
    :param filters: Liste mit Filterfunktionen, z. B.:
                    [lambda q: q.eq("season", 2025)]
    :param page_size: Anzahl Datensätze pro Page
    :return: Pandas DataFrame mit den Ergebnissen
    """
    all_data = []
    start = 0

    while True:
        query = supabase.table(table).select("*").range(start, start + page_size - 1)

        # Filter anwenden
        if filters:
            for f in filters:
                query = f(query)

        resp = query.execute()
        data = resp.data

        if not data:
            break

        all_data.extend(data)
        start += page_size

    return pd.DataFrame(all_data)
