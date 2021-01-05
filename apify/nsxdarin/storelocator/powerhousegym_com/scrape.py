import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("powerhousegym_com")


def write_output(data):
    with open("data.csv", mode="w") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )
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
        for row in data:
            writer.writerow(row)


def fetch_data():
    urls = [
        "https://powerhousegym.com/locations/?country=united-states&zip_code=&radius=25",
        "https://powerhousegym.com/locations/?country=canada&zip_code=&radius=25",
    ]
    for url in urls:
        r = session.get(url, headers=headers)
        website = "powerhousegym.com"
        typ = "<MISSING>"
        country = "US"
        hours = "<MISSING>"
        store = "<MISSING>"
        if "canada" in url:
            country = "CA"
        logger.info("Pulling Stores")
        lines = r.iter_lines()
        for line in lines:
            line = str(line.decode("utf-8"))
            if "myLatlng = new google.maps.LatLng(" in line:
                lat = line.split("myLatlng = new google.maps.LatLng(")[1].split(",")[0]
                lng = line.split(", ")[1].split(")")[0]
            if "<p><span class='bold' style='color:red;'>" in line:
                name = line.split("<p><span class='bold' style='color:red;'>")[1].split(
                    "<"
                )[0]
                city = name.split(",")[0]
                state = name.split(",")[1].strip()
                zc = "<MISSING>"
                g = next(lines)
                g = str(g.decode("utf-8"))
                add = g.split(">")[1].split("<")[0]
                g = next(lines)
                g = str(g.decode("utf-8"))
                phone = g.split(">")[1].split("<")[0]
            if "Visit Gym Website</a></p>" in line:
                try:
                    loc = line.split("href='")[1].split("'")[0]
                except:
                    loc = "<MISSING>"
            if "new google.maps.InfoWindow({" in line:
                if "Coming" not in phone:
                    if phone == "":
                        phone = "<MISSING>"
                    if "aldergrove" in name.lower():
                        loc = "https://powerhousegym.com/locations/aldergrove-bc/"
                    yield [
                        website,
                        loc,
                        name,
                        add,
                        city,
                        state,
                        zc,
                        country,
                        store,
                        phone,
                        typ,
                        lat,
                        lng,
                        hours,
                    ]


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
