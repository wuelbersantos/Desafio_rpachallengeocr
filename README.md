# Desafio RPA Challenge OCR 🤖📄

Este projeto é uma automação desenvolvida em Python para resolver o desafio de OCR do RPA Challenge. O robô combina a automação web com a extração inteligente de dados de documentos digitalizados.

## 🚀 Funcionalidades

* **Automação Web (Selenium):** Navega pela plataforma do desafio, interage com elementos dinâmicos e realiza o download das faturas.
* **Extração de Dados (EasyOCR & Regex):** Realiza a leitura óptica dos caracteres (OCR) das imagens baixadas e utiliza expressões regulares flexíveis para capturar campos dinâmicos mesmo em diferentes layouts de faturas.
* **Manipulação de Dados (Pandas):** Consolida as informações capturadas em uma lista estruturada e exporta os resultados finais em um arquivo CSV limpo e organizado.

## 🛠️ Tecnologias Utilizadas

* [Python]
* [Selenium]
* [EasyOCR]
* [Pandas]
* [Regex (re)

## 📁 Estrutura do Projeto

* `main.py`: Script principal contendo o fluxo de navegação e extração.
* `faturas/`: Pasta gerada automaticamente onde as imagens baixadas e o relatório `resultado_desafio.csv` são salvos.
