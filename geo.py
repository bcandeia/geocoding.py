# coding=utf-8
"""
Script: geo.py
Descrição: Geocodifica uma lista de endereços (texto) em coordenadas
           geográficas (latitude/longitude) usando a Google Geocoding API.
Autor: @bcandeia e @nathaliaolisil
Github: https://github.com/bcandeia

Como usar:
1. Configure sua chave da Google Geocoding API como variável de ambiente:
   Windows (cmd):      set GOOGLE_API_KEY=sua_chave_aqui
   Windows (PowerShell): $env:GOOGLE_API_KEY="sua_chave_aqui"
   Linux/Mac:          export GOOGLE_API_KEY=sua_chave_aqui

2. Crie um arquivo "enderecos.txt" com um endereço por linha.

3. Rode o script:
   python geo.py

O resultado é salvo em "coord_finais.txt".
"""

import os
from time import sleep

from geopy.geocoders import GoogleV3
from geopy.exc import GeocoderTimedOut, GeocoderServiceError

ARQUIVO_ENTRADA = "enderecos.txt"
ARQUIVO_SAIDA = "coord_finais.txt"
TEMPO_ESPERA_SEGUNDOS = 2  # respeita o limite de requisições da API


def geocodificar_enderecos(caminho_entrada: str, caminho_saida: str) -> None:
    """Lê endereços de um arquivo texto, geocodifica cada um via Google
    Geocoding API e grava os resultados (endereço + coordenadas) em um
    arquivo de saída.
    """
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        raise EnvironmentError(
            "Variável de ambiente GOOGLE_API_KEY não encontrada. "
            "Configure sua chave antes de rodar o script (veja o README)."
        )

    geolocator = GoogleV3(api_key=api_key)

    with open(caminho_entrada, "r", encoding="utf-8") as entrada, \
         open(caminho_saida, "w", encoding="utf-8") as saida:

        for linha in entrada:
            endereco = linha.strip()
            if not endereco:
                continue

            sleep(TEMPO_ESPERA_SEGUNDOS)

            try:
                location = geolocator.geocode(endereco, timeout=100)
            except (GeocoderTimedOut, GeocoderServiceError) as erro:
                print(f"Erro ao geocodificar '{endereco}': {erro}")
                saida.write(f"Endereco: {endereco} | Coordenadas: erro na consulta ({erro})\n")
                continue

            if location:
                coordenadas = (location.latitude, location.longitude)
                saida.write(f"Endereco: {endereco} | Coordenadas: {coordenadas}\n")
                print(endereco, "->", coordenadas)
            else:
                saida.write(f"Endereco: {endereco} | Coordenadas: não encontradas\n")
                print(endereco, "-> não encontrado")


if __name__ == "__main__":
    geocodificar_enderecos(ARQUIVO_ENTRADA, ARQUIVO_SAIDA)
