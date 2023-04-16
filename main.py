import requests
from datetime import datetime

from bs4 import BeautifulSoup
from tabula import read_pdf
import pandas

import os
import telebot

API_KEY = os.getenv('RUFSC_BOT_TOKEN')
CHANNEL_ID = os.getenv("CHANNEL_ID")
bot = telebot.TeleBot(token=API_KEY)

WEEK_DAY = ['SEGUNDA', 'TERÇA', 'QUARTA', 'QUINTA', 'SEXTA', 'SÁBADO', 'DOMINGO']
TODAY = datetime.today().date()
URL = "https://restaurante.joinville.ufsc.br/cardapio-da-semana/"


def prettyfi_menu_message(menu: list) -> str:
    if menu is not None:
        menu_message = f"CARDÁPIO RU UFSC CTJ \n" \
                       f"{WEEK_DAY[TODAY.weekday()]}  {menu[0]}\n\n"
        for item in menu:
            if item != menu[0]:
                menu_message += f"      {item}\n"
        menu_message += "\n*Cardápio sujeito a alterações."
    else:
        menu_message = f"Cardápio para o dia {TODAY.strftime('%d/%m/%Y')} não disponível"
    return menu_message


def webscraping(url: str) -> list:
    response = requests.get(url=url)
    html_doc = response.text
    soup = BeautifulSoup(html_doc, 'html.parser')
    menu_list = soup.select("p a")
    return menu_list


def pdf_to_dataframe(link: str) -> pandas.DataFrame:
    table = read_pdf(link, pages=[1], output_format="dataframe")
    df = table[0]
    df.dropna(inplace=True, how='all')
    return df


def search_day(df_menu: pandas.DataFrame) -> list:
    for day in range(7):
        str_date = df_menu.iloc[0, day]
        date = datetime.strptime(str_date, '%d/%m/%Y').date()
        if TODAY == date:
            menu = [str(item).replace('\r', ' ') for item in df_menu.iloc[:, day]]
            return menu


def send_menu(menu_message: str):
    bot.send_message(chat_id=CHANNEL_ID, text=menu_message)



menus = webscraping(URL)
while menus:
    last_item = menus.pop()
    link_cardapio = last_item.get_attribute_list("href")[0]
    menu_msg = prettyfi_menu_message(search_day(pdf_to_dataframe(link_cardapio)))
    send_menu(menu_msg)



