# -*- coding: utf-8 -*-
"""components/geo.py — Geographic breakdown. (Sprint 4)"""
import streamlit as st
import pandas as pd


def render(df: pd.DataFrame) -> None:
    st.header("Geographic Breakdown")
    st.info("Geographic charts — coming in Sprint 4.")
