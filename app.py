from quart import Quart, session, render_template, request
from datastar_py.sse import ServerSentEventGenerator as SSE
from datastar_py.quart import make_datastar_response

import json

# from data.places import places

# CONFIG

app = Quart(__name__)
app.secret_key = 'a_secret_key'

@app.get('/')
async def index():
    return await render_template('index.html')

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
    return SSE.merge_fragments(fragments=[f'''<globe-component 
            id="globe"
            places='{g_places}'
            arcs='{g_arcs}'
        ></globe-component>'''])

# @app.route('/get_paths')
# async def get_paths():
#     # Dynamic path data endpoint (example)
#     return jsonify([
#         {"startLat": 35.68, "startLng": 139.76, "endLat": 37.77, "endLng": -122.41}
#     ])

if __name__ == '__main__':
    app.run(debug=True)