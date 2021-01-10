import csv
from sgzip.dynamic import DynamicZipSearch, SearchableCountries
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("ccfi_com__cash1today")


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


search = DynamicZipSearch(
    country_codes=[SearchableCountries.USA],
    max_radius_miles=100,
    max_search_results=100,
)

session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36"
}


def fetch_data():
    ids = []
    for zipcode in search:
        logger.info(("Pulling Postal Code %s..." % zipcode))
        url = "https://www.ccfi.com/ajax/stores.php?zip=" + zipcode + "&distance=all"
        r = session.get(url, headers=headers)
        lines = r.iter_lines()
        website = "ccfi.com/cash1today"
        for line in lines:
            line = str(line.decode("utf-8"))
            if '{"lat":"' in line:
                items = line.split('{"lat":"')
                for item in items:
                    if '"lng":"' in item:
                        country = "US"
                        loc = "<MISSING>"
                        lng = item.split('"lng":"')[1].split('"')[0]
                        lat = item.split('"')[0]
                        add = item.split(',"street":"')[1].split('"')[0]
                        city = item.split('"city":"')[1].split('"')[0]
                        state = item.split('"state":"')[1].split('"')[0]
                        zc = item.split('"zip":"')[1].split('"')[0]
                        phone = item.split('"phone":"')[1].split('"')[0]
                        typ = item.split('"brand_link":"')[1].split('"')[0]
                        store = "<MISSING>"
                        hours = (
                            "Sun: "
                            + item.split('"sunday_open":"')[1].split('"')[0]
                            + "-"
                            + item.split('"sunday_close":"')[1].split('"')[0]
                        )
                        hours = (
                            hours
                            + "; Mon: "
                            + item.split('"monday_open":"')[1].split('"')[0]
                            + "-"
                            + item.split('"monday_close":"')[1].split('"')[0]
                        )
                        hours = (
                            hours
                            + "; Tue: "
                            + item.split('"tuesday_open":"')[1].split('"')[0]
                            + "-"
                            + item.split('"tuesday_close":"')[1].split('"')[0]
                        )
                        hours = (
                            hours
                            + "; Wed: "
                            + item.split('"wednesday_open":"')[1].split('"')[0]
                            + "-"
                            + item.split('"wednesday_close":"')[1].split('"')[0]
                        )
                        hours = (
                            hours
                            + "; Thu: "
                            + item.split('"thursday_open":"')[1].split('"')[0]
                            + "-"
                            + item.split('"thursday_close":"')[1].split('"')[0]
                        )
                        hours = (
                            hours
                            + "; Fri: "
                            + item.split('"friday_open":"')[1].split('"')[0]
                            + "-"
                            + item.split('"friday_close":"')[1].split('"')[0]
                        )
                        hours = (
                            hours
                            + "; Sat: "
                            + item.split('"saturday_open":"')[1].split('"')[0]
                            + "-"
                            + item.split('"saturday_close":"')[1].split('"')[0]
                        )
                        hours = hours.replace("Closed-Closed", "Closed")
                        if typ == "":
                            typ = "ccfi"
                        name = typ.title() + " - " + city
                        if lat == "":
                            lat = "<MISSING>"
                        if lng == "":
                            lng = "<MISSING>"
                        addinfo = typ + "|" + add + "|" + city + "|" + lat
                        if addinfo not in ids:
                            ids.append(addinfo)
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
