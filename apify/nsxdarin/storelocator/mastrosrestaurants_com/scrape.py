import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("mastrosrestaurants_com")


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
    url = "https://www.mastrosrestaurants.com/view-all-locations/"
    r = session.get(url, headers=headers)
    website = "mastrosrestaurants.com"
    typ = "<MISSING>"
    country = "US"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if '{"@type": "FoodEstablishment"' in line:
            items = line.split('{"@type": "FoodEstablishment"')
            for item in items:
                if '"photo":' in item:
                    locs.append(item.split('"url": "')[1].split('"')[0])
    for loc in locs:
        logger.info(loc)
        name = ""
        add = ""
        city = ""
        state = ""
        zc = ""
        store = "<MISSING>"
        phone = ""
        lat = ""
        lng = ""
        hours = ""
        r2 = session.get(loc, headers=headers)
        for line2 in r2.iter_lines():
            line2 = str(line2.decode("utf-8"))
            if "<title>" in line2:
                name = line2.split("<title>")[1].split(" |")[0]
            if ",<br>" in line2:
                add = line2.split(",<br>")[0].strip().replace("\t", "")
                city = line2.split(",<br>")[1].split(",")[0].strip()
                state = (
                    line2.split(",<br>")[1].strip().split(",")[1].strip().split(" ")[0]
                )
                zc = (
                    line2.replace("\t", "")
                    .replace("\r", "")
                    .replace("\n", "")
                    .rsplit(" ", 1)[1]
                )
            if '<a href="tel:' in line2:
                phone = line2.split('<a href="tel:')[1].split('"')[0]
            if 'gmaps-lat="' in line2:
                lat = line2.split('gmaps-lat="')[1].split('"')[0]
                lng = line2.split('-lng="')[1].split('"')[0]
            if "PM -" in line2:
                hours = (
                    line2.split("</p><p>")[1].split("<br/><")[0].replace("<br/>", "; ")
                )
        if "; Lounge" in hours:
            hours = hours.split("; Lounge")[0]
        if "; Join" in hours:
            hours = hours.split("; Join")[0]
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
