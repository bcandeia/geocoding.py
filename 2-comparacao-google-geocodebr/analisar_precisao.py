# coding=utf-8
"""
Script: analisar_precisao.py
Descrição: Terceiro passo do pipeline. Lê o CSV gerado por
           comparar_geocoding.py e calcula, para cada endereço, a
           distância real (fórmula de Haversine) entre a coordenada
           devolvida pela Google Geocoding API e pela geocodebr.

           Gera:
           - dados/precisao_resultados.csv — uma linha por endereço, com
             a distância em metros entre as duas fontes
           - um resumo por município impresso no terminal
           - assets/diferenca_por_municipio.png — o gráfico de barras
             usado no README

Pipeline completo:
    1. gerar_base_teste_nordeste.py   -> dados/enderecos_teste_nordeste.csv
    2. comparar_geocoding.py          -> dados/comparacao_resultados.csv
    3. analisar_precisao.py (este)    -> dados/precisao_resultados.csv
                                       -> assets/diferenca_por_municipio.png

Autor: @bcandeia
STATUS: rascunho não testado. Primeira execução deve ser feita localmente,
depois de rodar os passos 1 e 2.

Como usar:
    pip install pandas matplotlib
    python analisar_precisao.py
"""

from math import radians, sin, cos, sqrt, atan2
from pathlib import Path

import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ARQUIVO_ENTRADA = Path("dados/comparacao_resultados.csv")
ARQUIVO_SAIDA_CSV = Path("dados/precisao_resultados.csv")
ARQUIVO_SAIDA_GRAFICO = Path("assets/diferenca_por_municipio.png")


def haversine_metros(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Distância em metros entre dois pontos geográficos (fórmula de Haversine)."""
    R = 6371000  # raio médio da Terra, em metros
    phi1, phi2 = radians(lat1), radians(lat2)
    dphi = radians(lat2 - lat1)
    dlambda = radians(lon2 - lon1)
    a = sin(dphi / 2) ** 2 + cos(phi1) * cos(phi2) * sin(dlambda / 2) ** 2
    return 2 * R * atan2(sqrt(a), sqrt(1 - a))


def parear_por_municipio(df: pd.DataFrame) -> pd.DataFrame:
    """Casa cada endereço do Google com o endereço correspondente do
    geocodebr, por município e ordem de aparição (os dois scripts
    geram os endereços na mesma ordem a partir da mesma base de teste).
    """
    pares = []
    for municipio in df["municipio_alvo"].unique():
        subset = df[df["municipio_alvo"] == municipio]
        google = subset[subset["fonte"] == "google"].reset_index(drop=True)
        geocodebr = subset[subset["fonte"] == "geocodebr"].reset_index(drop=True)

        n = min(len(google), len(geocodebr))
        for i in range(n):
            g = google.iloc[i]
            b = geocodebr.iloc[i]
            if pd.isna(g["lat"]) or pd.isna(b["lat"]):
                continue
            distancia = haversine_metros(g["lat"], g["lon"], b["lat"], b["lon"])
            pares.append({
                "municipio_alvo": municipio,
                "estado_alvo": g["estado_alvo"],
                "endereco_google": g["endereco"],
                "endereco_geocodebr": b["endereco"],
                "lat_google": g["lat"],
                "lon_google": g["lon"],
                "lat_geocodebr": b["lat"],
                "lon_geocodebr": b["lon"],
                "distancia_metros": distancia,
            })
    return pd.DataFrame(pares)


def gerar_grafico(resumo: pd.DataFrame, caminho: Path) -> None:
    """Gera o gráfico de barras com a diferença média por município,
    destacando em vermelho o município com maior discrepância.
    """
    resumo_ordenado = resumo.sort_values("distancia_media_m")
    cores = ["#2563eb"] * len(resumo_ordenado)
    cores[-1] = "#dc2626"  # destaca o pior caso

    fig, ax = plt.subplots(figsize=(9, 5))
    bars = ax.bar(
        resumo_ordenado["municipio_alvo"],
        resumo_ordenado["distancia_media_m"],
        color=cores,
    )
    for bar, valor in zip(bars, resumo_ordenado["distancia_media_m"]):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            valor + resumo_ordenado["distancia_media_m"].max() * 0.015,
            f"{valor:,.0f}".replace(",", "."),
            ha="center", va="bottom", fontsize=9,
        )

    ax.set_ylabel("Diferença média entre as fontes (metros)")
    ax.set_title("Google Geocoding API vs. geocodebr — diferença de coordenadas por município")
    ax.spines[["top", "right"]].set_visible(False)
    plt.xticks(fontsize=8.5, rotation=15, ha="right")
    plt.tight_layout()

    caminho.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(caminho, dpi=150)
    plt.close(fig)


def main():
    if not ARQUIVO_ENTRADA.exists():
        raise FileNotFoundError(
            f"{ARQUIVO_ENTRADA} não encontrado. Rode gerar_base_teste_nordeste.py "
            f"e comparar_geocoding.py primeiro."
        )

    df = pd.read_csv(ARQUIVO_ENTRADA)
    pares = parear_por_municipio(df)

    if pares.empty:
        print("Nenhum par válido encontrado (verifique se as duas fontes "
              "retornaram coordenadas para os mesmos endereços).")
        return

    ARQUIVO_SAIDA_CSV.parent.mkdir(parents=True, exist_ok=True)
    pares.to_csv(ARQUIVO_SAIDA_CSV, index=False)

    resumo = (
        pares.groupby(["municipio_alvo", "estado_alvo"])["distancia_metros"]
        .agg(distancia_media_m="mean", distancia_mediana_m="median",
             distancia_max_m="max", n="count")
        .reset_index()
        .sort_values("distancia_media_m")
    )

    print("=== Resumo por município (distância entre as duas fontes) ===")
    print(resumo.to_string(index=False))

    geral = pares["distancia_metros"]
    print(f"\n=== Geral ({len(pares)} pares) ===")
    print(f"Mediana: {geral.median():,.0f} m")
    print(f"Média: {geral.mean():,.0f} m")
    for limite in (100, 500, 1000, 5000):
        pct = (geral <= limite).mean() * 100
        print(f"<= {limite} m: {pct:.0f}%")
    pct_acima = (geral > 5000).mean() * 100
    print(f"> 5000 m: {pct_acima:.0f}%")

    gerar_grafico(resumo, ARQUIVO_SAIDA_GRAFICO)
    print(f"\nGráfico salvo em {ARQUIVO_SAIDA_GRAFICO}")
    print(f"Dados completos salvos em {ARQUIVO_SAIDA_CSV}")


if __name__ == "__main__":
    main()
