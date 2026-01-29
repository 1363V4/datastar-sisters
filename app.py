from quart import Quart, render_template, request
from datastar_py import ServerSentEventGenerator as SSE
from datastar_py.quart import DatastarResponse, read_signals
from brotli_asgi import BrotliMiddleware

from tinydb import TinyDB, where

import json
import time
import logging


# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
    handlers=[logging.FileHandler("log/perso.log")]
)

# CONFIG

app = Quart(__name__)
app.asgi_app = BrotliMiddleware(app.asgi_app) 

db = TinyDB("data.json", indent=4, ensure_ascii=False)
db_cities = db.table("cities")

@app.get('/')
async def index():
    return await render_template(
        'index.html', 
        globe='''<globe-component id="globe"></globe-component>'''
        )

@app.get('/cities')
async def cities():
    html = '<datalist id="cities">'
    signals = await read_signals()
    if city := signals.get('city'):
        all_cities = db_cities.all()
        cities = [c for c in all_cities if city.lower() in c.get("city", "").lower()]
        for city in cities:
            html += f"<option>{city['display']}</option>"
    html += '</datalist>'
    return DatastarResponse(SSE.merge_fragments(html))

@app.route('/<value>', methods=["GET", "POST"])
async def sister(value):
    city = db_cities.get(where("display") == value)
    if city:
        # some computation
        start = time.time()
        g_places = {}
        arcs = []
        lat1, lng1 = city['lat'], city['lng']
        g_places[city['display']] = {'lat': lat1, 'lng': lng1}
        sis_data = db_cities.get(doc_ids=city['sis'])
        for data in sis_data:
            lat2, lng2 = data['lat'], data['lng']
            g_places[data['display']] = {'lat': lat2, 'lng': lng2}
            arcs.append({
                'startLat': float(lat1),
                'startLng': float(lng1),
                'endLat': float(lat2),
                'endLng': float(lng2)
            })
        g_places = json.dumps(g_places)
        g_arcs = json.dumps(arcs)
        zoom = json.dumps({'lat': lat1, 'lng': lng1})
        globe = f'''<globe-component id="globe" 
                places='{g_places}'
                arcs='{g_arcs}'
                zoom='{zoom}'>
                <div id="globe-container" data-ignore-morph></div>
                </globe-component>'''
        logging.info(f"{value} ok in {time.time() - start:.2f} seconds")
        if request.method == "GET":
            return await render_template('index.html', globe=globe)
        else:
            return DatastarResponse(SSE.merge_fragments(globe))
    return DatastarResponse()

# if __name__ == '__main__':
#     app.run(debug=True)
