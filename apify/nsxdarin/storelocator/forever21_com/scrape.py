import csv
from sgrequests import SgRequests
import json
import sgzip
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("forever21_com")

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
    for code in sgzip.for_radius(200):
        if code != "00794":
            try:
                logger.info("Pulling Zip Code %s..." % code)
                url = (
                    "https://locations.forever21.com/modules/multilocation/?near_location="
                    + code
                    + "&limit=100&services__in=&published=1&within_business=true&threshold=20000"
                )
                r = session.get(url, headers=headers, timeout=90, stream=True)
                for item in json.loads(r.content)["objects"]:
                    if (
                        item["country_name"] == "US"
                        or item["country_name"] == "United States of America"
                    ):
                        add = item["street"]
                        try:
                            add = add + " " + item["street2"]
                        except:
                            pass
                        city = item["city"]
                        country = "US"
                        website = "forever21.com"
                        typ = "<MISSING>"
                        lat = item["lat"]
                        lng = item["lon"]
                        state = item["state"]
                        loc = item["location_url"]
                        name = item["location_name"]
                        zc = item["postal_code"]
                        phone = item["phonemap"]["phone"]
                        store = item["id"]
                        hours = ""
                        hrs = str(item["formatted_hours"])
                        days = hrs.split("'content': '")
                        dc = 0
                        for day in days:
                            if "'label': '" in day:
                                dc = dc + 1
                                hrs = (
                                    day.split("'label': '")[1].split("'")[0]
                                    + ": "
                                    + day.split("'")[0]
                                )
                                if hours == "":
                                    hours = hrs
                                else:
                                    if dc <= 7:
                                        hours = hours + "; " + hrs
                        if hours == "":
                            hours = "<MISSING>"
                        if zc == "":
                            zc = "<MISSING>"
                        hours = (
                            hours.replace("\t", "")
                            .replace("  ", " ")
                            .replace("  ", " ")
                            .replace("  ", " ")
                            .replace("  ", " ")
                            .replace("  ", " ")
                        )
                        if store not in ids:
                            ids.append(store)
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
            except:
                pass


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
