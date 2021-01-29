import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("mybpstation_com")

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


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
    ids = []
    url = ""
    for x in range(30, 100):
        for y in range(-60, -126, -1):
            xlat = float(float(x) / 2)
            lats = xlat
            latn = xlat + 1
            lnge = y
            lngw = y - 1
            logger.info((str(xlat) + "," + str(y)))
            url = (
                "https://bpretaillocator.geoapp.me/api/v1/locations/within_bounds?sw%5B%5D="
                + str(lats)
                + "&sw%5B%5D="
                + str(lngw)
                + "&ne%5B%5D="
                + str(latn)
                + "&ne%5B%5D="
                + str(lnge)
                + "&autoload=true&travel_mode=driving&avoid_tolls=false&avoid_highways=false&show_stations_on_route=true&corridor_radius=25&key=AIzaSyDHlZ-hOBSpgyk53kaLADU18wq00TLWyEc&format=json"
            )
            r = session.get(url, headers=headers)
            if r.encoding is None:
                r.encoding = "utf-8"
            for line in r.iter_lines(decode_unicode=True):
                if '{"id":"' in line:
                    items = line.split('{"id":"')
                    for item in items:
                        if '"name":"' in item:
                            name = item.split('"name":"')[1].split('"')[0]
                            lat = item.split('"lat":')[1].split(",")[0]
                            lng = item.split('"lng":')[1].split(",")[0]
                            add = item.split('"address":"')[1].split('"')[0]
                            city = item.split('"city":"')[1].split('"')[0]
                            state = item.split('"state":"')[1].split('"')[0]
                            zc = item.split('"postcode":"')[1].split('"')[0]
                            country = item.split('"country_code":"')[1].split('"')[0]
                            phone = item.split('"telephone":"')[1].split('"')[0]
                            try:
                                typ = item.split('"site_brand":"')[1].split('"')[0]
                            except:
                                typ = "<MISSING>"
                            website = "mybpstation.com"
                            loc = "<MISSING>"
                            store = "<MISSING>"
                            storeinfo = name + "|" + add + "|" + city + "|" + lat
                            hours = ""
                            if '"opening_hours":[]' in item:
                                hours = "<MISSING>"
                            else:
                                days = (
                                    item.split('"opening_hours":[')[1]
                                    .split(',"open_status":"')[0]
                                    .split('"days":["')
                                )
                                for day in days:
                                    if '"hours":[["' in day:
                                        hrs = (
                                            day.split("]")[0]
                                            .replace('"', "")
                                            .replace(",", "-")
                                            + ": "
                                            + day.split('"hours":[["')[1]
                                            .split("]")[0]
                                            .replace('"', "")
                                            .replace(",", "-")
                                        )
                                        if hours == "":
                                            hours = hrs
                                        else:
                                            hours = hours + "; " + hrs
                            if phone == "":
                                phone = "<MISSING>"
                            if storeinfo not in ids and country == "US":
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
                                ids.append(storeinfo)


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
