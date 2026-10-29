"""Knowledge Retriever Tool for Research and Verification Agents.

Uses standard Python HTTP requests against the Wikipedia API and structured open sources
to obtain grounded background data without requiring external search API keys.
"""

import json
import urllib.parse
import urllib.request
from typing import Dict, List, Any


class KnowledgeRetriever:
    """Retrieves factual information, definitions, and articles for a research topic."""

    USER_AGENT = "AI-MultiAgent-ResearchSystem/1.0 (contact: info@sarvam.ai)"

    @classmethod
    def search_articles(cls, query: str, limit: int = 3) -> List[Dict[str, str]]:
        """Search Wikipedia for relevant articles matching the query.
        
        Returns a list of dicts with 'title' and 'snippet'.
        """
        encoded_query = urllib.parse.quote(query)
        url = (
            f"https://en.wikipedia.org/w/api.php?action=query&list=search"
            f"&srsearch={encoded_query}&utf8=&format=json&srlimit={limit}"
        )
        try:
            req = urllib.request.Request(url, headers={"User-Agent": cls.USER_AGENT})
            with urllib.request.urlopen(req, timeout=8) as response:
                data = json.loads(response.read().decode("utf-8"))
                search_results = data.get("query", {}).get("search", [])
                
                clean_results = []
                for res in search_results:
                    # Strip basic HTML tags from snippet
                    raw_snippet = res.get("snippet", "")
                    clean_snippet = (
                        raw_snippet.replace('<span class="searchmatch">', "")
                        .replace("</span>", "")
                        .replace("&quot;", '"')
                        .replace("&#039;", "'")
                    )
                    clean_results.append({
                        "title": res.get("title", ""),
                        "snippet": clean_snippet,
                        "pageid": str(res.get("pageid", ""))
                    })
                return clean_results
        except Exception as err:
            return [{"title": query, "snippet": f"Web search notice: {err}", "pageid": "0"}]

    @classmethod
    def get_article_extract(cls, title: str, intro_only: bool = True) -> str:
        """Fetch the content extract or summary for a specific article title."""
        encoded_title = urllib.parse.quote(title)
        intro_param = "&exintro=true" if intro_only else ""
        url = (
            f"https://en.wikipedia.org/w/api.php?action=query&prop=extracts"
            f"&titles={encoded_title}{intro_param}&explaintext=true&format=json"
        )
        try:
            req = urllib.request.Request(url, headers={"User-Agent": cls.USER_AGENT})
            with urllib.request.urlopen(req, timeout=8) as response:
                data = json.loads(response.read().decode("utf-8"))
                pages = data.get("query", {}).get("pages", {})
                for _, page_info in pages.items():
                    extract = page_info.get("extract", "")
                    if extract:
                        return extract.strip()
                return ""
        except Exception as err:
            return f"Extraction unavailable: {err}"

    @classmethod
    def gather_background_context(cls, topic: str, max_articles: int = 3) -> Dict[str, Any]:
        """Gathers comprehensive background facts for a research topic.
        
        Searches top articles and compiles extracts.
        """
        search_hits = cls.search_articles(topic, limit=max_articles)
        summaries = []

        for hit in search_hits:
            title = hit.get("title")
            if not title:
                continue
            extract = cls.get_article_extract(title, intro_only=True)
            if extract:
                # Keep first 1200 characters for concise context
                truncated = extract[:1200] + ("..." if len(extract) > 1200 else "")
                summaries.append({
                    "title": title,
                    "summary": truncated,
                    "url": f"https://en.wikipedia.org/wiki/{urllib.parse.quote(title.replace(' ', '_'))}"
                })

        return {
            "topic": topic,
            "sources_found": len(summaries),
            "sources": summaries
        }
