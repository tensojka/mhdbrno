import csv
from typing import List, Tuple, Dict, Optional
import heapq

StopId = str
Time = int
TripId = str
Departure = Tuple[Time, TripId] # departure 
Moment = Tuple[Time, StopId, "StopTime"]  # one moment in spacetime. stopTime is origin stop, StopId is current stop.
stop_times_by_tripid: Dict[TripId, List["StopTime"]] = dict()
trips: Dict[TripId, "Trip"] = dict()
stops: Dict[StopId, "Stop"] = dict()
stops_by_canonical_id: Dict[StopId, List[StopId]] = dict()  # holds all stops that correspond to a given canonical stop, including the canonical stop itself

###### misc

def parse_time(inp: str) -> Time:
    '''Parse time from 12:34:00 into amount of seconds since midnight'''
    # strftime to parse
    parts = inp.split(":")
    if len(parts) != 3:
        print(inp)
        assert len(parts) == 3
    res = 0
    res += int(parts[0]) * 60 * 60
    res += int(parts[1]) * 60
    res += int(parts[2])
    return res

###### classes

'''Holds information about one Trip of a vehicle from its start stop to its terminus.'''
class Trip:
    def __init__(self, trip_id: str, line):
        self.trip_id = trip_id
        self.route_id = line['route_id']
        self.trip_headsign = line['trip_headsign']
        self._stops: Optional[List[StopTime]] = None
    
    @property
    def stops(self):
        '''Get a list of StopTimes this Trip stops at. Generated just in time, only if needed. Access with trip.stops'''
        if self._stops is not None:
            return self._stops
        self._stops = []
        for stop_time in stop_times_by_tripid[self.trip_id]:
            self._stops.append(stop_time)


class StopTime:
    def __init__(self, trip_id: str, arrival_time: str, departure_time: str, stop_id: str, stop_sequence: str) -> None:
        self.trip_id = trip_id
        self.arrival_time = parse_time(arrival_time)
        self.departure_time = parse_time(departure_time)
        self.stop_id = stop_id
        self.stop_sequence = int(stop_sequence)


class Stop:
    def __init__(self, stop_id: str, stop_name: str, parent_station: str) -> None:
        self.stop_id = stop_id
        self.stop_name = stop_name
        self.parent_station = parent_station
        if parent_station not in stops_by_canonical_id:
            stops_by_canonical_id[parent_station] = [stop_id]
        else:
            stops_by_canonical_id[parent_station].append(stop_id)
    
    def get_canonical(self) -> "Stop":
        if len(self.parent_station) > 0:
            return stops[self.parent_station]
        else:
            return self
    
    def __str__(self) -> str:
        return self.stop_name

###### loading

def load_file(filename: str):
    with open(filename) as file:
        reader = csv.DictReader(file, quotechar='"', delimiter=",")
        return list(reader)


def load_trips(filename: str) -> Dict[TripId, Trip]:
    with open(filename) as file:
        trips_raw = csv.DictReader(file, quotechar='"', delimiter=",")
        res = dict()
        for trip_raw in trips_raw:
            # the header gets parsed weird because the file starts with a unicode ZERO WIDTH NO-BREAK SPACE.
            trip_raw['route_id'] = trip_raw['\ufeffroute_id']
            del trip_raw['\ufeffroute_id']
            trip = Trip(trip_raw['trip_id'], trip_raw)
            res[trip_raw['trip_id']] = trip
        return res


def load_stop_times(filename: str) -> Tuple[Dict[TripId, List["StopTime"]], Dict[StopId, List["StopTime"]]]:
    '''
    @returns tripId -> stopTime, canonical stopId -> stopTime
    '''
    with open(filename) as file:
        stop_times_raw = csv.DictReader(file, quotechar='"', delimiter=",")
        res: Dict[TripId, List["StopTime"]] = dict()
        res_stopid: Dict[StopId, List["StopTime"]] = dict()
        for raw in stop_times_raw:
            stop_time = StopTime(raw['\ufefftrip_id'], raw['arrival_time'], raw['departure_time'], raw['stop_id'], raw['stop_sequence'])
            if raw['\ufefftrip_id'] in res:
                res[raw['\ufefftrip_id']].append(stop_time)
            else:
                res[raw['\ufefftrip_id']] = [stop_time]
            if raw['stop_id'] in res_stopid:
                res_stopid[raw['stop_id']].append(stop_time)
            else:
                res_stopid[raw['stop_id']] = [stop_time]
        return res, res_stopid


def load_stops(filename: str) -> Dict[StopId, "Stop"]:
    with open(filename) as file:
        stops_raw = csv.DictReader(file, quotechar='"', delimiter=",")
        res = dict()
        for raw in stops_raw:
            stop = Stop(raw['\ufeffstop_id'], raw['stop_name'], raw['parent_station'])
            res[raw['\ufeffstop_id']] = stop
        return res


trips = load_trips("gtfs/trips.txt")
stops = load_stops("gtfs/stops.txt")
stop_times_by_tripid, stop_times_by_stopid = load_stop_times("gtfs/stop_times.txt")

###### niceties

def human_readable_time(secs_since_midnight: Time) -> str:
    hours = str(secs_since_midnight // (60 * 60))
    mins = str((secs_since_midnight % (60 * 60)) // 60)
    secs = str(secs_since_midnight % 60)
    return f'{hours.zfill(2)}:{mins.zfill(2)}:{secs.zfill(2)}'

def human_readable_visit(moment: Tuple[StopId, Tuple[StopId, Time]]) -> str:
    stopid, o = moment
    origin, secs_since_midnight = o
    return f'{stops[stopid]} at {human_readable_time(secs_since_midnight)} from {stops[origin]}'

def human_readable_stop(stopid: str) -> str:
    return str(stops[stopid])


###### core functionality

def leaves_from_stop(stop_id: StopId, currtime: Time, max_wait=20*60) -> List[Departure]:
    res: List[Departure] = []
    canonical_stop_id = canonical(stop_id)
    for stop_id in stops_by_canonical_id[canonical_stop_id]:
        for stop_time in stop_times_by_stopid.get(stop_id, []):
            if stop_time.departure_time > currtime and \
                max_wait + currtime < stop_time.departure_time:
                new = stop_time.departure_time, stop_time.trip_id
                res.append(new)
    return res

# get all possible disembarkements from a connection you jumped on
# origin is only for path tracking
def get_arrivals_from_departure(departure: Departure, origin: StopTime) -> List[Moment]:
    departure_time, trip_id = departure
    res: List[Moment] = []
    for stop_time in stop_times_by_tripid[trip_id]:
        if stop_time.arrival_time > departure_time:
            arrival = stop_time.arrival_time, stop_time.stop_id, origin
            res.append(arrival)
    return res


def canonical(stopid: StopId) -> StopId:
    return stops[stopid].get_canonical().stop_id
