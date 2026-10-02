# geocoding.py

Geocodificação de endereços com Python — do script original à comparação entre fontes.

📝 Este repositório acompanha a publicação no LinkedIn:
[Geocodificação de Endereços: a melhor geotecnologia de todos os tempos da última semana](https://www.linkedin.com/pulse/geocodifica%C3%A7%C3%A3o-de-endere%C3%A7os-melhor-geotecnologia-todos-bruna-candeia/)


## Estrutura

```
geocoding.py/
├── 1-google-geocoding/
│   └── geo.py                        # geocodifica endereços via Google Geocoding API
│
└── 2-comparacao-google-geocodebr/
    ├── gerar_base_teste_nordeste.py  # monta base de teste com endereços reais do CNEFE/IBGE
    ├── comparar_geocoding.py         # compara Google API vs. geocodebr (IPEA)
    └── dados/
        ├── enderecos_teste_nordeste.csv   # base de teste: 9 municípios do Nordeste
        └── comparacao_resultados.csv      # saída gerada por comparar_geocoding.py
```


## 1. Google Geocoding API (`geo.py`)

Lê um arquivo `enderecos.txt` (um endereço por linha), consulta a Google Geocoding API
e grava as coordenadas em `coord_finais.txt`.

**Dependências:**
```bash
pip install geopy
```

**Como rodar:**
```bash
# Configure a chave como variável de ambiente (nunca coloque no código)
export GOOGLE_API_KEY=sua_chave_aqui          # Linux/Mac
$env:GOOGLE_API_KEY="sua_chave_aqui"          # Windows PowerShell

python geo.py
```


## 2. Comparação: Google API vs. geocodebr

Dois scripts que trabalham em sequência:

### 2.1 Gerar a base de teste

`gerar_base_teste_nordeste.py` consulta o CNEFE/IBGE via
[geocodebr](https://ipea.github.io/geocodebr/) e monta uma base com endereços
**reais** de 9 municípios pequenos do Nordeste (todos com menos de 2.400 habitantes):
Quixaba, Parari, Coxixola, Riacho de Santo Antônio, Areia de Baraúnas, Zabelê,
Curral Velho e São José do Brejo do Cruz (PB), e Miguel Leão (PI).

```bash
pip install geocodebr[geo]
python gerar_base_teste_nordeste.py
# gera: dados/enderecos_teste_nordeste.csv
```

### 2.2 Comparar as duas fontes

`comparar_geocoding.py` geocodifica os mesmos 135 endereços pelas duas abordagens:

| | Google Geocoding API | geocodebr |
|---|---|---|
| Custo | Paga (acima da cota gratuita) | Gratuita, sem limite |
| Chave de API | Obrigatória | Não precisa |
| Fonte | Base comercial do Google | CNEFE/IBGE (dado público) |
| Cobertura | Global | Brasil |

```bash
pip install geopy geocodebr[geo] polars
$env:GOOGLE_API_KEY="sua_chave_aqui"
python comparar_geocoding.py
# gera: dados/comparacao_resultados.csv
```

### Resultados (135 endereços reais)

As duas fontes encontraram **100% dos endereços**. O achado relevante é outro:
elas frequentemente discordam de *onde* o endereço fica.

| Métrica | Valor |
|---|---|
| Diferença mediana entre as fontes | 2.554 m |
| Diferença média | 4.108 m |
| Pares a menos de 100 m | 13% |
| Pares a mais de 5 km | 27% |

O caso mais extremo: para um endereço em Coxixola (PB), a Google retornou
um ponto **98 km fora dos limites do município**. O geocodebr manteve o
resultado dentro do município.

> Não há um gabarito independente para dizer qual fonte está certa em cada caso —
> só sabemos que elas discordam, e com que frequência. A exceção é Coxixola,
> onde a distância por si só já descarta o resultado do Google como plausível.


## Dependências

```bash
pip install -r requirements.txt
```

Ou individualmente:

```bash
pip install geopy              # módulo 1
pip install geocodebr[geo] polars  # módulo 2
```


## Referências

- Google Developers. [Geocoding API Overview](https://developers.google.com/maps/documentation/geocoding/start?hl=pt)
- Pereira, R. H. M. et al. [geocodebr](https://ipea.github.io/geocodebr/) — IPEA, 2026
- Araújo, T. L; Candeia, B. A; et al. *Geocodificação de endereços e espacialização de dados através do módulo Geopy/Python e do Quantum GIS*. 2017.

---

Autora: [@bcandeia](https://github.com/bcandeia)
