import csv
from sgrequests import SgRequests
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("chuckecheese_com")

session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
    "Content-Type": "application/json; charset=UTF-8",
    "Authorization": "Basic TG9jYXRpb246OUQ2QjFCREEtRDVDNC00Q0VDLTgxQTktOEUzRTU2OUVCNENC",
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
    locs = []
    coord = [
        "18,-66",
        "60,-150",
        "20,-155",
        "45,-120",
        "45,-115",
        "35,-120",
        "35,-115",
        "45,-110",
        "35,-110",
        "45,-105",
        "35,-105",
        "45,-100",
        "35,-100",
        "45,-95",
        "35,-95",
        "45,-90",
        "35,-90",
        "45,-85",
        "35,-85",
        "45,-80",
        "35,-80",
        "45,-75",
        "35,-75",
        "45,-70",
        "35,-70",
    ]
    coord.append("50,-120")
    coord.append("50,-115")
    coord.append("50,-110")
    coord.append("50,-105")
    coord.append("50,-100")
    coord.append("50,-95")
    coord.append("50,-90")
    coord.append("50,-85")
    coord.append("50,-80")
    coord.append("50,-75")
    coord.append("50,-70")
    coord.append("55,-120")
    coord.append("55,-115")
    coord.append("55,-110")
    coord.append("55,-105")
    coord.append("55,-100")
    coord.append("55,-95")
    coord.append("55,-90")
    coord.append("55,-85")
    coord.append("55,-80")
    coord.append("55,-75")
    coord.append("55,-70")
    for xy in coord:
        x = xy.split(",")[0]
        y = xy.split(",")[1]
        logger.info(("%s-%s..." % (x, y)))
        url = "https://z1-prod-cec-services-location.azurewebsites.net/api/cec/locations/search"
        payload = {"latitude": x, "longitude": y, "radius": "500"}
        r = session.post(url, headers=headers, data=json.dumps(payload))
        if r.encoding is None:
            r.encoding = "utf-8"
        for line in r.iter_lines(decode_unicode=True):
            if '"website":"' in line:
                items = line.split('"account_id":"')
                for item in items:
                    if "yelp_accuracy_score" in item:
                        store = item.split('"storeId":')[1].split(",")[0]
                        if store not in locs:
                            locs.append(store)
                            website = "chuckecheese.com"
                            add = item.split('"address":"')[1].split('"')[0]
                            country = "US"
                            city = item.split('"locality":"')[1].split('"')[0]
                            state = item.split('"region":"')[1].split('"')[0]
                            lat = item.split('"latitude":"')[1].split('"')[0]
                            lng = item.split('"longitude":"')[1].split('"')[0]
                            phone = item.split('"phone":"')[1].split('"')[0]
                            loc = item.split('"website":"')[1].split('"')[0]
                            zc = item.split('"postcode":"')[1].split('"')[0]
                            typ = "<MISSING>"
                            name = "Chuck E. Cheese " + city + ", " + state
                            hours = item.split('"store_hours":"')[1].split('"')[0]
                            hours = hours.replace("1,", "Mon: ")
                            hours = hours.replace(";2,", "; Tue: ")
                            hours = hours.replace(";3,", "; Wed: ")
                            hours = hours.replace(";4,", "; Thu: ")
                            hours = hours.replace(";5,", "; Fri: ")
                            hours = hours.replace(";6,", "; Sat: ")
                            hours = hours.replace(";7,", "; Sun: ")
                            hours = hours.replace(",", "-")
                            hours = hours[:-1]
                            if hours == "":
                                hours = "<MISSING>"
                            if "https://" not in loc:
                                loc = "https://" + loc
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

        logger.info(("Found %s Locations..." % str(len(locs))))


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
