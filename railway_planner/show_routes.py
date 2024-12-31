from railway_route_planner import RailwayRoutePlanner
from datetime import datetime
import json

def create_sample_data():
    """Create more comprehensive sample data"""
    stations_data = [
        {"code": "NDLS", "name": "New Delhi", "lat": 28.6419, "lon": 77.2195},
        {"code": "MMCT", "name": "Mumbai Central", "lat": 18.9398, "lon": 72.8194},
        {"code": "CNB", "name": "Kanpur Central", "lat": 26.4499, "lon": 80.3319},
        {"code": "BPL", "name": "Bhopal Junction", "lat": 23.2687, "lon": 77.4168},
        {"code": "JHS", "name": "Jhansi", "lat": 25.4484, "lon": 78.5685},
        {"code": "NGP", "name": "Nagpur", "lat": 21.1458, "lon": 79.0882}
    ]

    trains_data = [
        {
            "number": "12951",
            "name": "Rajdhani Express",
            "source": "NDLS",
            "destination": "MMCT",
            "stops": [
                ["NDLS", "16:00", "16:25"],
                ["BPL", "00:30", "00:35"],
                ["MMCT", "08:00", None]
            ]
        },
        {
            "number": "12309",
            "name": "Shatabdi Express",
            "source": "NDLS",
            "destination": "BPL",
            "stops": [
                ["NDLS", "15:00", "15:25"],
                ["CNB", "20:30", "20:35"],
                ["BPL", "23:30", None]
            ]
        },
        {
            "number": "12139",
            "name": "Sewagram Express",
            "source": "BPL",
            "destination": "MMCT",
            "stops": [
                ["BPL", "01:30", "01:45"],
                ["NGP", "06:30", "06:35"],
                ["MMCT", "15:00", None]
            ]
        }
    ]

    with open('test_stations.json', 'w') as f:
        json.dump(stations_data, f, indent=2)

    with open('test_trains.json', 'w') as f:
        json.dump(trains_data, f, indent=2)

def display_route(route, index):
    """Display a single route with detailed information"""
    print(f"\nRoute {index + 1}:")
    print("=" * 50)
    
    print(f"Total Duration: {route.total_duration}")
    print(f"Number of Transfers: {route.transfers}")
    print(f"Approximate Distance: {route.total_distance:.2f} units")
    print("\nSegments:")
    
    for i, segment in enumerate(route.segments, 1):
        train, from_station, to_station = segment
        print(f"\nSegment {i}:")
        print(f"Train: {train.number} - {train.name}")
        print(f"From: {from_station.name} ({from_station.code})")
        print(f"To: {to_station.name} ({to_station.code})")
        
        # Find the departure and arrival times from train schedule
        for stop in train.stops:
            if stop[0] == from_station.code:
                departure = stop[2].strftime('%H:%M') if stop[2] else 'N/A'
                print(f"Departure: {departure}")
        for stop in train.stops:
            if stop[0] == to_station.code:
                arrival = stop[1].strftime('%H:%M') if stop[1] else 'N/A'
                print(f"Arrival: {arrival}")

def main():
    # Create fresh sample data
    create_sample_data()
    
    # Initialize the planner
    planner = RailwayRoutePlanner()
    planner.load_station_data("test_stations.json")
    planner.load_train_data("test_trains.json")
    planner.build_graph()
    
    # Search for routes
    print("\nSearching for routes from New Delhi to Mumbai Central...")
    routes = planner.find_routes("NDLS", "MMCT", datetime(2024, 1, 1))
    
    if not routes:
        print("No routes found!")
        return
        
    print(f"\nFound {len(routes)} possible route(s):")
    
    # Display all routes
    for i, route in enumerate(routes):
        display_route(route, i)
        
    # Show some statistics
    print("\nRoute Statistics:")
    print("=" * 50)
    print(f"Total routes found: {len(routes)}")
    print(f"Direct routes: {len([r for r in routes if len(r.segments) == 1])}")
    print(f"Routes with transfers: {len([r for r in routes if len(r.segments) > 1])}")
    
if __name__ == "__main__":
    main()