# imports
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.devtools.v135.debugger import pause
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
# from urllib.parse import urlparse
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
from configs.xpath_options import xpath_options_dict
import logging

#Função para iniciar o webdriver
# inicializa o driver como None para evitar erros de escopo



# Configuração do logging
logging.basicConfig(
    level=logging.INFO,
    format=r"%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("logsscraper.log", encoding="utf-8"),
        logging.StreamHandler()  # exibe no terminal também
    ]
)


# TODO: refatorar esse trecho de código para o arquivo utils.py

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# RAW_DIR
RAW_DIR = os.path.join(BASE_DIR, "data", "raw")
CSV_PATH = os.path.join(RAW_DIR, "game_data.csv")

# LOGS_DIR
LOG_DIR = os.path.join(BASE_DIR, "logs")
os.makedirs(LOG_DIR, exist_ok=True)

# Caminho completo para o arquivo de log
LOG_PATH = os.path.join(LOG_DIR, "scraper.log")

# Inicializa o navegador com o driver atualizado automaticamente
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

url = "https://gol.gg/tournament/tournament-matchlist/LTA%20South%202025%20Split%202/"

driver.get(url)
driver.maximize_window()
driver.implicitly_wait(2)

num_partida = driver.find_element(By.XPATH, '/html/body/div/main/div[2]/div/div[3]/div/section/div/div/table/tbody/tr[1]/td[1]/a')
num_partida.click()

# Após clicar no jogo e esperar o carregamento
current_url = driver.current_url
match_id = current_url.split("/")[5]


# clica em um dos games da partida
game = driver.find_element(By.XPATH, '//*[@id="gameMenuToggler"]/ul/li[2]')
game_number = game.text
game_number = game_number.lower().replace(" ", "_")
game_uid = f"{match_id}_{game_number}"
game.click()

def get_game_time ():
    """Função para obter o tempo do jogo."""

    xpath_options = xpath_options_dict.get("game_time", []) #xpath_options_dict é um dicionário que contém as opções de XPath para localizar o tempo do jogo

    for xpath in xpath_options: # percorre as opções de XPath
        try:
            element = driver.find_element(By.XPATH, xpath)
            game_time = element.text.strip()
            if game_time:
                return game_time
        except NoSuchElementException:
            logging.error(f"[game_time] XPath não encontrado: {xpath}")
            raise
        except Exception as e:
            logging.error(f"[game_time] Erro ao buscar o tempo do jogo: {e}")
            raise


#função para coletar a data do jogo
def get_game_date():
    """Função para obter a data do jogo"""

    xpath_opitons = xpath_options_dict.get("game_date", []) # obtém as opções de XPath para a data do jogo
    for xpath in xpath_opitons: # percorre as opções de XPath
        try:
            element = driver.find_element(By.XPATH, xpath) # tenta encontrar o elemento pelo XPath
            game_date = element.text.strip() # obtém o texto do elemento e remove espaços em branco
            if game_date: # se o texto não estiver vazio
                game_date = game_date.split(' ', 1)
                game_week = game_date[1]
                game_week = game_week.strip('()')
                game_date = game_date[0]

                return game_date, game_week # retorna a data do jogo
        except NoSuchElementException:
            logging.error(f"[game_date] XPath não encontrado: {xpath}")
            raise
        except Exception as e:
            logging.error(f"[game_date] Erro ao buscar a data do jogo: {e}")
            raise
# Obtém a data do jogo

def get_gold_red_side():
    """Função para obter o ouro do lado vermelho."""

    xpath_options= xpath_options_dict.get("team_gold_red_side", [])
    for xpath in xpath_options:
        try:
            wait = WebDriverWait(driver, 5)
            element = wait.until(EC.presence_of_element_located((By.XPATH, xpath))) # espera até que o elemento esteja presente na página
            gold_red_side = element.text.strip()

            if gold_red_side: # se o texto não estiver vazio
                gold_red_side = gold_red_side.replace(',', '')
                print(f"[DEBUG - GOLD RED SIDE] {gold_red_side}")
                return gold_red_side
        except NoSuchElementException:
            logging.error(f"[gold_red_side] XPath não encontrado: {xpath}")
            raise
        except Exception as e:
            logging.error(f"[gold_red_side] Erro ao buscar o ouro do lado vermelho: {e}")
            raise

def scrape_game_data():
    """Função principal para coletar os dados do jogo."""

    game_time = get_game_time()
    game_date, game_week = get_game_date()
    gold_red_side = get_gold_red_side()

    # TODO: refatorar para adicionar os headers caso não existam
    data = pd.DataFrame(columns=['game_uid', 'game_time','game_date','game_week'], # cria um DataFrame com as colunas especificadas
                        data=[[game_uid, game_time, game_date, game_week]]) # adiciona os dados coletados ao DataFrame

    data.to_csv(CSV_PATH, mode='a', header=not os.path.exists(CSV_PATH), index=False, encoding='utf-8') # escreve os dados no CSV

    with open(CSV_PATH, 'r', encoding='utf-8') as file: # lê o arquivo CSV
        last_line = file.readlines()[-1].strip()

    logging.info(f"[DEBUG - ÚLTIMA LINHA CSV] {last_line}")



scrape_game_data()
# time.sleep(5)


