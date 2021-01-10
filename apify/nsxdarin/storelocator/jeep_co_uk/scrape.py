import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("jeep_co_uk")


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
    url = "https://dealerlocator.fiat.com/geocall/RestServlet?jsonp=callback&mkt=3112&brand=57&func=finddealerxml&serv=sales&track=1&x=-3.1911&y=51.46691&rad=1000&drl=1&_=1607097768896"
    r = session.get(url, headers=headers)
    website = "jeep.co.uk"
    country = "GB"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if '{"PP":0,"' in line:
            items = line.split('{"PP":0,"')
            for item in items:
                if "N_CAMPAIGN9" in item:
                    zc = item.split('"ZIPCODE":"')[1].split('"')[0]
                    typ = "<MISSING>"
                    store = "<MISSING>"
                    name = item.split('"COMPANYNAM":"')[1].split('"')[0]
                    loc = item.split(',"WEBSITE":"')[1].split('"')[0]
                    add = item.split(',"ADDRESS":"')[1].split('"')[0]
                    city = item.split('"TOWN":"')[1].split('"')[0]
                    state = "<MISSING>"
                    phone = item.split(',"TEL_1":"')[1].split('"')[0]
                    lng = item.split('"XCOORD":')[1].split(",")[0]
                    lat = item.split('"YCOORD":')[1].split(",")[0]
                    days = item.split('"DATEWEEK":"')
                    hours = ""
                    for day in days:
                        if '"MORNING_FROM":"' in day:
                            try:
                                hrs = (
                                    day.split('"')[0]
                                    + ": "
                                    + day.split('"MORNING_FROM":"')[1].split('"')[0]
                                    + "-"
                                    + day.split('"AFTERNOON_TO":"')[1].split('"')[0]
                                )
                            except:
                                hrs = (
                                    day.split('"')[0]
                                    + ": "
                                    + day.split('"MORNING_FROM":"')[1].split('"')[0]
                                    + "-"
                                    + day.split('"MORNING_TO":"')[1].split('"')[0]
                                )
                            if hours == "":
                                hours = hrs
                            else:
                                hours = hours + "; " + hrs
                    if "." not in loc:
                        loc = "<MISSING>"
                    if phone == "":
                        phone = "<MISSING>"
                    if hours == "":
                        hours = "<MISSING>"
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
