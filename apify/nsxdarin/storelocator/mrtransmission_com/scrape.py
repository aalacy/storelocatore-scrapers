import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("mrtransmission_com")


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
    url = "https://mrtransmission.com/Places?ctr=places&act=get"
    r = session.get(url, headers=headers)
    website = "mrtransmission.com"
    typ = "<MISSING>"
    country = "US"
    store = "<MISSING>"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if '{"id":"' in line:
            items = line.split('{"id":"')
            for item in items:
                if 'typeId":"' in item:
                    zc = item.split('"code":"')[1].split('"')[0]
                    add = item.split('"street":"')[1].split('"')[0]
                    city = item.split('"city":"')[1].split('"')[0]
                    state = item.split('"region":"')[1].split('"')[0]
                    country = item.split('"country":"')[1].split('"')[0]
                    lat = item.split('"lat":')[1].split(",")[0]
                    lng = item.split('"lng":')[1].split(",")[0]
                    phone = item.split('"phone":"')[1].split('"')[0]
                    try:
                        store = item.split("#")[1].split('"')[0].strip()
                    except:
                        store = "<MISSING>"
                    loc = item.split('"url":"')[1].split('"')[0]
                    hours = item.split(',"text":"')[1].split('"')[0]
                    name = item.split('"title":"')[1].split('"')[0]
                    hours = (
                        hours.replace("<br />\\n", "; ")
                        .replace("<p>", "")
                        .replace("</p>\\n", "")
                    )
                    hours = (
                        hours.replace(" | ", "; ")
                        .replace("\t", "")
                        .replace("  ", " ")
                        .replace("  ", " ")
                        .replace("  ", " ")
                        .replace("  ", " ")
                        .replace("  ", " ")
                    )
                    hours = hours.replace("\\n", "").replace("<br/>", "; ")
                    if country == "US" or country == "CA":
                        if loc == "":
                            loc = "<MISSING>"
                        if hours == "":
                            hours = "<MISSING>"
                        if phone == "":
                            phone = "<MISSING>"
                        if add != "":
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
