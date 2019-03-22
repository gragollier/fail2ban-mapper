import re
import requests
import argparse
import json
import csv
from tqdm import tqdm
from mpl_toolkits.basemap import Basemap
import matplotlib
import matplotlib.pyplot as plt
import numpy as np


class Location:
    lat = 0.0
    lon = 0.0

    def __init__(self, lat, lon):
        self.lat = lat
        self.lon = lon

    def __str__(self):
        return (f"{self.lat}, {self.lon}")


def main():
    (file, export_file, headless, api_key) = parse_arguments()

    ip_regex = re.compile(r"Ban \d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}")

    banned_ips = []

    with open(file, 'r') as f:
        print("Reading and parsing log file")
        for line in tqdm(f, unit=" lines"):
            match = ip_regex.search(line)
            if match:
                banned_ips.append(match.group().split(' ')[1])

    banned_urls = list(
        map(lambda x: f"http://api.ipstack.com/{x}?access_key={api_key}", banned_ips))

    locs = []

    print("\nLooking up IP address location information")
    for url in tqdm(banned_urls):
        response = requests.get(url)
        response = json.loads(response.text)
        try:
            lat = float(response['latitude'])
            lon = float(response['longitude'])
            locs.append(Location(lat, lon))
        except KeyError:
            print("\nIt appears either the geolocation service is down or you've reached your daily quota, we'll stop getting location data now")
            break
        except TypeError:
            pass

    if (export_file):
        with open(export_file, 'w') as f:
            csv_writer = csv.writer(f, delimiter=',')
            print(f"\nWriting location data to {export_file}")
            for location in tqdm(locs):
                csv_writer.writerow([location.lat, location.lon])

    print("\nPlotting Chart")
    plot_locations(locs, headless)


def plot_locations(locations, headless):
    # Plotting based off of Engineer's Maker Portal's Mapping guide (https://gist.github.com/engineersportal/cbcd749142b7d1aff338f979eb64fe92#file-asos_elevation_mapper-py)
    zoom_scale = 5

    lats = list(map(lambda x: x.lat, locations))
    lons = list(map(lambda x: x.lon, locations))

    bbox = [np.min(lats)-zoom_scale, np.max(lats)+zoom_scale,
            np.min(lons)-zoom_scale, np.max(lons)+zoom_scale]

    plt.title("Fail2Ban Banned IP Addresses")

    # Define the projection, scale, the corners of the map, and the resolution.
    m = Basemap(projection='merc', llcrnrlat=bbox[0], urcrnrlat=bbox[1],
                llcrnrlon=bbox[2], urcrnrlon=bbox[3], lat_ts=10, resolution='i')

    # Draw coastlines and fill continents and water with color
    m.drawcoastlines()
    m.fillcontinents(color='#CCCCCC', lake_color='lightblue')

    # draw parallels, meridians, and color boundaries
    m.drawparallels(np.arange(bbox[0], bbox[1],
                              (bbox[1]-bbox[0])/5), labels=[1, 0, 0, 0])
    m.drawmeridians(np.arange(
        bbox[2], bbox[3], (bbox[3]-bbox[2])/5), labels=[0, 0, 0, 1], rotation=15)
    m.drawmapboundary(fill_color='lightblue')

    cmap = plt.get_cmap('seismic')

    for ii in range(0, len(lats)):
        x, y = m(lons[ii], lats[ii])
        plt.plot(x, y, 3, marker='o', color=cmap(int(200)))

    plt.savefig('fail2ban_map.png', format='png', dpi=500, transparent=False)
    if(not headless):
        plt.show()


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Parses fail2ban log file and plots banned IP Addresses")

    parser.add_argument('-f', '--file', action="store", default="/var/log/fail2ban.log", dest="input_file",
                        help="Fail2Ban log file to parse, if this argument is not provided it defaults to /var/log/fail2ban.log")

    parser.add_argument('-o', '--output-file', action="store", default="", dest="export_file",
                        help="Where to store output csv of location information")

    parser.add_argument('--headless',
                        action='store_true', dest='headless', help="Run without displaying graph, ideal for servers without a desktop environment")

    requiredNamed = parser.add_argument_group('required named arguments')
    requiredNamed.add_argument('-a', '--api-key', help='IP Stack API Key, visit their website for more information', dest="api_key", required=True)

    args = parser.parse_args()
    return (args.input_file, args.export_file, args.headless, args.api_key)


if __name__ == '__main__':
    main()
