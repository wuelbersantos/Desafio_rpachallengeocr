from selenium import webdriver #importar selenium
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
import time
import os
import requests
import easyocr
import re
import csv
import pandas as pd



import os
import pandas as pd

def salvar_dados_em_csv(lista_faturas):
    nome_arquivo = "resultado_desafio.csv"
    pasta_destino = "faturas"

    caminho_final = os.path.join(pasta_destino, nome_arquivo)

    try:
        #transforma em list
        if isinstance(lista_faturas, dict):
            lista_faturas = [lista_faturas]


        df = pd.DataFrame(lista_faturas)

        df.to_csv(caminho_final, index=False, encoding="utf-8")

        print(f"\n CSV gerado  {len(lista_faturas)}")
        print(f"Arquivo salvo em: {caminho_final}")
        return True

    except Exception as e:
        print(f"[ERRO] Falha ao salvar o arquivo CSV: {e}")
        return False


def inicializar_navegador():

    chrome_opions= Options()

    chrome_opions.add_argument("--start-maximized")#iniciar com tela maximizada
    chrome_opions.add_argument("--disable-blink-features=AutomationControlled")#evitar bloqueios
    chrome_opions.add_experimental_option("excludeSwitches", ["enable-automation"])#remover cabeçalhos para nao identifcar que é um robo
    chrome_opions.add_experimental_option('useAutomationExtension', False) #nao executar exntesao

    driver = webdriver.Chrome(chrome_opions)

    return driver


def ExtrairDadosFaturas(nome_arquivo, pasta_fatura, id_fatura, due_date):
    caminho_imagem = os.path.join(pasta_fatura, nome_arquivo)

    if not os.path.exists(caminho_imagem):
        print(f"[ERRO] Arquivo {caminho_imagem} não encontrado!")
        return None

    print(f"Iniciando OCR no arquivo: {caminho_imagem}...\n")

    leitor = easyocr.Reader(['en', 'pt'], gpu=False)
    resultado = leitor.readtext(caminho_imagem, detail=0)

    dados_extraidos = {
        "ID": id_fatura,
        "due_date": due_date,
        "company_name": None,
        "invoice_number": None,
        "invoice_date": None,
        "total_due": None
    }

    print("--- TEXTO EXTRAÍDO DA IMAGEM ---")
    for linha in resultado:
        print(linha)
    print("--------------------------------")

    # 1. Nome da Empresa (Se a primeira linha for 'INVOICE', tenta pegar o nome real mais abaixo)
    if len(resultado) > 0:
        primeira_linha = resultado[0].strip()
        if primeira_linha.upper() == "INVOICE" and len(resultado) > 2:
            dados_extraidos["company_name"] = resultado[2].strip() # Pega 'Sit Amet'
        else:
            dados_extraidos["company_name"] = primeira_linha

    # 2. Varre as linhas
    for i, linha in enumerate(resultado):
        linha_limpa = linha.upper().strip()

        # --- CAPTURA INVOICE NUMBER ---
        if "INVOICE #" in linha_limpa:
            numeros = re.findall(r'#\s*(\d+)', linha_limpa)
            if numeros: dados_extraidos["invoice_number"] = numeros[0]
        elif linha_limpa == "INVOICE" and (i + 1) < len(resultado):
            # Se 'INVOICE' estiver sozinho e a próxima linha for só números (temple 2)
            proxima = resultado[i + 1].strip()
            if proxima.isdigit():
                dados_extraidos["invoice_number"] = proxima

        # --- CAPTURA INVOICE DATE ORIGINAL ---
        if "DATE" in linha_limpa and not dados_extraidos["invoice_date"]:
            if ":" in linha and len(linha.split(":")[-1].strip()) > 0:
                dados_extraidos["invoice_date"] = linha.split(":")[-1].strip()
            elif (i + 2) < len(resultado):
                # Caso o mês e o ano estejam nas linhas de baixo (Layout Novo: 'Jun' e '2019')
                mes = resultado[i + 1].strip()
                ano = resultado[i + 2].strip()
                dados_extraidos["invoice_date"] = f"{mes} {ano}"

        # --- CAPTURA TOTAL DUE ---
        if (linha_limpa == "TOTAL" or linha_limpa == "TOTAL:") and (i + 1) < len(resultado):
            valor_candidato = resultado[i + 1].strip()
            # Remove caracteres comuns de erro do OCR mas manter: vírgulas e números
            dados_extraidos["total_due"] = valor_candidato

    print(dados_extraidos)
    print("*" * 50)

    # salvar csv
    salvar_dados_em_csv([dados_extraidos])


def baixar_fatura_local(url_fatura,nome_arquivo,id_fatura,due_date):
    pasta_destino = "faturas"

    if not os.path.exists(pasta_destino):
        os.makedirs(pasta_destino)
        print(f"Pasta '{pasta_destino}' criada com sucesso.")
    else:
        print(f"Pasta '{pasta_destino}' ja disponivel.")

    caminho_completo = os.path.join(pasta_destino, nome_arquivo)

    print(f"Iniciando download de: {url_fatura}")

    #fazer Requisição
    resposta = requests.get(url_fatura, stream=True)

    if resposta.status_code == 200:
        # Grava o arquivo no disco
        with open(caminho_completo, 'wb') as arquivo:
            for bloco in resposta.iter_content(chunk_size=128):
                arquivo.write(bloco)
        print(f"Sucesso! Fatura salva em: {caminho_completo}")

        print("*"*50)
        #chamar Funcao Extrair dados:
        ExtrairDadosFaturas(nome_arquivo,pasta_destino,id_fatura,due_date)

        return caminho_completo
    else:
        print(f"[ERRO] Falha no download. Código : {resposta.status_code}")
        return None


def acessar_rpachallengeocr():
    driver = inicializar_navegador()

    url = "https://rpachallengeocr.azurewebsites.net/"

    try:
        driver.get(url)
        print(f"pagina carregada com sucesso")
        wait = WebDriverWait(driver, 10)
        #esperar objeto apresentar na tela
        tabela_pagina = wait.until(EC.presence_of_element_located((By.ID, "tableSandbox")))
        print("elemento presente em tela")
    except Exception as e:
        print(f"[ERRO] Falha ao acessar a pagina {e}")


    try:
        url_fatura = driver.find_element(By.XPATH,"/html/body/div/div/div[2]/div/div[1]/div[1]/table/tbody/tr[1]/td[4]/a").get_attribute("href")
        print(url_fatura)

    except Exception as e:
        print(print(f"[ERRO] Falha ao Baixar a fatura {e}"))

    nome_arquivo = url_fatura.split("/")[-1]
    #coletar id_fatura
    id_fatura=driver.find_element(By.XPATH,"/html/body/div/div/div[2]/div/div[1]/div[1]/table/tbody/tr[1]/td[2]").text.strip()
    #coletar = due_date
    due_date = driver.find_element(By.XPATH, "/html/body/div/div/div[2]/div/div[1]/div[1]/table/tbody/tr[1]/td[3]").text.strip()



    baixar_fatura_local(url_fatura,nome_arquivo,id_fatura,due_date)


if __name__ == "__main__":
    acessar_rpachallengeocr()

