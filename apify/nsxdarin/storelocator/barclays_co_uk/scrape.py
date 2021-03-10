import csv
from sgrequests import SgRequests
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("barclays_co_uk")

search = DynamicGeoSearch(
    country_codes=[SearchableCountries.BRITAIN],
    max_radius_miles=None,
    max_search_results=30,
)

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
    for lat, lng in search:
        x = lat
        y = lng
        url = (
            "https://search.barclays.co.uk/content/bf/en/4_0/branches_atms?lat="
            + str(x)
            + "&lng="
            + str(y)
        )
        logger.info("%s - %s..." % (str(x), str(y)))
        website = "barclays.co.uk"
        r = session.get(url, headers=headers)
        for line in r.iter_lines():
            line = str(line.decode("utf-8"))
            if '{"distance":' in line:
                items = line.split('{"distance":')
                for item in items:
                    if ',"myDistance":' in item:
                        store = item.split('"outletId":"')[1].split('"')[0]
                        typ = item.split('"type":"')[1].split('"')[0]
                        lat = item.split('"latitude":')[1].split(",")[0]
                        lng = item.split('"longitude":')[1].split(",")[0]
                        add = item.split('"buildingNameNumber":"')[1].split('"')[0]
                        add = add + " " + item.split('"line1":"')[1].split('"')[0]
                        add = add.strip()
                        add = add + " " + item.split('"line2":"')[1].split('"')[0]
                        add = add.strip()
                        city = item.split('"town":"')[1].split('"')[0]
                        state = "<MISSING>"
                        country = item.split('"country":"')[1].split('"')[0]
                        zc = item.split('"postCode":"')[1].split('"')[0]
                        name = item.split('"line1":"')[1].split('"')[0]
                        phone = "0345 734 5345"
                        hours = (
                            "Sun: "
                            + item.split('"sunday":{"openTime":"')[1].split('"')[0]
                            + "-"
                            + item.split('"sunday":{')[1]
                            .split('"closeTime":"')[1]
                            .split('"')[0]
                        )
                        hours = (
                            hours
                            + "; Mon: "
                            + item.split('"monday":{"openTime":"')[1].split('"')[0]
                            + "-"
                            + item.split('"monday":{"')[1]
                            .split('"closeTime":"')[1]
                            .split('"')[0]
                        )
                        hours = (
                            hours
                            + "; Tue: "
                            + item.split('"tuesday":{"openTime":"')[1].split('"')[0]
                            + "-"
                            + item.split('"tuesday":{"')[1]
                            .split('"closeTime":"')[1]
                            .split('"')[0]
                        )
                        hours = (
                            hours
                            + "; Wed: "
                            + item.split('"wednesday":{"openTime":"')[1].split('"')[0]
                            + "-"
                            + item.split('"wednesday":{"')[1]
                            .split('"closeTime":"')[1]
                            .split('"')[0]
                        )
                        hours = (
                            hours
                            + "; Thu: "
                            + item.split('"thursday":{"openTime":"')[1].split('"')[0]
                            + "-"
                            + item.split('"thursday":{"')[1]
                            .split('"closeTime":"')[1]
                            .split('"')[0]
                        )
                        hours = (
                            hours
                            + "; Fri: "
                            + item.split('"friday":{"openTime":"')[1].split('"')[0]
                            + "-"
                            + item.split('"friday":{"')[1]
                            .split('"closeTime":"')[1]
                            .split('"')[0]
                        )
                        hours = (
                            hours
                            + "; Sat: "
                            + item.split('"saturday":{"openTime":"')[1].split('"')[0]
                            + "-"
                            + item.split('"saturday":{"')[1]
                            .split('"closeTime":"')[1]
                            .split('"')[0]
                        )
                        hours = hours.replace("00:00-00:00", "Closed")
                        if store not in ids and typ == "BRANCH":
                            loc = "<MISSING>"
                            country = "GB"
                            ids.append(store)
                            add = (
                                add.replace("Barclays Wealth", "")
                                .replace("Ground Floor", "")
                                .replace("Level 11", "")
                                .replace("Donegal House", "")
                                .replace("Wytham Court", "")
                            )
                            add = add.replace(",", "").strip()
                            add = add.replace("&#x2f;", "/")
                            name = name.replace("&#x2f;", "/")
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
