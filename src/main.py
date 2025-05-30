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
import pandas as pd
from configs.xpath_options import xpath_options_dict
import logging

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

    xpath_options = xpath_options_dict.get("game_time", [])

    for xpath in xpath_options:
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


def scrape_game_data():
    """Função principal para coletar os dados do jogo."""

    game_time = get_game_time()

    data = pd.DataFrame(columns=['game_uid', 'game_time'],
                        data=[[game_uid, game_time]])

    data.to_csv(CSV_PATH, mode='a', header=not os.path.exists(CSV_PATH), index=False, encoding='utf-8')

    with open(CSV_PATH, 'r', encoding='utf-8') as file:
        last_line = file.readlines()[-1].strip()

    logging.info(f"[DEBUG - ÚLTIMA LINHA CSV] {last_line}")


scrape_game_data()
# time.sleep(5)