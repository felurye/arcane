import httpx
from agno.tools import tool


@tool("search_adverse_veterinary_events")
def search_adverse_veterinary_events(
    medication: str,
    search_type: str = "active_ingredient",
    species: str = "",
    limit: int = 5,
) -> str:
    """Search for adverse veterinary events reported to the FDA for a medication.

    Args:
        medication: Brand name or active ingredient. Ex: "Meloxicam", "Rimadyl", "Amoxicillin".
        search_type: "active_ingredient" or "brand_name". Default: "active_ingredient".
        species: Filter by species. Ex: "Dog", "Cat", "Horse". Empty for all.
        limit: Number of cases (1-10). Default: 5.

    Returns:
        JSON with aggregated statistics (reactions, outcomes, species) and individual FDA cases.
    """
    BASE_URL = "https://api.fda.gov/animalandveterinary/event.json"
    limit = max(1, min(limit, 10))
    field = "drug.brand_name" if search_type == "brand_name" else "drug.active_ingredients.name"

    query = f'{field}:"{medication}"'
    if species:
        query += f'+AND+animal.species:"{species}"'

    resp = httpx.get(BASE_URL, params={"search": query, "limit": str(limit)}, timeout=15)
    return resp.text
