#!/usr/bin/env python3
"""
AI Selector Agent (Final Version)
"""

import json
import re
from typing import Dict, List, Optional, Any
from bs4 import BeautifulSoup, element
from difflib import SequenceMatcher
from dataclasses import dataclass

@dataclass
class SelectorMatch:
    original_selector: str
    new_selector: str
    confidence: float
    reasoning: str

class SelectorAgent:
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4-turbo"):
        self.use_ai = bool(api_key)
        self.model = model
        self.client = None
        if self.use_ai:
            try:
                from openai import OpenAI
                self.client = OpenAI(api_key=api_key)
                print(f"🤖 OpenAI client initialized for model '{self.model}'.")
            except ImportError:
                print("⚠️  OpenAI library not found. Falling back to rule-based agent."); self.use_ai = False
        else:
            print("🤖 No API key provided. Using rule-based agent.")

    def _extract_element_context(self, html: str, selector: str) -> Optional[Dict]:
        try:
            soup = BeautifulSoup(html, 'html.parser')
            elem = soup.select_one(selector)
            if not elem: return None
            return {
                'selector': selector,
                'outer_html': str(elem),
                'text_content': re.sub(r'\s+', ' ', elem.get_text(strip=True)[:300])
            }
        except Exception:
            return None

    def _get_ai_prompt(self, old_context: Dict[str, Any], candidates: List[Dict[str, Any]], failure_context: Optional[str] = None):
        system_prompt = """
You are a world-class Senior Test Automation Engineer. Your only job is to find the single best, most stable, and maintainable CSS selector for a web element that has changed.

Analyze the old selector, its context, and the candidate elements from the new DOM.

Your response MUST be a valid JSON object with `new_selector`, `confidence` (0.0-1.0), and `reasoning`.

Selector Priority:
1.  Unique `data-testid`: The gold standard.
2.  Composite Selector: A `data-testid` on a parent combined with a stable child class is excellent (e.g., [data-testid='film-entry'] .film-name).
3.  Unique `id`: Good, but less preferred than `data-testid`.
4.  Meaningful Class Name: Use only if it describes function, not appearance (e.g., .user-profile-card is good, .text-blue is bad).
5.  NEVER use structural selectors that rely on `nth-child` or are overly long and brittle.
"""
        user_prompt = "I need to find a new CSS selector.\n"
        if failure_context:
            user_prompt += f"\nATTENTION: A previous attempt failed with this error:\n\"{failure_context}\"\nRe-evaluate with extreme care.\n"
        user_prompt += "\nOld Element Context:\n"
        user_prompt += json.dumps(old_context, indent=2)
        user_prompt += "\n\nTop potential candidates from the New DOM, ranked by text similarity:\n"

        for i, candidate in enumerate(candidates[:5]):
            html_snippet = candidate['element'].prettify().replace("```", "\\`\\`\\`")
            user_prompt += f"\n---\nCandidate #{i+1}:\n{html_snippet}\n"

        user_prompt += "\n\nProvide the single best selector in the following JSON format:\n"
        user_prompt += '{ "new_selector": "...", "confidence": 0.0, "reasoning": "..." }'

        return system_prompt, user_prompt

    def _map_with_ai(self, old_selector: str, old_html: str, new_html: str, failure_context: Optional[str] = None) -> SelectorMatch:
        old_context = self._extract_element_context(old_html, old_selector)
        if not old_context:
            return SelectorMatch(old_selector, "", 0.0, "Original element not found.")

        soup_v2 = BeautifulSoup(new_html, 'html.parser')
        old_text = old_context.get('text_content', '')
        candidates = []
        for elem in soup_v2.find_all(True):
            new_text = re.sub(r'\s+', ' ', elem.get_text(strip=True)[:300])
            if old_text and new_text:
                score = SequenceMatcher(None, old_text, new_text).ratio()
                if score > 0.3:
                    candidates.append({'element': elem, 'score': score})

        candidates.sort(key=lambda x: x['score'], reverse=True)
        if not candidates:
            return SelectorMatch(old_selector, "", 0.0, "No similar element found.")

        system_prompt, user_prompt = self._get_ai_prompt(old_context, candidates, failure_context)
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.0
            )
            result = json.loads(response.choices[0].message.content)
            return SelectorMatch(
                original_selector=old_selector,
                new_selector=result.get("new_selector", ""),
                confidence=float(result.get("confidence", 0.0)),
                reasoning=result.get("reasoning", "N/A")
            )
        except Exception as e:
            print(f"❌ OpenAI API call failed: {e}. Falling back to rule-based method.")
            return self._fallback_mapping(old_selector, old_html, new_html)

    def batch_map_selectors(self, selectors_to_map: Dict[str, str], old_html: str, new_html: str, failure_context: Optional[Dict[str, str]] = None) -> Dict[str, SelectorMatch]:
        results = {}
        print(f"🤖 Mapping {len(selectors_to_map)} selectors...")
        for name, selector in selectors_to_map.items():
            context_for_this_selector = (
                failure_context.get("error_message")
                if failure_context and failure_context.get("selector_name") == name
                else None
            )
            if context_for_this_selector:
                print(f"   Re-healing high-priority selector: {name}")
            else:
                print(f"   Mapping: {name} ('{selector}')")
            if self.use_ai:
                result = self._map_with_ai(selector, old_html, new_html, context_for_this_selector)
            else:
                result = self._fallback_mapping(selector, old_html, new_html)
            results[name] = result
            if result.confidence > 0.7:
                print(f"   ✅ Confident match for '{name}': '{result.new_selector}'")
            else:
                print(f"   ⚠️  Low confidence for '{name}': '{result.new_selector}'")
        return results

    def _fallback_mapping(self, old_selector: str, old_html: str, new_html: str) -> SelectorMatch:
        old_context = self._extract_element_context(old_html, old_selector)
        if not old_context:
            return SelectorMatch(old_selector, "", 0.0, "Original element not found.")
        soup_v2 = BeautifulSoup(new_html, 'html.parser')
        old_text = old_context.get('text_content', '')
        candidates = []
        for elem in soup_v2.find_all(True):
            new_text = re.sub(r'\s+', ' ', elem.get_text(strip=True)[:300])
            score = SequenceMatcher(None, old_text, new_text).ratio() if old_text and new_text else 0
            if score > 0.3:
                candidates.append({'element': elem, 'score': score})
        if not candidates:
            return SelectorMatch(old_selector, "", 0.0, "No similar element found.")
        best_candidate = sorted(candidates, key=lambda x: x['score'], reverse=True)[0]
        if best_candidate['element'].get('data-testid'):
            best_selector = f"[data-testid='{best_candidate['element']['data-testid']}']"
            confidence = best_candidate['score'] * 0.9
        elif best_candidate['element'].get('id'):
            best_selector = f"#{best_candidate['element']['id']}"
            confidence = best_candidate['score'] * 0.8
        else:
            best_selector = best_candidate['element'].name
            confidence = best_candidate['score'] * 0.4
        reasoning = f"Fallback mapping. Similarity: {best_candidate['score']:.2f}."
        return SelectorMatch(old_selector, best_selector, confidence, reasoning)

    def generate_mapping_report(self, results: Dict[str, SelectorMatch]) -> Dict:
        successful = [r for r in results.values() if r.confidence > 0.7]
        failed = [r for r in results.values() if r.confidence <= 0.7]
        return {
            "summary": {
                "total_selectors": len(results),
                "successful_mappings": len(successful),
                "failed_mappings": len(failed),
                "success_rate": len(successful) / len(results) if results else 0
            },
            "details": [vars(r) for r in results.values()]
        }
