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

def get_element_text(field_name, driver, xpath_dict):

    xpath_options = xpath_dict.get(field_name, [])

    for xpath in xpath_options:
        try:
            element = driver.find_element(By.XPATH, xpath)
            value = element.text.strip()
            if value:
                logging.info(f"[{field_name}] Valor encontrado: {value}")
                return value
        except NoSuchElementException:
            logging.warning(f"[{field_name}] XPath não encontrado: {xpath}")
        except Exception as e:
            logging.error(f"[{field_name}] Erro ao buscar o valor: {e}")
            raise


#função para coletar a data do jogo
def get_game_date(driver, xpath_options_dict):
    """
    Função que obtém a data e a semana do jogo,
    reutilizando a função genérica de extração.
    """
    try:
        raw_text = get_element_text("game_date", driver, xpath_options_dict)
        # Exemplo de retorno: "2025-05-18 (WEEK7)"
        game_date, game_week = raw_text.split(' ', 1)
        game_week = game_week.strip("()")
        return game_date, game_week

    except ValueError as e:
        logging.error(f"[game_date] Erro ao dividir a data e semana: {e}")
        raise
    except Exception as e:
        logging.error(f"[game_date] Erro inesperado ao buscar a data do jogo: {e}")
        raise


def scrape_game_data():
    """Função principal para coletar os dados do jogo em formato long."""

    game_time = get_element_text("game_time", driver, xpath_options_dict)
    game_date, game_week = get_game_date(driver, xpath_options_dict)
    gold_red_side = get_element_text("team_gold_red_side", driver, xpath_options_dict)
    gold_blue_side = get_element_text("team_gold_blue_side", driver, xpath_options_dict)
    red_side_kills = get_element_text("team_red_kills", driver, xpath_options_dict)
    blue_side_kills = get_element_text("team_blue_kills", driver, xpath_options_dict)

    # Dados em formato long: duas linhas, uma para cada time
    data = pd.DataFrame([
        {
            "game_uid": game_uid,
            "game_date": game_date,
            "game_week": game_week,
            "game_time": game_time,
            "team": "RED",
            "kills": red_side_kills,
            "gold": gold_red_side,
        },
        {
            "game_uid": game_uid,
            "game_date": game_date,
            "game_week": game_week,
            "game_time": game_time,
            "team": "BLUE",
            "kills": blue_side_kills,
            "gold": gold_blue_side,
        }
    ])

    data.to_csv(CSV_PATH, mode='a', header=not os.path.exists(CSV_PATH), index=False, encoding='utf-8')

    with open(CSV_PATH, 'r', encoding='utf-8') as file:
        last_line = file.readlines()[-1].strip()

    logging.info(f"[DEBUG - ÚLTIMA LINHA CSV] {last_line}")


scrape_game_data()
# time.sleep(5)


