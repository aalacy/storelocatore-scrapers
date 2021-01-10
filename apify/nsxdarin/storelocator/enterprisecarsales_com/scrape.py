import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("enterprisecarsales_com")


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
    states = [
        "AK",
        "AL",
        "AR",
        "AS",
        "AZ",
        "CA",
        "CO",
        "CT",
        "DC",
        "DE",
        "FL",
        "GA",
        "GU",
        "HI",
        "IA",
        "ID",
        "IL",
        "IN",
        "KS",
        "KY",
        "LA",
        "MA",
        "MD",
        "ME",
        "MI",
        "MN",
        "MO",
        "MP",
        "MS",
        "MT",
        "NC",
        "ND",
        "NE",
        "NH",
        "NJ",
        "NM",
        "NV",
        "NY",
        "OH",
        "OK",
        "OR",
        "PA",
        "PR",
        "RI",
        "SC",
        "SD",
        "TN",
        "TX",
        "UM",
        "UT",
        "VA",
        "VI",
        "VT",
        "WA",
        "WI",
        "WV",
        "WY",
    ]
    for state in states:
        logger.info("Pulling State %s..." % state)
        url = (
            "https://www.enterprisecarsales.com/wp-json/jazel-auto5/v1/locations/state/"
            + state
        )
        r = session.get(url, headers=headers)
        website = "enterprisecarsales.com"
        country = "US"
        typ = "<MISSING>"
        for line in r.iter_lines():
            line = str(line.decode("utf-8"))
            if '{"StoreInfo":' in line:
                items = line.split('{"StoreInfo"')
                for item in items:
                    if '"Name":"' in item:
                        store = item.split('"Code":"')[1].split('"')[0]
                        name = item.split('"Name":"')[1].split('"')[0]
                        add = item.split('"Address1":"')[1].split('"')[0]
                        city = item.split('"City":"')[1].split('"')[0]
                        state = item.split('"State":"')[1].split('"')[0]
                        zc = item.split('"Zipcode":"')[1].split('"')[0]
                        phone = item.split('"ContactNumber":"')[1].split('"')[0]
                        ll = item.split(',"LatLon":"')[1].split('"')[0]
                        lat = ll.split(",")[0]
                        lng = ll.split(",")[1]
                        loc = "https://www.enterprisecarsales.com/location/" + store
                        hours = (
                            "Sun: "
                            + item.split('"SundayOpen":"')[1].split('"')[0]
                            + "-"
                            + item.split('"SundayClose":"')[1].split('"')[0]
                        )
                        hours = (
                            hours
                            + "; Mon: "
                            + item.split('"MondayOpen":"')[1].split('"')[0]
                            + "-"
                            + item.split('"MondayClose":"')[1].split('"')[0]
                        )
                        hours = (
                            hours
                            + "; Tue: "
                            + item.split('"TuesdayOpen":"')[1].split('"')[0]
                            + "-"
                            + item.split('"TuesdayClose":"')[1].split('"')[0]
                        )
                        hours = (
                            hours
                            + "; Wed: "
                            + item.split('"WednesdayOpen":"')[1].split('"')[0]
                            + "-"
                            + item.split('"WednesdayClose":"')[1].split('"')[0]
                        )
                        hours = (
                            hours
                            + "; Thu: "
                            + item.split('"ThursdayOpen":"')[1].split('"')[0]
                            + "-"
                            + item.split('"ThursdayClose":"')[1].split('"')[0]
                        )
                        hours = (
                            hours
                            + "; Fri: "
                            + item.split('"FridayOpen":"')[1].split('"')[0]
                            + "-"
                            + item.split('"FridayClose":"')[1].split('"')[0]
                        )
                        hours = (
                            hours
                            + "; Sat: "
                            + item.split('"SaturdayOpen":"')[1].split('"')[0]
                            + "-"
                            + item.split('"SaturdayClose":"')[1].split('"')[0]
                        )
                        hours = hours.replace("Closed-Closed", "Closed")
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
