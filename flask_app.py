from flask import Flask, request
import telepot
from requests import Session
import json
import urllib3
import pandas as pd

proxy_url = "http://proxy.server:3128"
telepot.api._pools = {
    'default': urllib3.ProxyManager(proxy_url=proxy_url, num_pools=3, maxsize=10, retries=False, timeout=30),
}
telepot.api._onetime_pool_spec = (urllib3.ProxyManager, dict(proxy_url=proxy_url, num_pools=1, maxsize=1, retries=False, timeout=30))

secret = "A_SECRET_NUMBER"
bot = telepot.Bot('YOUR_AUTHORIZATION_TOKEN')
bot.setWebhook("https://YOUR_PYTHONANYWHERE_USERNAME.pythonanywhere.com/{}".format(secret), max_connections=1)


def get_price():
    url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest'
    parameters = {
      'start':'1',
      'limit':'5000',
      'convert':'USD'
    }
    headers = {
      'Accepts': 'application/json',
      'X-CMC_PRO_API_KEY': 'YOUR_coinmarketcap_TOKEN',
    }
    session = Session()
    session.headers.update(headers)
    response = session.get(url, params=parameters)
    data = json.loads(response.text)
    df = pd.DataFrame(data["data"])

    results = {}
    for i in range(50):
        name = df["name"].iloc[i]
        price = df["quote"].iloc[i]["USD"]["price"]
        price = str(round(price, 5)) + ' $'
        results[name] = results.get(name, price)

    return results


def handle(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)
    if content_type == 'text':
        text = msg['text']
        if text == '/start':
            bot.sendMessage(chat_id, 'For getting help, tap on /help')
        elif text == '/help':
            bot.sendMessage(chat_id, 'Hi, Welcome to my bot')
            bot.sendMessage(chat_id, 'In order to get top-fifty cryptocurrency instant prices tap on /first50')
        elif text == '/first50':
            results = get_price()
            r = str(results).replace(',', '\n')
            r = r.replace("'", "")
            r = r.replace('{', '  ')
            r = r.strip('{}')
            bot.sendMessage(chat_id, r)
            

app = Flask(__name__)

@app.route('/{}'.format(secret), methods=["POST"])
def telegram_webhook():
    update = request.get_json()
    if "message" in update:
        handle(update["message"])

    return "OK"
