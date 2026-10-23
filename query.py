#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Chinese Standards Bilingual Term Bank - CLI Query Tool
Author: Bancheng Fengyu (banchengfengyu-maker)
License: MIT with Attribution
"""

from __future__ import annotations

import argparse
import json
import re
import sqlite3
import sys
from pathlib import Path
from typing import Any

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

ROOT = Path(__file__).resolve().parent
DEFAULT_DB = ROOT / "data" / "standard_term_bank.sqlite"


def normalize_key(text: str) -> str:
    """Normalize query key by collapsing whitespace and lowercasing."""
    return re.sub(r"\s+", " ", text).strip().casefold()


def has_cjk(text: str) -> bool:
    """Check if query text contains Chinese/CJK characters."""
    return bool(re.search(r"[\u4e00-\u9fff]", text))


def query(
    db_path: Path,
    term: str,
    *,
    direction: str = "auto",
    domain: str = "",
    limit: int = 20,
    exact: bool = True
) -> list[dict[str, Any]]:
    """Query bilingual terms from SQLite term bank."""
    if not db_path.exists():
        raise FileNotFoundError(f"Database not found at: {db_path}")

    if direction == "auto":
        direction = "zh2en" if has_cjk(term) else "en2zh"

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        if exact:
            key = normalize_key(term)
            if direction == "zh2en":
                sql = """
                    SELECT zh AS source, en AS target, domain, term_id, trust_score, source_name, alternatives_json
                    FROM zh_to_en_best
                    WHERE zh_key = ? {domain_filter}
                    ORDER BY trust_score DESC
                    LIMIT ?
                """
            else:
                sql = """
                    SELECT en AS source, zh AS target, domain, term_id, trust_score, source_name, alternatives_json
                    FROM en_to_zh_best
                    WHERE en_key = ? {domain_filter}
                    ORDER BY trust_score DESC
                    LIMIT ?
                """
            params: list[Any] = [key]
        else:
            pattern = f"%{term.strip()}%"
            if direction == "zh2en":
                sql = """
                    SELECT zh AS source, en AS target, domain, id AS term_id, trust_score, source_name, '[]' AS alternatives_json
                    FROM terms
                    WHERE zh LIKE ? {domain_filter}
                    ORDER BY trust_score DESC
                    LIMIT ?
                """
            else:
                sql = """
                    SELECT en AS source, zh AS target, domain, id AS term_id, trust_score, source_name, '[]' AS alternatives_json
                    FROM terms
                    WHERE en LIKE ? {domain_filter}
                    ORDER BY trust_score DESC
                    LIMIT ?
                """
            params = [pattern]

        domain_filter = ""
        if domain:
            domain_filter = "AND domain = ?"
            params.append(domain)
        params.append(limit)

        rows = conn.execute(sql.format(domain_filter=domain_filter), params).fetchall()

        results = []
        for r in rows:
            alts = json.loads(r["alternatives_json"] or "[]")
            results.append({
                "source": r["source"],
                "target": r["target"],
                "domain": r["domain"],
                "term_id": r["term_id"],
                "trust_score": r["trust_score"],
                "source_name": r["source_name"],
                "alternatives": alts[:5] if alts else [],
            })
        return results
    finally:
        conn.close()


def main() -> int:
    parser = argparse.ArgumentParser(description="Query the Chinese Standards Bilingual Term Bank.")
    parser.add_argument("--term", "-t", required=True, help="Term to search (Chinese or English)")
    parser.add_argument("--db", default=str(DEFAULT_DB), help="Path to standard_term_bank.sqlite")
    parser.add_argument("--direction", "-d", choices=["auto", "zh2en", "en2zh"], default="auto", help="Translation direction")
    parser.add_argument("--domain", help="Filter by specific engineering domain")
    parser.add_argument("--fuzzy", "-f", action="store_true", help="Enable fuzzy/contains matching instead of exact")
    parser.add_argument("--limit", "-n", type=int, default=10, help="Max results to return")
    parser.add_argument("--json", action="store_true", help="Output pure JSON format")

    args = parser.parse_args()

    results = query(
        Path(args.db),
        args.term,
        direction=args.direction,
        domain=args.domain or "",
        limit=args.limit,
        exact=not args.fuzzy
    )

    if args.json:
        print(json.dumps({"query": args.term, "count": len(results), "results": results}, ensure_ascii=False, indent=2))
        return 0

    if not results:
        print(f"未找到与 '{args.term}' 相关的术语。")
        return 0

    print(f"\n🔍 查询词: '{args.term}' (共找到 {len(results)} 条匹配结果):")
    print("-" * 75)
    for i, item in enumerate(results, 1):
        print(f"[{i}] {item['source']}  ==>  {item['target']}")
        print(f"    领域: {item['domain']} | 信任分: {item['trust_score']}")
        print(f"    来源标准: {item['source_name']}")
        if item["alternatives"]:
            print(f"    其他候选: {', '.join(item['alternatives'])}")
        print("-" * 75)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
