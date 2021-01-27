import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("maverik_com")

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"
}


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
            writer.writerow(row)


def fetch_data():
    # Your scraper here
    data = []
    street_list = []
    url = "https://gateway.maverik.com/ac-loc/location/all"
    loclist = session.get(url, headers=headers).json()["locations"]
    for loc in loclist:
        if "Closed" in loc["name"]:
            continue
        title = loc["name"]
        store = loc["code"]
        if title.count("-") == 2:
            title = title.split("-", 1)[1].split("-", 1)[0]
            title = title.strip()
            title = title + " #" + store
        else:
            title = title.split("-", 1)[0]
            title = title + " #" + store
        street = loc["address"]["address1"]
        if street in street_list:
            continue
        street_list.append(street)
        city = loc["address"]["city"]
        state = loc["address"]["stateProvince"]
        pcode = loc["address"]["postalCode"]
        phone = loc["address"]["phone"]

        if phone is None:
            phone = "<MISSING>"
        try:
            lat = loc["latitude"]
            longt = loc["longitude"]
            hours = loc["hoursOfOperation"]
        except:
            lat = "<MISSING>"
            longt = "<MISSING>"
            hours = "<MISSING>"
        data.append(
            [
                "https://maverik.com/",
                "https://loyalty.maverik.com/locations/map",
                title,
                street,
                city,
                state,
                pcode,
                "US",
                store,
                phone,
                "<MISSING>",
                lat,
                longt,
                hours,
            ]
        )
    return data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
