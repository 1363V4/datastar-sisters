from quart import Quart, session, render_template, request
from datastar_py import ServerSentEventGenerator as SSE
from datastar_py.quart import DatastarResponse, read_signals

import json

from data.places import places
from data.sisters import sisters

# CONFIG

app = Quart(__name__)
app.secret_key = 'a_secret_key'

@app.get('/')
async def index():
    return await render_template('index.html')

@app.get('/cities')
async def cities():
    html = '<datalist id="cities">'
    for place in places:
        ci, co = place.split("___")
        html += f"<option>{ci} ({co})</option>"
    html += '</datalist>'
    return DatastarResponse(SSE.merge_fragments(html))

@app.post('/test')
async def test():
    places = {
        "Berat___Albania": {
            "lat": "40.70222",
            "lng": "19.95833"
        },
        "Amasya___Turkey": {
            "lat": "40.65000",
            "lng": "35.83306"
        },
        "Brest___France": {
            "lat": "48.39",
            "lng": "-4.49"
        },
    }
    g_places = json.dumps(places)
    arcs = [
        {'startLat': 10, 'startLng': 10, 'endLat': 20, 'endLng': 20}
    ]
    g_arcs = json.dumps(arcs)
    return DatastarResponse(
        SSE.merge_fragments(f'''<globe-component 
                    id="globe"
                    places='{g_places}'
                    arcs='{g_arcs}'
                ></globe-component>''')
    )

@app.post('/sister')
async def sister():
    signals = await read_signals()
    if signals.get('city'):
        print(signals['city'])
        city = signals['city']
        ci, co = city.split()
        city_code = f"{ci}___{co.replace("(", "").replace(")", "")}"
        print(city_code)
        if city_code in places:
            sister_cities = sisters[city_code]
            g_places = {}
            arcs = []
            lat1, lng1 = places[city_code].values()
            g_places[city_code] = {'lat': lat1, 'lng': lng1}
            for code in sister_cities:
                lat, lng = places[code].values()
                g_places[code] = {'lat': lat, 'lng': lng}
                lat2, lng2 = places[code].values()
                arcs.append({
                    'startLat': float(lat1),
                    'startLng': float(lng1),
                    'endLat': float(lat2),
                    'endLng': float(lng2)
                })
            g_places = json.dumps(g_places)
            g_arcs = json.dumps(arcs)
            return DatastarResponse(SSE.merge_fragments(
                f'''<globe-component id="globe" 
                places='{g_places}'
                arcs='{g_arcs}'
                zoom='{json.dumps({'lat': lat1, 'lng': lng1})}'></globe-component>''')
                )
    return DatastarResponse()

if __name__ == '__main__':
    app.run(debug=True)