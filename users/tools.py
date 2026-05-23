import httpx
from agno.tools import tool


@tool("buscar_eventos_adversos_veterinarios")
def buscar_eventos_adversos_veterinarios(
    medicamento: str,
    tipo_busca: str = "principio_ativo",
    especie: str = "",
    limite: int = 5,
) -> str:
    """Busca eventos adversos veterinários reportados ao FDA para um medicamento.

    Args:
        medicamento: Nome comercial ou princípio ativo. Ex: "Meloxicam", "Rimadyl", "Amoxicillin".
        tipo_busca: "principio_ativo" ou "nome_comercial". Padrão: "principio_ativo".
        especie: Filtrar por espécie. Ex: "Dog", "Cat", "Horse". Vazio para todas.
        limite: Quantidade de casos (1-10). Padrão: 5.

    Returns:
        JSON com estatísticas agregadas (reações, desfechos, espécies) e casos individuais do FDA.
    """
    BASE_URL = "https://api.fda.gov/animalandveterinary/event.json"
    limite = max(1, min(limite, 10))
    campo = "drug.brand_name" if tipo_busca == "nome_comercial" else "drug.active_ingredients.name"

    query = f'{campo}:"{medicamento}"'
    if especie:
        query += f'+AND+animal.species:"{especie}"'

    resp = httpx.get(BASE_URL, params={"search": query, "limit": str(limite)}, timeout=15)
    return resp.text
