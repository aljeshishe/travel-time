#!/usr/bin/env python3
"""Build interactive HTML map from collected travel time data."""

import glob
import json
import os

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
OUTPUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "index.html")

DESTINATION = {
    "name": "Alber Blanc",
    "lat": 34.685361,
    "lng": 33.055667,
}

POINTS = [
    {"name": "Limassol - Zakaki", "lat": 34.655087, "lng": 33.01148},
    {"name": "Trachoni Lemesou", "lat": 34.65644, "lng": 32.96281},
    {"name": "Kato Polemidia", "lat": 34.68938, "lng": 33.00874},
    {"name": "Agios Tychon Tourist Area", "lat": 34.72524, "lng": 33.13828},
    {"name": "Historical Center", "lat": 34.67376, "lng": 33.04264},
    {"name": "Agios Athanasios", "lat": 34.7292, "lng": 33.05403},
    {"name": "Limassol - Tsirion", "lat": 34.70089, "lng": 33.02278},
    {"name": "Limassol - Apostolos Andreas", "lat": 34.68093, "lng": 33.018},
    {"name": "Limassol - Katholiki", "lat": 34.68015, "lng": 33.03681},
    {"name": "Limassol - Neapolis", "lat": 34.68825, "lng": 33.06227},
    {"name": "Limassol - Agios Nicolaos", "lat": 34.69273, "lng": 33.0578},
    {"name": "Limassol - Agios Spyridon", "lat": 34.66846, "lng": 33.00258},
    {"name": "Pyrgos Lemesou", "lat": 34.74179, "lng": 33.1832},
    {"name": "Ypsonas", "lat": 34.68828, "lng": 32.96121},
    {"name": "Limassol", "lat": 34.67863, "lng": 33.04131},
    {"name": "Limassol - Agia Fyla", "lat": 34.71725, "lng": 33.01178},
    {"name": "Parekklisia", "lat": 34.74358, "lng": 33.16008},
    {"name": "Filbert Residence", "lat": 34.69073, "lng": 33.046758},
    {"name": "Point @34.6858,33.0396", "lat": 34.685751, "lng": 33.039624},
    {"name": "Parpis Carob Syrup", "lat": 34.702046, "lng": 33.050907},
    {"name": "Point @34.6967,33.0819", "lat": 34.696708, "lng": 33.081927},
    {"name": "La Thea Residences", "lat": 34.709083, "lng": 33.039893},
    {"name": "Pelopida 28", "lat": 34.668939, "lng": 33.015863},
    {"name": "Elia Residence", "lat": 34.713959, "lng": 33.0561},
    {"name": "BLOCK B PLATINUM 77", "lat": 34.658257, "lng": 33.007895},
    {"name": "METRO Supermarket", "lat": 34.703463, "lng": 33.106341},
    {"name": "Point @34.6887,32.9626", "lat": 34.688675, "lng": 32.962583},
    {"name": "Four Seasons Hotel", "lat": 34.709706, "lng": 33.128048},
    {"name": "Sanctum at Sunset Gardens", "lat": 34.64812, "lng": 32.986207},
    {"name": "Malindi Beach Bar", "lat": 34.711973, "lng": 33.164902},
    {"name": "Point @34.6764,32.9346", "lat": 34.676444, "lng": 32.934611},
    {"name": "Point @34.6714,32.9031", "lat": 34.671389, "lng": 32.903056},
    {"name": "Point @34.7199,33.0850", "lat": 34.719944, "lng": 33.085028},
    {"name": "Point @34.7024,32.9957", "lat": 34.702417, "lng": 32.995667},
]


def load_all_data():
    """Load all JSON data files."""
    all_collections = []
    pattern = os.path.join(DATA_DIR, "*.json")
    for filepath in sorted(glob.glob(pattern)):
        with open(filepath, "r") as f:
            data = json.load(f)
        all_collections.extend(data.get("collections", []))
    return all_collections


