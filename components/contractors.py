# -*- coding: utf-8 -*-
"""components/contractors.py — Contractor leaderboard. (Sprint 4)"""
import streamlit as st
import pandas as pd


def render(df: pd.DataFrame) -> None:
    st.header("Contractor Leaderboard")
    st.info("Contractor leaderboard — coming in Sprint 4.")
