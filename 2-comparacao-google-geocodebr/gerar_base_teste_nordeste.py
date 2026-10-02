# coding=utf-8
"""
Script: gerar_base_teste_nordeste.py
Descrição: Constrói uma base de teste com endereços REAIS de vários
           municípios pequenos do Nordeste, consultando diretamente o
           CNEFE (IBGE) via busca_por_cep() do geocodebr.

           Substitui gerar_base_teste_quixaba.py (versão de uma cidade só)
           por uma versão que varre várias cidades pequenas, pensando em
           cobertura de pequenos municípios de forma mais ampla — não só
           um caso isolado.

Municípios incluídos (todos com confirmação de faixa de CEP via
cepsbrasil.com.br, nenhum nome de rua foi inventado):

    Quixaba (PB)                   - 58733-000 a 58733-999 (~1.800 hab.)
    Parari (PB)                    - 58575-000 a 58579-999 (~1.750 hab.,
                                      menos populoso da Paraíba)
    Coxixola (PB)                  - 58588-000 a 58589-999 (~1.880 hab.)
    Riacho de Santo Antônio (PB)   - 58465-000 a 58469-999 (~2.040 hab.)
    Areia de Baraúnas (PB)         - 58732-000 a 58732-999 (~2.040 hab.)
    Zabelê (PB)                    - 58515-000 a 58519-999 (~2.310 hab.)
    Curral Velho (PB)              - 58990-000 a 58992-999 (~2.330 hab.)
    São José do Brejo do Cruz (PB) - 58893-000 a 58894-999 (~1.750 hab.)
    Miguel Leão (PI)               - 64445-000 a 64449-999 (~1.350 hab.,
                                      menos populoso do Piauí)

Autor: @bcandeia
STATUS: rascunho não testado. Primeira execução deve ser feita localmente.

Como usar:
1. pip install geocodebr[geo]
2. python gerar_base_teste_nordeste.py

Gera "enderecos_teste_nordeste.csv" com os endereços reais encontrados em
cada município (até AMOSTRA_POR_MUNICIPIO cada), e imprime um resumo por
cidade no terminal.
"""

import polars as pl
from geocodebr import busca_por_cep

MUNICIPIOS = [
    {"nome": "Quixaba", "estado": "PB", "cep_inicio": "58733-000", "cep_fim": "58733-999"},
    {"nome": "Parari", "estado": "PB", "cep_inicio": "58575-000", "cep_fim": "58579-999"},
    {"nome": "Coxixola", "estado": "PB", "cep_inicio": "58588-000", "cep_fim": "58589-999"},
    {"nome": "Riacho de Santo Antônio", "estado": "PB", "cep_inicio": "58465-000", "cep_fim": "58469-999"},
    {"nome": "Areia de Baraúnas", "estado": "PB", "cep_inicio": "58732-000", "cep_fim": "58732-999"},
    {"nome": "Zabelê", "estado": "PB", "cep_inicio": "58515-000", "cep_fim": "58519-999"},
    {"nome": "Curral Velho", "estado": "PB", "cep_inicio": "58990-000", "cep_fim": "58992-999"},
    {"nome": "São José do Brejo do Cruz", "estado": "PB", "cep_inicio": "58893-000", "cep_fim": "58894-999"},
    {"nome": "Miguel Leão", "estado": "PI", "cep_inicio": "64445-000", "cep_fim": "64449-999"},
]

# Amostra final por município, para o teste comparativo com a Google.
# 9 municípios x 15 = no máximo 135 requisições à Google — ~1,4% do
# limite gratuito mensal (10.000/mês), mesmo rodando o teste várias vezes.
AMOSTRA_POR_MUNICIPIO = 15


def _cep_para_int(cep: str) -> int:
    """Converte '58733-000' em 58733000 (inteiro, sem hífen)."""
    return int(cep.replace("-", ""))


def _int_para_cep(numero: int) -> str:
    """Converte 58733000 de volta em '58733-000'."""
    texto = f"{numero:08d}"
    return f"{texto[:5]}-{texto[5:]}"


def gerar_candidatos(municipio: dict) -> list[str]:
    inicio = _cep_para_int(municipio["cep_inicio"])
    fim = _cep_para_int(municipio["cep_fim"])
    return [_int_para_cep(n) for n in range(inicio, fim + 1)]


def main():
    todas_amostras = []

    for municipio in MUNICIPIOS:
        candidatos = gerar_candidatos(municipio)
        print(
            f"\n{municipio['nome']}-{municipio['estado']}: consultando "
            f"{len(candidatos)} CEPs candidatos no CNEFE..."
        )

        resultado = busca_por_cep(cep=candidatos, verboso=False)
        df = resultado.to_pandas()
        df_validos = df.dropna(subset=["lat", "lon"])

        print(
            f"  -> {len(df_validos)} CEPs reais encontrados "
            f"de {len(candidatos)} candidatos"
        )

        if len(df_validos) == 0:
            print(
                f"  Nenhum endereço encontrado para {municipio['nome']}. "
                f"Confira a grafia do município (acentos podem variar) "
                f"na base do CNEFE."
            )
            continue

        amostra = df_validos.sample(
            n=min(AMOSTRA_POR_MUNICIPIO, len(df_validos)),
            random_state=42,
        )
        amostra = amostra.assign(
            municipio_alvo=municipio["nome"],
            estado_alvo=municipio["estado"],
        )
        todas_amostras.append(amostra)

    if not todas_amostras:
        print("\nNenhum endereço encontrado em nenhum município. Confira a conexão e os nomes.")
        return

    base_final = pl.concat(
        [pl.from_pandas(df) for df in todas_amostras]
    )
    base_final.write_csv("enderecos_teste_nordeste.csv")

    print(
        f"\n{len(base_final)} endereços reais salvos em "
        f"enderecos_teste_nordeste.csv, cobrindo "
        f"{len(todas_amostras)} municípios."
    )
    print(
        base_final.group_by(["municipio_alvo", "estado_alvo"])
        .len()
        .sort("municipio_alvo")
    )


if __name__ == "__main__":
    main()
