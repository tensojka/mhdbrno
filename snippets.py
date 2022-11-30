import csv
import time

def load_stops(filename: str):
    # This is actually a very inefficient way to store the results, you might want to store them in a Dict for handy lookups.
    # The purpose of this snippet is to show you how to read a CSV, not what data type to use internally.
    res = []
    with open(filename) as file:
        reader = csv.DictReader(file, quotechar='"', delimiter=",")
        for row in reader:
            # the header gets parsed weird because the file starts with a unicode ZERO WIDTH NO-BREAK SPACE.
            # this is why the stop_id key is so weird
            res.append((row["\ufeffstop_id"], row["stop_name"], row["parent_station"]))
    return res

# parse stop time from stop_times.txt
def read_stop_time(inp):
    # strftime to parse
    return time.strptime(inp, "%H:%M:%S")
