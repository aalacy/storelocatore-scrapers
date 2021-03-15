import csv
from sgrequests import SgRequests
from sgzip.dynamic import DynamicZipSearch, SearchableCountries
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("walmart_ca")

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

search = DynamicZipSearch(
    country_codes=[SearchableCountries.CANADA],
    max_radius_miles=20,
    max_search_results=25,
)


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
    for code in search:
        logger.info(("Pulling Zip Code %s..." % code))
        url = (
            "https://www.walmart.ca/en/stores-near-me/api/searchStores?singleLineAddr="
            + code.replace(" ", "")
        )
        website = "walmart.ca"
        typ = "Walmart"
        session = SgRequests()
        r2 = session.get(url, headers=headers, timeout=15)
        if r2.encoding is None:
            r2.encoding = "utf-8"
        for line2 in r2.iter_lines(decode_unicode=True):
            if '"stores":[{"distance":' in line2:
                items = line2.split('{"distance":')
                for item in items:
                    if '"address":{' in item:
                        hours = ""
                        name = item.split('"displayName":"')[1].split('"')[0]
                        store = item.split('"id":')[1].split(",")[0]
                        loc = (
                            "https://www.walmart.ca/en/stores-near-me/"
                            + name.replace(" ", "-").lower()
                            + "-"
                            + store
                        )
                        add = item.split('"address1":"')[1].split('"')[0]
                        city = item.split('"city":"')[1].split('"')[0]
                        state = item.split('"state":"')[1].split('"')[0]
                        phone = item.split('"phone":"')[1].split('"')[0]
                        lat = item.split('"latitude":')[1].split(",")[0]
                        lng = item.split('"longitude":')[1].split("}")[0]
                        zc = item.split('"postalCode":"')[1].split('"')[0]
                        days = (
                            item.split('"regularHours":[')[1]
                            .split("]},")[0]
                            .split('"start":"')
                        )
                        for day in days:
                            if '"day":"' in day:
                                if '"closed":true' in day:
                                    hrs = (
                                        day.split('"day":"')[1].split('"')[0]
                                        + ": Closed"
                                    )
                                else:
                                    hrs = (
                                        day.split('"day":"')[1].split('"')[0]
                                        + ": "
                                        + day.split('"')[0]
                                        + "-"
                                        + day.split('"end":"')[1].split('"')[0]
                                    )
                                if hours == "":
                                    hours = hrs
                                else:
                                    hours = hours + "; " + hrs
                        country = "CA"
                        if "Supercentre" in name:
                            typ = "Supercenter"
                        if "Neighborhood Market" in name:
                            typ = "Neighborhood Market"
                        if hours == "":
                            hours = "<MISSING>"
                        if add != "" and store not in ids:
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


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
