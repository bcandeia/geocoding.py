# coding=utf-8
"""
Script: comparar_geocoding.py
Descrição: Geocodifica o mesmo conjunto de endereços brasileiros usando
           duas abordagens diferentes, para comparação:

           1. Google Geocoding API (geopy) — paga, com limite de requisições,
              exige chave de API.
           2. geocodebr (IPEA) — gratuita, sem limite de consultas, baseada
              em dado público do CNEFE/IBGE, não exige chave.

Autor: @bcandeia
Github: https://github.com/bcandeia

STATUS: rascunho não testado. Escrito a partir da documentação oficial do
geocodebr (PyPI, verificada em 02/10/2026) e do geo.py existente neste
repositório. Primeira execução deve ser feita localmente.

Base de teste: endereços reais de 9 municípios pequenos do Nordeste
(8 na Paraíba + 1 no Piauí, todos com menos de 2.400 habitantes),
obtidos diretamente do CNEFE/IBGE via gerar_base_teste_nordeste.py —
não são endereços inventados.

Como usar:
1. Instale as dependências:
   pip install geopy
   pip install geocodebr[geo]   # o extra "geo" é necessário para retorno
                                 # como GeoDataFrame / uso geoespacial

2. Rode primeiro o gerador da base de teste (gratuito, sem chave):
   python gerar_base_teste_nordeste.py
   (gera enderecos_teste_nordeste.csv)

3. Configure sua chave da Google Geocoding API como variável de ambiente:
   Linux/Mac:           export GOOGLE_API_KEY=sua_chave_aqui
   Windows (PowerShell): $env:GOOGLE_API_KEY="sua_chave_aqui"

   (o geocodebr não precisa de chave nenhuma)

4. Rode a comparação:
   python comparar_geocoding.py

O resultado é impresso no terminal e salvo em "comparacao_resultados.csv".
"""

import os
import time

import polars as pl
from geopy.geocoders import GoogleV3
from geopy.exc import GeocoderTimedOut, GeocoderServiceError

from geocodebr import definir_campos, geocode


# Base de teste real de 9 municípios pequenos do Nordeste, gerada por
# gerar_base_teste_nordeste.py (endereços confirmados no CNEFE/IBGE —
# rode esse script primeiro).
ARQUIVO_BASE_TESTE = "enderecos_teste_nordeste.csv"

_df_base = pl.read_csv(ARQUIVO_BASE_TESTE)

# Formato texto, para a Google Geocoding API (mantém o par endereço+cidade
# alvo juntos, pra conseguir cruzar os dois resultados depois)
_ENDERECOS_COM_CIDADE = [
    (
        f"{row['logradouro']}, {row['localidade']}, {row['municipio']}, "
        f"{row['estado']}, {row['cep']}",
        row["municipio_alvo"],
        row["estado_alvo"],
    )
    for row in _df_base.to_dicts()
]
ENDERECOS_TEXTO = [item[0] for item in _ENDERECOS_COM_CIDADE]

# Formato estruturado, para o geocodebr
# Nota: busca_por_cep() não retorna número de residência (é info em nível
# de CEP, não de domicílio), então o reteste via geocode() aqui usa só
# logradouro/localidade/município/estado.
ENDERECOS_ESTRUTURADOS = _df_base.select(
    pl.col("logradouro"),
    pl.col("localidade"),
    pl.col("municipio"),
    pl.col("estado"),
    pl.col("municipio_alvo"),
    pl.col("estado_alvo"),
)


def geocodificar_google(enderecos_com_cidade: list[tuple]) -> list[dict]:
    """Geocodifica endereços usando a Google Geocoding API (via geopy)."""
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        raise EnvironmentError(
            "Variável de ambiente GOOGLE_API_KEY não encontrada."
        )

    geolocator = GoogleV3(api_key=api_key)
    resultados = []

    for endereco, municipio_alvo, estado_alvo in enderecos_com_cidade:
        time.sleep(2)  # respeita o limite de requisições da API
        base = {
            "fonte": "google",
            "endereco": endereco,
            "municipio_alvo": municipio_alvo,
            "estado_alvo": estado_alvo,
        }
        try:
            location = geolocator.geocode(endereco, timeout=100)
        except (GeocoderTimedOut, GeocoderServiceError) as erro:
            resultados.append({**base, "lat": None, "lon": None, "erro": str(erro)})
            continue

        if location:
            resultados.append({
                **base,
                "lat": location.latitude,
                "lon": location.longitude,
                "erro": None,
            })
        else:
            resultados.append({**base, "lat": None, "lon": None, "erro": "não encontrado"})

    return resultados


def geocodificar_geocodebr(enderecos_estruturados: pl.DataFrame) -> list[dict]:
    """Geocodifica endereços usando o geocodebr (CNEFE/IBGE, gratuito)."""
    campos = definir_campos(
        logradouro="logradouro",
        localidade="localidade",
        municipio="municipio",
        estado="estado",
    )

    # Na primeira execução, baixa os dados do CNEFE para cache local
    # (pode demorar alguns minutos).
    resultado = geocode(
        enderecos=enderecos_estruturados,
        campos_endereco=campos,
        resultado_completo=False,
        verboso=True,
    )

    df = resultado.to_pandas()
    resultados = []
    for _, row in df.iterrows():
        resultados.append({
            "fonte": "geocodebr",
            "endereco": f"{row.get('logradouro')}, "
                        f"{row.get('municipio')}/{row.get('estado')}",
            "municipio_alvo": row.get("municipio_alvo"),
            "estado_alvo": row.get("estado_alvo"),
            "lat": row.get("lat"),
            "lon": row.get("lon"),
            "erro": None if row.get("lat") else row.get("tipo_resultado"),
        })
    return resultados


def main():
    print(f"Base de teste: {len(ENDERECOS_TEXTO)} endereços reais "
          f"em {_df_base['municipio_alvo'].n_unique()} municípios.\n")

    print("Geocodificando via Google Geocoding API (paga, com limite)...")
    resultados_google = geocodificar_google(_ENDERECOS_COM_CIDADE)

    print("\nGeocodificando via geocodebr (gratuita, dado CNEFE/IBGE)...")
    resultados_geocodebr = geocodificar_geocodebr(ENDERECOS_ESTRUTURADOS)

    todos_resultados = resultados_google + resultados_geocodebr
    df_final = pl.DataFrame(todos_resultados)
    df_final.write_csv("comparacao_resultados.csv")

    print("\n=== Resumo por município (quantos endereços cada fonte achou) ===")
    resumo = (
        df_final
        .with_columns((pl.col("lat").is_not_null()).alias("encontrado"))
        .group_by(["municipio_alvo", "estado_alvo", "fonte"])
        .agg(pl.col("encontrado").sum().alias("encontrados"), pl.len().alias("total"))
        .sort(["municipio_alvo", "fonte"])
    )
    print(resumo)

    print("\nResultados completos salvos em comparacao_resultados.csv")


if __name__ == "__main__":
    main()
