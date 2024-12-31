import unittest
from datetime import datetime, timedelta
import json
import os
from railway_route_planner import RailwayRoutePlanner, Station, Train, Route

# Create test data files
def create_sample_data():
    """Create sample data files for testing"""
    stations_data = [
        {"code": "NDLS", "name": "New Delhi", "lat": 28.6419, "lon": 77.2195},
        {"code": "MMCT", "name": "Mumbai Central", "lat": 18.9398, "lon": 72.8194},
        {"code": "CNB", "name": "Kanpur Central", "lat": 26.4499, "lon": 80.3319},
        {"code": "BPL", "name": "Bhopal Junction", "lat": 23.2687, "lon": 77.4168}
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
            "name": "Rajdhani Express",
            "source": "NDLS",
            "destination": "CNB",
            "stops": [
                ["NDLS", "15:00", "15:25"],
                ["CNB", "20:30", None]
            ]
        }
    ]

    with open('test_stations.json', 'w') as f:
        json.dump(stations_data, f, indent=2)

    with open('test_trains.json', 'w') as f:
        json.dump(trains_data, f, indent=2)

class TestRailwayRoutePlanner(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Create test data files
        create_sample_data()

    def setUp(self):
        self.planner = RailwayRoutePlanner()
        self.planner.load_station_data("test_stations.json")
        self.planner.load_train_data("test_trains.json")
        self.planner.build_graph()

    def test_station_loading(self):
        """Test if stations are loaded correctly"""
        self.assertEqual(len(self.planner.stations), 4)
        self.assertEqual(self.planner.stations["NDLS"].name, "New Delhi")
        self.assertEqual(self.planner.stations["MMCT"].latitude, 18.9398)

    def test_train_loading(self):
        """Test if trains are loaded correctly"""
        self.assertEqual(len(self.planner.trains), 2)
        self.assertEqual(self.planner.trains["12951"].name, "Rajdhani Express")

    def test_direct_route_finding(self):
        """Test finding direct route between stations"""
        routes = self.planner.find_routes("NDLS", "MMCT", datetime(2024, 1, 1))
        self.assertTrue(len(routes) >= 1)
        # Find direct route (route with single segment)
        direct_routes = [r for r in routes if len(r.segments) == 1]
        self.assertTrue(len(direct_routes) > 0)
        self.assertEqual(direct_routes[0].segments[0][0].number, "12951")

    def test_invalid_route(self):
        """Test handling of invalid routes"""
        routes = self.planner.find_routes("NDLS", "INVALID", datetime(2024, 1, 1))
        self.assertEqual(len(routes), 0)

    @classmethod
    def tearDownClass(cls):
        # Clean up test files
        if os.path.exists("test_stations.json"):
            os.remove("test_stations.json")
        if os.path.exists("test_trains.json"):
            os.remove("test_trains.json")

if __name__ == '__main__':
    unittest.main()