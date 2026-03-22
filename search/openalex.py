"""
OpenAlex 检索 — via OpenAlex API
文档: https://docs.openalex.org/
免费开源，速率限制: 10 req/sec，需 email
"""
import urllib.request
import urllib.parse
import json
import time
from typing import Optional


class OpenAlexSearcher:
    BASE_URL = "https://api.openalex.org"
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
    
    def _headers(self) -> dict:
        h = {
            'User-Agent': 'ResearchSuite/1.0 (mailto:research@example.com)',
            'Accept': 'application/json',
        }
        if self.api_key:
            h['Authorization'] = f"Bearer {self.api_key}"
        return h
    
    def search(self, query: str, limit: int = 20) -> list[dict]:
        # OpenAlex 使用 filter 语法
        search_term = urllib.parse.quote_plus(query)
        url = (
            f"{self.BASE_URL}/works?"
            f"search={search_term}"
            f"&per-page={min(limit * 2, 100)}"
            f"&mailto=research@example.com"
        )
        
        req = urllib.request.Request(url, headers=self._headers())
        
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode('utf-8'))
        except Exception as e:
            print(f"OpenAlex search error: {e}")
            return []
        
        papers = []
        for item in data.get('results', []):
            authorships = item.get('authorships', [])
            authors = [
                au.get('author', {}).get('display_name', '')
                for au in authorships[:10]
            ]
            
            # 关键词
            topics = item.get('topics', [])
            keywords = [t.get('display_name', '').lower() for t in topics[:5]]
            
            # 出版来源
            primary_loc = item.get('primary_location', {}) or {}
            source = item.get('primary_location', {}).get('source', {}) or {}
            journal = source.get('display_name', 'N/A')
            
            papers.append({
                'id': item.get('id', ''),
                'title': item.get('title', 'N/A'),
                'abstract': item.get('abstract_inverted_index', {}),  # 保留，待处理
                'authors': authors,
                'year': str(item.get('publication_year', '')),
                'journal': journal,
                'doi': item.get('doi'),
                'url': item.get('doi') or item.get('id', ''),
                'keywords': keywords,
                'citations': item.get('cited_by_count', 0) or 0,
                'methods': topics[:3],
            })
        
        return papers
