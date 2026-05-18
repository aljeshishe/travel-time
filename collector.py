#!/usr/bin/env python3
"""Collect travel time data between points in Limassol and Alber Blanc restaurant."""

import argparse
import json
import os
import sys
import time
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

CYPRUS_TZ = ZoneInfo("Asia/Nicosia")

import requests
import schedule
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))

API_KEY = os.environ["GOOGLE_API_KEY"]
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

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

ROUTES_API_URL = "https://routes.googleapis.com/distanceMatrix/v2:computeRouteMatrix"


def compute_route_matrix(origins, destinations):
    """Call Google Routes API to compute route matrix."""
    origin_waypoints = [
        {"waypoint": {"location": {"latLng": {"latitude": o["lat"], "longitude": o["lng"]}}}}
        for o in origins
    ]
    dest_waypoints = [
        {"waypoint": {"location": {"latLng": {"latitude": d["lat"], "longitude": d["lng"]}}}}
        for d in destinations
    ]

    body = {
        "origins": origin_waypoints,
        "destinations": dest_waypoints,
        "travelMode": "DRIVE",
        "routingPreference": "TRAFFIC_AWARE",
    }

    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": API_KEY,
        "X-Goog-FieldMask": "originIndex,destinationIndex,duration,distanceMeters,status",
    }

    resp = requests.post(ROUTES_API_URL, json=body, headers=headers, timeout=60)
    resp.raise_for_status()
    return resp.json()


def parse_duration(duration_str):
    """Parse duration string like '123s' to integer seconds."""
    if not duration_str:
        return 0
    return int(duration_str.rstrip("s"))


def collect_once():
    """Perform a single data collection."""
    now = datetime.now(CYPRUS_TZ)
    timestamp = now.strftime("%Y-%m-%dT%H:%M:%S")
    date_str = now.strftime("%Y-%m-%d")
    print(f"[{timestamp}] Collecting travel time data...")

    # To destination: points -> Alber Blanc
    to_dest = {}
    try:
        results = compute_route_matrix(POINTS, [DESTINATION])
        for entry in results:
            if isinstance(entry, dict) and entry.get("status", {}).get("code", 0) == 0 or "duration" in entry:
                oidx = entry.get("originIndex", 0)
                duration = parse_duration(entry.get("duration", "0s"))
                distance = entry.get("distanceMeters", 0)
                point_name = POINTS[oidx]["name"]
                to_dest[point_name] = {
                    "duration_seconds": duration,
                    "distance_meters": distance,
                }
        print(f"  To destination: {len(to_dest)} routes collected")
    except Exception as e:
        print(f"  ERROR collecting to_destination: {e}")

    # From destination: Alber Blanc -> points
    from_dest = {}
    try:
        results = compute_route_matrix([DESTINATION], POINTS)
        for entry in results:
            if isinstance(entry, dict) and entry.get("status", {}).get("code", 0) == 0 or "duration" in entry:
                didx = entry.get("destinationIndex", 0)
                duration = parse_duration(entry.get("duration", "0s"))
                distance = entry.get("distanceMeters", 0)
                point_name = POINTS[didx]["name"]
                from_dest[point_name] = {
                    "duration_seconds": duration,
                    "distance_meters": distance,
                }
        print(f"  From destination: {len(from_dest)} routes collected")
    except Exception as e:
        print(f"  ERROR collecting from_destination: {e}")

    collection = {
        "timestamp": timestamp,
        "to_destination": to_dest,
        "from_destination": from_dest,
    }

    # Save to file
    filepath = os.path.join(DATA_DIR, f"{date_str}.json")
    if os.path.exists(filepath):
        with open(filepath, "r") as f:
            data = json.load(f)
    else:
        data = {"collections": []}

    data["collections"].append(collection)

    os.makedirs(DATA_DIR, exist_ok=True)
    with open(filepath, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"  Saved to {filepath} ({len(data['collections'])} collections total)")
    return collection


def is_collection_time():
    """Check if current time is within collection window (7:00-20:00)."""
    now = datetime.now(CYPRUS_TZ)
    return 7 <= now.hour < 20


def run_scheduler(days=2):
    """Run the scheduler for the specified number of days."""
    start_time = datetime.now(CYPRUS_TZ)
    end_time = start_time + timedelta(days=days)
    print(f"Starting collector. Will run until {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Collection window: 7:00-20:00, every 30 minutes")

    # Schedule collection every 30 minutes
    schedule.every(30).minutes.do(lambda: collect_once() if is_collection_time() else None)

    # Also collect immediately if within window
    if is_collection_time():
        collect_once()

    while datetime.now(CYPRUS_TZ) < end_time:
        schedule.run_pending()
        time.sleep(30)

    print("Collection period complete.")


def main():
    parser = argparse.ArgumentParser(description="Travel time data collector")
    parser.add_argument("--once", action="store_true", help="Collect once and exit")
    parser.add_argument("--days", type=int, default=2, help="Number of days to collect (default: 2)")
    args = parser.parse_args()

    os.makedirs(DATA_DIR, exist_ok=True)

    if args.once:
        collect_once()
    else:
        run_scheduler(days=args.days)


if __name__ == "__main__":
    main()
