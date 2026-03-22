"""
多源联邦检索模块
并发查询多个数据库，统一去重后返回结构化结果
"""
import asyncio
import hashlib
import html
from typing import Optional
from concurrent.futures import ThreadPoolExecutor
import time

from .pubmed import PubMedSearcher
from .arxiv import ArXivSearcher
from .semantic import SemanticScholarSearcher
from .openalex import OpenAlexSearcher
from .crossref import CrossRefSearcher
from .bgpt import BGPTSearcher


SEARCHERS = {
    'pubmed': PubMedSearcher,
    'arxiv': ArXivSearcher,
    'semantic': SemanticScholarSearcher,
    'openalex': OpenAlexSearcher,
    'crossref': CrossRefSearcher,
    'bgpt': BGPTSearcher,
}


def _deduplicate(papers: list[dict]) -> list[dict]:
    """基于 DOI / Title 哈希去重"""
    seen = set()
    unique = []
    for p in papers:
        key = p.get('doi') or _title_hash(p.get('title', ''))
        if key and key not in seen:
            seen.add(key)
            unique.append(p)
    return unique


def _title_hash(title: str) -> str:
    return hashlib.md5(title.lower().encode()).hexdigest()[:16]


def _normalize_paper(p: dict, source: str) -> dict:
    """统一字段格式"""
    return {
        'id': p.get('id') or _title_hash(p.get('title', '')),
        'title': html.unescape(str(p.get('title', 'N/A'))),
        'authors': p.get('authors', []),
        'year': p.get('year') or p.get('published') or 'N/A',
        'journal': p.get('journal') or p.get('venue') or p.get('container', 'N/A'),
        'doi': p.get('doi'),
        'url': p.get('url') or (f"https://doi.org/{p['doi']}" if p.get('doi') else None),
        'abstract': _clean_abstract(p.get('abstract', '')),
        'keywords': p.get('keywords', []) or [],
        'source': source,
        'citations': p.get('citation_count') or p.get('citations', 0),
        'methods': p.get('methods', []),
        'results': p.get('results', {}),
        'raw': p,  # 保留原始数据
    }


def _clean_abstract(text: str) -> str:
    if not text:
        return ''
    # 去除 HTML 标签
    import re
    text = re.sub(r'<[^>]+>', '', text)
    text = html.unescape(text)
    # 去除多余空白
    text = re.sub(r'\s+', ' ', text).strip()
    return text


class FederatedSearcher:
    """联邦检索器 — 并发查询多个数据库"""

    # 不需要 API Key 的数据源
    NO_KEY_BASES = {'arxiv', 'openalex', 'crossref'}

    def __init__(self, api_keys: dict = None):
        self.api_keys = api_keys or {}
        self.searchers = {}
        for name, cls in SEARCHERS.items():
            if name in self.NO_KEY_BASES:
                self.searchers[name] = cls()
            else:
                self.searchers[name] = cls(api_key=self.api_keys.get(name))
    
    def search(
        self,
        query: str,
        databases: list[str] = None,
        limit: int = 20,
    ) -> dict:
        """
        并发检索，返回去重后的统一格式结果
        
        Args:
            query: 检索词
            databases: 要查询的数据库列表，默认全部
            limit: 每库返回数量
        
        Returns:
            {
                'query': str,
                'databases': list[str],
                'total': int,
                'papers': list[dict],
                'by_source': dict[str, int],
            }
        """
        databases = databases or list(SEARCHERS.keys())
        all_results = []
        by_source = {}
        
        start = time.time()
        
        # 并发查询所有数据库
        with ThreadPoolExecutor(max_workers=min(len(databases), 6)) as executor:
            futures = {}
            for db in databases:
                if db in self.searchers:
                    fut = executor.submit(
                        self.searchers[db].search,
                        query,
                        limit
                    )
                    futures[db] = fut
            
            for db, fut in futures.items():
                try:
                    papers = fut.result(timeout=30)
                    normalized = [_normalize_paper(p, db) for p in papers]
                    all_results.extend(normalized)
                    by_source[db] = len(normalized)
                except Exception as e:
                    by_source[db] = 0
                    print(f"⚠️  {db} 检索失败: {e}", file=__import__('sys').stderr)
        
        # 去重
        all_results = _deduplicate(all_results)
        
        # 按相关度 / 引用数排序
        all_results.sort(
            key=lambda p: (p.get('citations', 0) or 0, p.get('year', '0')),
            reverse=True
        )
        
        elapsed = time.time() - start
        
        return {
            'query': query,
            'databases': [d for d in databases if d in by_source],
            'total': len(all_results),
            'papers': all_results[:limit],
            'by_source': by_source,
            'elapsed_seconds': round(elapsed, 2),
        }
    
    def search_async(self, query: str, databases: list[str] = None, limit: int = 20) -> dict:
        """异步版本（asyncio）"""
        return self.search(query, databases, limit)
