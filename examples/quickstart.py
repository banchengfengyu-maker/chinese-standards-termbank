#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Quickstart Example: How to query the Chinese Standards Term Bank directly in Python.
Author: Bancheng Fengyu (banchengfengyu-maker)
"""

import sqlite3
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Locate the SQLite database
DB_PATH = Path(__file__).resolve().parent.parent / "data" / "standard_term_bank.sqlite"


def lookup_chinese(zh_term: str):
    """Query standard English translations for a Chinese term."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    key = zh_term.strip().lower()

    sql = """
        SELECT zh, en, domain, source_name, trust_score
        FROM zh_to_en_best
        WHERE zh_key = ?
        ORDER BY trust_score DESC
    """
    cur.execute(sql, (key,))
    rows = cur.fetchall()
    conn.close()
    return rows


def lookup_english(en_term: str):
    """Query standard Chinese translations for an English term."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    key = en_term.strip().lower()

    sql = """
        SELECT en, zh, domain, source_name, trust_score
        FROM en_to_zh_best
        WHERE en_key = ?
        ORDER BY trust_score DESC
    """
    cur.execute(sql, (key,))
    rows = cur.fetchall()
    conn.close()
    return rows


if __name__ == "__main__":
    print(f"Connecting to: {DB_PATH.name}")

    test_zh = "建筑物(构筑物)"
    print(f"\n--- 查询中文: {test_zh} ---")
    for zh, en, domain, source, score in lookup_chinese(test_zh):
        print(f"[{domain}] {zh} -> {en} (来源: {source})")

    test_en = "primary water system"
    print(f"\n--- 查询英文: {test_en} ---")
    for en, zh, domain, source, score in lookup_english(test_en):
        print(f"[{domain}] {en} -> {zh} (来源: {source})")
