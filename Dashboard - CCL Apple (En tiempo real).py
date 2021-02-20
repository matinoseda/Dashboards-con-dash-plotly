import websocket
import time
import threading
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
from dash.dependencies import Output, Input
from collections import deque
import json
import re
import requests

x = deque(maxlen=20)
x.append(1)
y = deque(maxlen=20)
y.append(1)

AAPL_BA = 1
AAPL = 1

def ws_cedears():
    def StringBetween(text, left, right):
        return re.search(left + '(.*?)' + right, text).group(1)

    username = input("Usuario Talaris: ")
    password = input("Contraseña Talaris: ")

    url = "https://api.primary.com.ar/rest/users/login"
    headers = {
        "Host": "api.primary.com.ar",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0",
        "Accept": "*/*",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "deflate",
        "Referer": "https://web.talaris.com.ar/",
        "DNT": "1",
        "Connection": "keep-alive",
        "Content-Type": "application/json",
        "Cache-control": "no-cache",
        "Origin": "https://web.talaris.com.ar",
        "Pragma": "no-cache"
    }
    data = json.dumps({"username": username, "password": password, "brokerId": 407})  # 407 es ECO, cambiar si se trata de otro

    response = requests.post(url=url, headers=headers, data=data)

    status = response.status_code
    if status != 200:
        print("Error, Etapa I")
        quit()

    respuesta = json.loads(response.text)

    if respuesta["message"] != "User is Authenticated.":
        print("usuario y/o contrasenia erroneos")
        quit()

    {
        "status": "OK",
        "message": "User is Authenticated."
    }

    text = response.headers['Set-Cookie']
    cookie = StringBetween(text, "", ";")

    send = json.dumps({"type": "smd", "level": 1,  # Acá se vé que se pide en el websocket
                       "entries": ["BI", "OF", "LA", "OP", "CL", "SE", "OI", "LO", "HI", "IV", "TV", "EV", "NV"],
                       "depth": 1, "products": [{"symbol": "MERV - XMEV - AAPL - 48hs", "marketId": "ROFX"}]})#productos})

    def on_message(ws, message):
        global AAPL_BA
        dict_message = json.loads(message)
        try:
            AAPL_BA = float(dict_message["marketData"]["OF"][0]["price"])
        except:
            print("Error en el ws de cedears!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!:\n",dict_message)
        print("Nuevo valor de ---- CEDEAR de AAPL: ", AAPL_BA, "     Hora: ", time.strftime('%H:%M:%S',
                                                                            time.gmtime(((dict_message["timestamp"])-10800000) / 1000.)))
                                                            #hora = time.strftime('%m/%d/%Y %H:%M:%S', time.gmtime
                                                                #((dict_message["data"][-1]["t"]-10800000) / 1000.))#dict_message["data"][-1]["t"])

    def on_error(ws, error):
        print("Error en ws de cedears: " + error)
    def on_open(ws):
        print("CONNECTED TO PYROFEX")
        ws.send(send)
    def on_close(ws):
        print("DISCONNECTED FROM PYROFEX")

    host = "wss://api.primary.com.ar/"
    #websocket.enableTrace(True)     #Si está en True, imprime por pantalla el trazado de la conexión ws
    ws = websocket.WebSocketApp(host,on_message=on_message,on_error=on_error,on_close=on_close,on_open=on_open,cookie=cookie)
    ws.run_forever()

def ws_acciones():
    def on_message(ws, message):
        global AAPL
        dict_message = json.loads(message)
        try:
            if dict_message["data"][-1]["s"] == "AAPL":
                AAPL = dict_message["data"][-1]["p"]
        except:
            print("Error en el ws de acciones!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!:\n",dict_message)
        print("Nuevo valor de ---- ACCION de AAPL: ", AAPL, "     Hora: ", time.strftime('%H:%M:%S',
                                                            time.gmtime(((dict_message["data"][-1]["t"])-10800000) / 1000.)))
    def on_error(ws, error):
        print("Error en ws de acciones", error)
    def on_close(ws):
        print("DISCONNECTED FROM FINNHUB")
    def on_open(ws):
        ws.send('{"type":"subscribe","symbol":"AAPL"}')
        print("CONNECTED TO FINNHUB")

    #websocket.enableTrace(True)
    ws = websocket.WebSocketApp("wss://ws.finnhub.io?token=vamoboquita2008",on_message = on_message,on_error = on_error,on_close = on_close)
    ws.on_open = on_open
    ws.run_forever()

def pagina_web():
    app = dash.Dash()
    app.title = "CCL de AAPL"

    app.layout = html.Div([
    html.H1("CCL de AAPL - En Tiempo Real"),
    html.Div(
        dcc.Graph(id="id_grafico",figure=go.Figure(layout_yaxis_range=[26,28]))),
    html.Div(
        dcc.Interval(id='update',interval=1000,n_intervals=1)),
    ])


    @app.callback(Output('id_grafico', 'figure'),[Input('update', 'n_intervals')])
    def update_chart(time):
        global x, y, AAPL, AAPL_BA

        x.append(time)
        y.append(round(AAPL_BA / AAPL * 10,2))

        fig = go.Figure(data=go.Scatter(x=list(x), y=list(y)),layout_yaxis_range=[min(y),max(y)])
        return fig

    app.run_server(debug=True, port=3000) #Debug=True lo que me hace es mostrar un cartel en la página de la aplicación webde si algo deja de andar.

# Separación de los procesos
Datos=threading.Thread(target=ws_acciones)
Datos.daemon = True
Datos.start()

Datos=threading.Thread(target=ws_cedears)
Datos.daemon = True
Datos.start()

Datos=threading.Thread(target=pagina_web())
Datos.daemon = True
Datos.start()

