class GlobeComponent extends HTMLElement {
    constructor() {
        super();
        this.attachShadow({ mode: 'open' });
        this.shadowRoot.innerHTML = `
            <div id="globe-container"></div>
            <style>
                .place-marker {
                    color: #ff0000;
                    width: 20px;
                    top: -10px;
                    position: relative;
                }
                .place-marker svg {
                    width: 100%;
                    height: 100%;
                }
                .place-name {
                    position: absolute;
                    top: 0px;
                    left: 50%;
                    transform: translateX(-50%);
                    white-space: nowrap;
                    color: white;
                    text-shadow: 1px 1px 2px black;
                    font-size: 12px;
                }
            </style>
        `;
        this.container = this.shadowRoot.getElementById('globe-container');
        this.globe = null;
        this.markerSvg = `<svg viewBox="-4 0 36 36">
            <path fill="currentColor" d="M14,0 C21.732,0 28,5.641 28,12.6 C28,23.963 14,36 14,36 C14,36 0,24.064 0,12.6 C0,5.641 6.268,0 14,0 Z"></path>
            <circle fill="black" cx="14" cy="14" r="7"></circle>
        </svg>`;
    }

    static get observedAttributes() {
        return ['paths', 'zoom', 'places', 'arcs'];
    }

    attributeChangedCallback(name, oldValue, newValue) {
        if (name === 'paths' && newValue) {
            this.updatePaths(JSON.parse(newValue));
        } else if (name === 'zoom' && newValue) {
            this.updateZoom(JSON.parse(newValue));
        } else if (name === 'places' && newValue) {
            this.updatePlaces(JSON.parse(newValue));
        } else if (name === 'arcs' && newValue) {
            this.updateArcs(JSON.parse(newValue));
        }
    }

    connectedCallback() {
        this.initGlobe();
    }

    initGlobe() {
        this.globe = Globe()(this.container)
            .globeImageUrl('https://unpkg.com/three-globe/example/img/earth-blue-marble.jpg')
            .bumpImageUrl('https://unpkg.com/three-globe/example/img/earth-topology.png');
    }

    updatePaths(paths) {
        console.log(paths);
        if (this.globe) {
            this.globe.pathsData(paths)
                .pathColor(() => '#ff0000')
                .pathStroke(0.5);
        }
    }

    updateZoom(zoomData) {
        console.log(zoomData);
        if (this.globe) {
            this.globe.pointOfView(
                {
                    lat: zoomData.lat,
                    lng: zoomData.lng,
                },
                2000
            );
        }
    }

    updatePlaces(places) {
        if (this.globe) {
            const elements = Object.entries(places).map(([name, coords]) => ({
                name,
                lat: parseFloat(coords.lat),
                lng: parseFloat(coords.lng),
                html: `<div class="place-marker">
                    ${this.markerSvg}
                    <div class="place-name">${name.replace('___', ', ')}</div>
                </div>`
            }));
            
            this.globe.htmlElementsData(elements)
                .htmlElement(d => {
                    const el = document.createElement('div');
                    el.innerHTML = d.html;
                    return el;
                });
        }
    }

    updateArcs(arcs) {
        if (this.globe) {
            this.globe
                .arcsData(arcs)
                .arcDashLength(0.5)
                .arcDashGap(0.5)
                .arcDashAnimateTime(1000);
        }
    }
}

customElements.define('globe-component', GlobeComponent);