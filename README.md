# Dashboards-con-dash-plotly

Este dashboard grafica en tiempo real valor del dólar CCL de la acción de Apple.

## Cómo funciona el script:
  - se creó una conexión websocket con Finnhub para traer market data (último precio, volumen, hora del último trade) de la acción de Apple en tiempo real.
  - se creó una conexión websocket con Pyrofex para traer market data (último precio, bid, offer, volumen) del cedear de Apple en tiempo real.
  - se creó una web app simple con un gráfico interactivo, con las librerías Dash y Plotly.
  - se crearon 3 threads para que todo funcione en paralelo simultáneamente.

## Qué se necesita:
  - Para usar Finnhub se necesita un token (línea 116 del código). Se puede obtener gratis en la página de Finnhub.
  - Para usar Pyrofex se necesita tener una cuenta en un broker que utilice la plataforma Talaris, ya el que el código pide usuario y contraseña de ahí (líneas 26 y 27 del código). Y además el broker debe ofrecer invertir en el mercado BYMA, para que dentro de la información disponible que me envíe Pyrofex estén disponibles los CEDEARS ya que se operan en BYMA. 
