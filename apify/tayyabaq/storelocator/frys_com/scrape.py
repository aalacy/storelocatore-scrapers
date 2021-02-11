import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re


def write_output(data):
    with open("data.csv", mode="w") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )
        # Header
        writer.writerow(
            [
                "locator_domain",
                "page_url",
                "location_name",
                "street_address",
                "city",
                "state",
                "zip",
                "country_code",
                "store_number",
                "phone",
                "location_type",
                "latitude",
                "longitude",
                "hours_of_operation",
            ]
        )
        # Body
        for row in data:
            if row:
                writer.writerow(row)


def parse_geo(url):
    lon = re.findall(r"\,(--?[\d\.]*)", url)[0]
    lat = re.findall(r"\&ll=([\d\.]*)", url)[0]
    return lat, lon


def fetch_data():
    data = []
    location_name = []
    links = []
    city = []
    street_address = []
    zipcode = []
    state = []
    latitude = []
    longitude = []
    phone = []

    base_link = "https://www.frys.com/ac/storeinfo/storelocator/?site=csfooter_B"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
    HEADERS = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=HEADERS)

    base = BeautifulSoup(req.text, "lxml")

    location = base.find(id="submenu-stores").find_all(
        "a", {"href": re.compile(r"/ac/storeinfo/.+hours-maps-directions")}
    )
    location_href = [
        "https://www.frys.com" + location[n]["href"] for n in range(0, len(location))
    ]

    for n in range(0, len(location_href)):
        link = location_href[n]        
        req = session.get(link, headers=HEADERS)
        base = BeautifulSoup(req.text, "lxml")
        title = base.find(id="text1").text.strip()
        try:
            address = list(base.find(id="address").stripped_strings)
        except:
            continue
        street = address[0]
        city = address[1].split(",")[0]
        state = address[1].split(",")[1].split()[0]
        pcode = address[1].split(",")[1].split()[1]
        phone = address[2].split("Phone ")[1]
        try:
            lat_lon = base.find("a", string="Google Map")
            lat, lon = parse_geo(str(lat_lon["href"]))
            if (lat == "") or (lat == []):
                lat = "<MISSING>"
            else:
                lat = lat
            if (lon == "") or (lon == []):
                longt = "<MISSING>"
            else:
                longt = lon
        except:
            map_link = lat_lon["href"]
            if "@" in map_link:
                at_pos = map_link.rfind("@")
                lat = map_link[at_pos + 1 : map_link.find(",", at_pos)].strip()
                
                longt =  map_link[map_link.find(",", at_pos) + 1 : map_link.find(",", at_pos + 15)
                    ].strip()
                
            else:
                try:
                    req = session.get(map_link, headers=HEADERS)
                    maps = BeautifulSoup(req.text, "lxml")
                    raw_gps = maps.find("meta", attrs={"itemprop": "image"})["content"]
                    latitude.append(
                        raw_gps[raw_gps.find("=") + 1 : raw_gps.find("%")].strip()
                    )
                    longitude.append(
                        raw_gps[raw_gps.find("-") : raw_gps.find("&")].strip()
                    )
                except:
                    lat = "<MISSING>"
                    longt = "<MISSING>"
    
        data.append(
            [
                "https://www.frys.com",
                link,
                title,
                street,
                city,
                state,
                pcode,
                "US",
                "<MISSING>",
                phone,
                "<MISSING>",
                latitude,
                longitude,
                "<INACCESSIBLE>",
            ]
        )
    return data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()

