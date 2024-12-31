from dataclasses import dataclass
from typing import List, Dict, Tuple
from datetime import datetime, timedelta
from collections import defaultdict
import networkx as nx

@dataclass
class Station:
    code: str
    name: str
    latitude: float
    longitude: float

@dataclass
class Train:
    number: str
    name: str
    source: str
    destination: str
    stops: List[Tuple[str, datetime, datetime]]  # (station_code, arrival, departure)

@dataclass
class Route:
    segments: List[Tuple[Train, Station, Station]]  # (train, from_station, to_station)
    total_duration: timedelta
    total_distance: float
    transfers: int
    availability: Dict[str, bool]  # train_number -> is_available

class RailwayRoutePlanner:
    def __init__(self):
        self.stations: Dict[str, Station] = {}
        self.trains: Dict[str, Train] = {}
        self.graph = nx.DiGraph()
        self.station_connections = defaultdict(list)
        
    def load_station_data(self, filename: str):
        """Load station data from JSON"""
        import json
        with open(filename, 'r') as f:
            data = json.load(f)
            for station in data:
                self.stations[station['code']] = Station(
                    code=station['code'],
                    name=station['name'],
                    latitude=station['lat'],
                    longitude=station['lon']
                )
        
    def load_train_data(self, filename: str):
        """Load train schedules from JSON"""
        import json
        with open(filename, 'r') as f:
            data = json.load(f)
            for train in data:
                stops = []
                for stop in train['stops']:
                    arrival = datetime.strptime(stop[1], '%H:%M') if stop[1] else None
                    departure = datetime.strptime(stop[2], '%H:%M') if stop[2] else None
                    stops.append((stop[0], arrival, departure))
                
                self.trains[train['number']] = Train(
                    number=train['number'],
                    name=train['name'],
                    source=train['source'],
                    destination=train['destination'],
                    stops=stops
                )
        
    def build_graph(self):
        """Build a directed graph of all possible connections"""
        for train in self.trains.values():
            for i in range(len(train.stops) - 1):
                curr_stop = train.stops[i]
                next_stop = train.stops[i + 1]
                
                self.graph.add_edge(
                    curr_stop[0],
                    next_stop[0],
                    train=train,
                    departure=curr_stop[2],
                    arrival=next_stop[1]
                )
                
    def find_routes(self, source: str, destination: str, date: datetime, 
               max_transfers: int = 2) -> List[Route]:
        """Find all possible routes between source and destination"""
        if source not in self.stations or destination not in self.stations:
            return []
        
        routes = []
        visited = set()
    
        def dfs(current: str, path: List[Tuple[Train, Station, Station]], 
            transfers: int, total_time: timedelta):
            if transfers > max_transfers:
                return
            
            if current == destination and path:  # Make sure we have a path
                routes.append(Route(
                    segments=path.copy(),
                    total_duration=total_time,
                    total_distance=self._calculate_distance(path),
                    transfers=len(path) - 1,
                    availability={}
                ))
                return
            
            # Look for all outgoing edges
            for _, next_station, edge_data in self.graph.edges(current, data=True):
                train = edge_data['train']
            
                # Skip if we've visited this station in this path
                if next_station in visited:
                    continue
                
                # Add the segment to our path
                visited.add(next_station)
                path.append((train, 
                           self.stations[current],
                           self.stations[next_station]))
            
                # Calculate time for this segment
                segment_time = timedelta(hours=2)  # Simplified duration
                if edge_data['departure'] and edge_data['arrival']:
                    hours = edge_data['arrival'].hour - edge_data['departure'].hour
                    if hours < 0:  # Handle overnight trains
                        hours += 24
                    segment_time = timedelta(hours=hours)
            
                # Continue search
                dfs(next_station, path, 
                    transfers + (1 if path[-1][0] != train else 0), 
                    total_time + segment_time)
            
                # Backtrack
                path.pop()
                visited.remove(next_station)
    
        visited.add(source)
        dfs(source, [], 0, timedelta())
    
        return routes
        
    def _calculate_distance(self, path: List[Tuple[Train, Station, Station]]) -> float:
        """Calculate total distance of the route"""
        total_distance = 0.0
        for segment in path:
            from_station = segment[1]
            to_station = segment[2]
            # Simplified distance calculation
            total_distance += abs(from_station.latitude - to_station.latitude) + \
                            abs(from_station.longitude - to_station.longitude)
        return total_distance
    
