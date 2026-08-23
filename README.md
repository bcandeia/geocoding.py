# O QUE É GEOCODIFICAÇÃO?

📝 Este código acompanha a publicação no LinkedIn:
[Geocodificação de Endereços: a melhor geotecnologia de todos os tempos da última semana](https://www.linkedin.com/pulse/geocodifica%C3%A7%C3%A3o-de-endere%C3%A7os-melhor-geotecnologia-todos-bruna-candeia/)

Geocodificação é o processo de conversão de endereços como (445, Avenida Barao do Triunfo, Varadouro, Joao Pessoa, Paraiba,
58010400) em coordenadas geográficas (Latitude: -7.1170654 e Longitude: -34.887439), os quais podem ser utilizados como
marcadores em um mapa ou para posicionar o mapa, propriamente dito.

O Google possui uma solução de Geocodificação através da API Geocoding, através da qual é possível acessar os servidores da
Google de forma direta por meio de uma solicitação HTTP.

O código aqui desenvolvido é uma solução em Python utilizando a API Geocoding para a conversão dos endereços textuais em
coordenadas geográficas.

## COMO RODAR O CÓDIGO

1. Criar um ambiente virtual (diretório) através do Prompt CMD
   >>>python -m venv <nomedoambientevirtual>

2. Entrar no ambiente virtual recém criado
   >>>C:\>cd <nomedoambientevirtual>

3. Ativar ambiente virtual
   >>>scripts\activate

4. Instalar as dependências
   >>>pip install geopy

5. Obter uma chave de API do Google Geocoding, seguindo o guia oficial:
   https://developers.google.com/maps/documentation/geocoding/get-api-key?hl=pt

6. Configurar a chave como variável de ambiente (nunca coloque a chave direto no código):

   Windows (cmd):
   >>>set GOOGLE_API_KEY=sua_chave_aqui

   Windows (PowerShell):
   >>>$env:GOOGLE_API_KEY="sua_chave_aqui"

   Linux/Mac:
   >>>export GOOGLE_API_KEY=sua_chave_aqui

7. Criar um novo diretório com: código (geo.py) e arquivo de endereços/entrada (enderecos.txt),
   um endereço por linha.
   <novodiretorio>

8. Entrar no novo diretório com o código e o arquivo de entrada
   >>>C:\nomedoambientevirtual>cd novodiretorio

9. Rodar o código
   >>>python geo.py

O resultado é salvo automaticamente em "coord_finais.txt", no mesmo diretório, contendo cada
endereço e suas respectivas coordenadas (ou uma indicação de erro/não encontrado).

## ESTRUTURA DO CÓDIGO

O script está organizado em uma única função, `geocodificar_enderecos()`, responsável por:
- Ler a chave da API a partir da variável de ambiente GOOGLE_API_KEY
- Ler os endereços do arquivo de entrada, linha a linha
- Consultar a Google Geocoding API para cada endereço, respeitando um intervalo entre
  requisições
- Tratar erros de timeout ou falha de serviço sem interromper o processamento dos
  demais endereços
- Gravar os resultados no arquivo de saída

## REFERÊNCIAS

Google Developers. Geocoding API: Get Started. Disponível em:
<https://developers.google.com/maps/documentation/geocoding/start?hl=pt>

Google Developers. Geocoding API: Get an API Key. Disponível em:
<https://developers.google.com/maps/documentation/geocoding/get-api-key?hl=pt>