def build_html(collections):
    """Generate index.html with embedded data."""
    points_json = json.dumps(POINTS, ensure_ascii=False)
    destination_json = json.dumps(DESTINATION, ensure_ascii=False)
    collections_json = json.dumps(collections, ensure_ascii=False)

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Travel Time Map - Limassol to Alber Blanc</title>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; }}
  #map {{ width: 100%; height: 100vh; }}
  .controls {{
    position: absolute; top: 10px; right: 10px; z-index: 1000;
    background: white; padding: 15px; border-radius: 8px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.2); max-width: 320px;
  }}
  .controls h3 {{ margin-bottom: 10px; font-size: 14px; }}
  .controls label {{ font-size: 13px; display: block; margin-bottom: 4px; }}
  .controls select, .controls input[type=range] {{ width: 100%; margin-bottom: 10px; }}
  .direction-btn {{
    width: 100%; padding: 8px; border: 2px solid #4A90D9; background: #4A90D9;
    color: white; border-radius: 4px; cursor: pointer; font-size: 13px; font-weight: bold;
    margin-bottom: 10px;
  }}
  .direction-btn:hover {{ background: #357ABD; }}
  .direction-btn.from {{ background: #9B59B6; border-color: #9B59B6; }}
  .direction-btn.from:hover {{ background: #8E44AD; }}
  .time-display {{ font-size: 12px; color: #666; text-align: center; margin-top: 2px; }}
  .legend {{
    position: absolute; bottom: 30px; left: 10px; z-index: 1000;
    background: white; padding: 10px 14px; border-radius: 8px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.2); font-size: 12px;
  }}
  .legend-item {{ display: flex; align-items: center; margin: 4px 0; }}
  .legend-dot {{
    width: 14px; height: 14px; border-radius: 50%; margin-right: 8px;
    border: 2px solid rgba(0,0,0,0.3);
  }}
  .no-data {{ color: #999; font-style: italic; font-size: 12px; text-align: center; padding: 10px 0; }}
</style>
</head>
<body>
<div id="map"></div>
<div class="controls">
  <h3>Travel Time Map</h3>
  <button class="direction-btn" id="dirBtn" onclick="toggleDirection()">To Alber Blanc</button>
  <label for="timeSlider">Time:</label>
  <input type="range" id="timeSlider" min="0" max="0" value="0" oninput="updateMap()">
  <div class="time-display" id="timeDisplay">No data</div>
</div>
<div class="legend">
  <div class="legend-item"><div class="legend-dot" style="background:#2ECC40"></div> &lt; 10 min</div>
  <div class="legend-item"><div class="legend-dot" style="background:#FFDC00"></div> 10-20 min</div>
  <div class="legend-item"><div class="legend-dot" style="background:#FF4136"></div> &gt; 20 min</div>
  <div class="legend-item"><div class="legend-dot" style="background:#AAAAAA"></div> No data</div>
</div>

<script>
const POINTS = {points_json};
const DEST = {destination_json};
const COLLECTIONS = {collections_json};

let direction = 'to'; // 'to' or 'from'
let markers = [];

const map = L.map('map').setView([34.695, 33.04], 13);
L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
  attribution: '&copy; OpenStreetMap contributors',
  maxZoom: 18
}}).addTo(map);

// Destination marker
const destIcon = L.divIcon({{
  className: '',
  html: '<div style="width:20px;height:20px;background:#9B59B6;border:3px solid white;border-radius:50%;box-shadow:0 2px 6px rgba(0,0,0,0.4)"></div>',
  iconSize: [20, 20],
  iconAnchor: [10, 10]
}});
L.marker([DEST.lat, DEST.lng], {{icon: destIcon}})
  .addTo(map)
  .bindPopup('<b>' + DEST.name + '</b><br>Destination');

// Setup slider
const slider = document.getElementById('timeSlider');
const timeDisplay = document.getElementById('timeDisplay');
if (COLLECTIONS.length > 0) {{
  slider.max = COLLECTIONS.length - 1;
  slider.value = 0;
}}

function getColor(seconds) {{
  if (seconds <= 0) return '#AAAAAA';
  const minutes = seconds / 60;
  if (minutes < 10) return '#2ECC40';
  if (minutes <= 20) {{
    const ratio = (minutes - 10) / 10;
    const r = Math.round(46 + (255 - 46) * ratio);
    const g = Math.round(204 + (220 - 204) * ratio * 0.3);
    const b = Math.round(64 + (0 - 64) * ratio);
    return 'rgb(' + r + ',' + g + ',' + b + ')';
  }}
  return '#FF4136';
}}

function formatDuration(seconds) {{
  if (!seconds) return 'N/A';
  const m = Math.floor(seconds / 60);
  const s = seconds % 60;
  return m + ' min ' + s + ' sec';
}}

function formatTimestamp(ts) {{
  const d = new Date(ts);
  return d.toLocaleDateString('en-GB', {{day:'2-digit',month:'short'}}) + ' ' +
         d.toLocaleTimeString('en-GB', {{hour:'2-digit',minute:'2-digit'}});
}}

function clearMarkers() {{
  markers.forEach(m => map.removeLayer(m));
  markers = [];
}}

function updateMap() {{
  clearMarkers();
  if (COLLECTIONS.length === 0) {{
    timeDisplay.textContent = 'No data collected yet';
    return;
  }}

  const idx = parseInt(slider.value);
  const col = COLLECTIONS[idx];
  const data = direction === 'to' ? col.to_destination : col.from_destination;
  timeDisplay.textContent = formatTimestamp(col.timestamp);

  POINTS.forEach(pt => {{
    const info = data[pt.name];
    const dur = info ? info.duration_seconds : 0;
    const dist = info ? info.distance_meters : 0;
    const color = getColor(dur);

    const minLabel = dur > 0 ? Math.round(dur / 60) + '' : '?';
    const icon = L.divIcon({{
      className: '',
      html: '<div style="position:relative;width:36px;height:36px">' +
            '<div style="width:14px;height:14px;background:' + color +
            ';border:2px solid rgba(0,0,0,0.3);border-radius:50%;box-shadow:0 1px 4px rgba(0,0,0,0.3);position:absolute;left:11px;top:11px"></div>' +
            '<div style="position:absolute;top:-2px;left:50%;transform:translateX(-50%);font-size:11px;font-weight:bold;color:#333;' +
            'text-shadow:1px 1px 1px white,-1px -1px 1px white,1px -1px 1px white,-1px 1px 1px white;white-space:nowrap">' + minLabel + '</div></div>',
      iconSize: [36, 36],
      iconAnchor: [18, 18]
    }});

    const dirLabel = direction === 'to' ? 'To Alber Blanc' : 'From Alber Blanc';
    let originLat, originLng, destLat, destLng;
    if (direction === 'to') {{
      originLat = pt.lat; originLng = pt.lng;
      destLat = DEST.lat; destLng = DEST.lng;
    }} else {{
      originLat = DEST.lat; originLng = DEST.lng;
      destLat = pt.lat; destLng = pt.lng;
    }}
    const gmapsUrl = 'https://www.google.com/maps/dir/' + originLat + ',' + originLng + '/' + destLat + ',' + destLng;
    const popup = '<b>' + pt.name + '</b><br>' +
                  dirLabel + '<br>' +
                  'Time: <b>' + formatDuration(dur) + '</b><br>' +
                  'Distance: ' + (dist / 1000).toFixed(1) + ' km<br>' +
                  '<a href="' + gmapsUrl + '" target="_blank" style="color:#4A90D9">Open in Google Maps</a>';

    const m = L.marker([pt.lat, pt.lng], {{icon: icon}}).addTo(map).bindPopup(popup);
    markers.push(m);
  }});
}}

function toggleDirection() {{
  const btn = document.getElementById('dirBtn');
  if (direction === 'to') {{
    direction = 'from';
    btn.textContent = 'From Alber Blanc';
    btn.classList.add('from');
  }} else {{
    direction = 'to';
    btn.textContent = 'To Alber Blanc';
    btn.classList.remove('from');
  }}
  updateMap();
}}

updateMap();
</script>
</body>
</html>"""
    return html


def main():
    collections = load_all_data()
    print(f"Loaded {len(collections)} collections from data/")

    html = build_html(collections)
    with open(OUTPUT, "w") as f:
        f.write(html)
    print(f"Generated {OUTPUT}")


if __name__ == "__main__":
    main()
