import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("nutrishopusa_com")


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
    letters = [
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
    url = "https://order.capriottis.com/sitemap.xml"
    r = session.get(url, headers=headers)
    website = "nutrishopusa.com"
    typ = "<MISSING>"
    country = "US"
    loc = "<MISSING>"
    logger.info("Pulling Stores")
    for letter in letters:
        logger.info(letter)
        url = "https://www.nutrishopusa.com/find-nutrishop/search?state=" + letter
        r = session.get(url, headers=headers)
        for line in r.iter_lines():
            line = str(line.decode("utf-8"))
            if '{"id":"' in line:
                items = line.split('{"id":"')
                for item in items:
                    if '"address1":"' in item and '"status":"coming_soon"' not in item:
                        name = item.split('"name":"')[1].split('"')[0].replace("\\", "")
                        store = item.split('"')[0]
                        add = item.split('"address1":"')[1].split('"')[0].strip()
                        addinfo = item.split('"address2":"')[1].split('"')[0].strip()
                        zc = addinfo.rsplit(" ", 1)[1]
                        city = addinfo.split(",")[0]
                        state = addinfo.split(",")[1].strip().split(" ")[0]
                        phone = item.split('"phone":"')[1].split('"')[0]
                        lat = item.split('"lat":"')[1].split('"')[0]
                        lng = item.split('"lon":"')[1].split('"')[0]
                        if '"1":{"start":"' in item:
                            try:
                                hours = (
                                    "Sun: "
                                    + item.split('0":{"start":"')[1].split('"')[0]
                                    + "-"
                                    + item.split('0":{"start":"')[1]
                                    .split('"end":"')[1]
                                    .split('"')[0]
                                )
                            except:
                                hours = "Sun: Closed"
                            hours = (
                                hours
                                + "; Mon: "
                                + item.split('1":{"start":"')[1].split('"')[0]
                                + "-"
                                + item.split('1":{"start":"')[1]
                                .split('"end":"')[1]
                                .split('"')[0]
                            )
                            hours = (
                                hours
                                + "; Tue: "
                                + item.split('2":{"start":"')[1].split('"')[0]
                                + "-"
                                + item.split('2":{"start":"')[1]
                                .split('"end":"')[1]
                                .split('"')[0]
                            )
                            try:
                                hours = (
                                    hours
                                    + "; Wed: "
                                    + item.split('3":{"start":"')[1].split('"')[0]
                                    + "-"
                                    + item.split('3":{"start":"')[1]
                                    .split('"end":"')[1]
                                    .split('"')[0]
                                )
                            except:
                                hours = hours + "; Wed: Closed"
                            hours = (
                                hours
                                + "; Thu: "
                                + item.split('4":{"start":"')[1].split('"')[0]
                                + "-"
                                + item.split('4":{"start":"')[1]
                                .split('"end":"')[1]
                                .split('"')[0]
                            )
                            hours = (
                                hours
                                + "; Fri: "
                                + item.split('5":{"start":"')[1].split('"')[0]
                                + "-"
                                + item.split('5":{"start":"')[1]
                                .split('"end":"')[1]
                                .split('"')[0]
                            )
                            try:
                                hours = (
                                    hours
                                    + "; Sat: "
                                    + item.split('6":{"start":"')[1].split('"')[0]
                                    + "-"
                                    + item.split('6":{"start":"')[1]
                                    .split('"end":"')[1]
                                    .split('"')[0]
                                )
                            except:
                                hours = hours + "; Sat: Closed"
                        if '"hours":[{"start":"' in item:
                            hours = (
                                "Sun: "
                                + item.split('{"start":"')[1].split('"')[0]
                                + "-"
                                + item.split('"end":"')[1].split('"')[0]
                            )
                            hours = (
                                hours
                                + "; Mon: "
                                + item.split('{"start":"')[2].split('"')[0]
                                + "-"
                                + item.split('"end":"')[2].split('"')[0]
                            )
                            hours = (
                                hours
                                + "; Tue: "
                                + item.split('{"start":"')[3].split('"')[0]
                                + "-"
                                + item.split('"end":"')[3].split('"')[0]
                            )
                            hours = (
                                hours
                                + "; Wed: "
                                + item.split('{"start":"')[4].split('"')[0]
                                + "-"
                                + item.split('"end":"')[4].split('"')[0]
                            )
                            hours = (
                                hours
                                + "; Thu: "
                                + item.split('{"start":"')[5].split('"')[0]
                                + "-"
                                + item.split('"end":"')[5].split('"')[0]
                            )
                            hours = (
                                hours
                                + "; Fri: "
                                + item.split('{"start":"')[6].split('"')[0]
                                + "-"
                                + item.split('"end":"')[6].split('"')[0]
                            )
                            hours = (
                                hours
                                + "; Sat: "
                                + item.split('{"start":"')[7].split('"')[0]
                                + "-"
                                + item.split('"end":"')[7].split('"')[0]
                            )
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
