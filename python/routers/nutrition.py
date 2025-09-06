from __future__ import annotations
from typing import Optional, Dict, Any
import os, httpx

FDC_API_KEY = os.getenv("FDC_API_KEY", "")

def _from_off(name: str) -> Optional[Dict[str, Any]]:
    url = ("https://world.openfoodfacts.org/cgi/search.pl"
           f"?search_terms={name}&search_simple=1&action=process&json=1&page_size=1"
           "&fields=product_name,nutriments")
    try:
        r = httpx.get(url, timeout=10)
        r.raise_for_status()
        data = r.json()
        prods = data.get("products") or []
        if not prods: return None
        p = prods[0]; nutr = p.get("nutriments") or {}
        return {
            "source": "openfoodfacts",
            "name": p.get("product_name") or name,
            "energy_kcal": nutr.get("energy-kcal_100g") or nutr.get("energy-kcal_serving"),
            "protein_g":   nutr.get("proteins_100g")   or nutr.get("proteins_serving"),
            "fat_g":       nutr.get("fat_100g")        or nutr.get("fat_serving"),
            "carbs_g":     nutr.get("carbohydrates_100g") or nutr.get("carbohydrates_serving"),
            "raw": p,
        }
    except Exception:
        return None

def _from_fdc(name: str) -> Optional[Dict[str, Any]]:
    if not FDC_API_KEY:
        return None
    url = f"https://api.nal.usda.gov/fdc/v1/foods/search?query={name}&pageSize=1&api_key={FDC_API_KEY}"
    try:
        r = httpx.get(url, timeout=10)
        r.raise_for_status()
        js = r.json()
        foods = js.get("foods") or []
        if not foods: return None
        f = foods[0]
        def pick(prefix: str):
            for n in f.get("foodNutrients", []) or []:
                nm = (n.get("nutrientName") or "").lower()
                if prefix in nm:
                    v = n.get("value")
                    if v is not None:
                        return float(v)
            return None
        return {
            "source": "usda_fdc",
            "name": f.get("description") or name,
            "energy_kcal": pick("energy"),
            "protein_g":   pick("protein"),
            "fat_g":       pick("fat"),
            "carbs_g":     pick("carbohyd"),
            "raw": f,
        }
    except Exception:
        return None

def fetch_nutrition(food_name: str) -> Optional[Dict[str, Any]]:
    data = _from_fdc(food_name)
    if data: return data
    return _from_off(food_name)
