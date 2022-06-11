import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("tumi_com")


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
    pages = 0
    r2 = session.get(
        "https://www.tumi.com/store-finder?q=10002&searchRadius=5000.0&page=0",
        headers=headers,
    )
    for line2 in r2.iter_lines():
        line2 = str(line2.decode("utf-8"))
        if "<p>Page 1 of " in line2:
            pages = int(line2.split("<p>Page 1 of ")[1].split("<")[0])
    logger.info("%s Pages..." % str(pages))
    for x in range(0, pages):
        url = (
            "https://www.tumi.com/store-finder?q=10002&searchRadius=5000.0&page="
            + str(x)
        )
        website = "tumi.com"
        country = "US"
        logger.info("Pulling Stores Page %s..." % str(x))
        r = session.get(url, headers=headers)
        for line in r.iter_lines():
            line = str(line.decode("utf-8"))
            if "','/store/" in line:
                store = line.split("','/store/")[1].split("?")[0]
                loc = "https://www.tumi.com/store/" + store
                typ = "<MISSING>"
                name = line.split("','")[2].split("'")[0]
                add = line.split("','','")[1].split("'")[0]
                city = line.split("','")[5]
                state = line.split("','")[6]
                zc = line.split("','")[7]
                phone = line.split("','")[8].split("'")[0]
            if 'id="pos_' in line:
                lat = (
                    line.split("','")[0]
                    .replace("\t", "")
                    .strip()
                    .replace(",", "")
                    .replace("'", "")
                )
                lng = line.split("','")[1].split("'")[0]
            if '<h2 class="boxTitle">HOURS</h2>' in line:
                hours = ""
                daycount = 0
            if 'class="day-name">' in line:
                hrs = (
                    line.split('class="day-name">')[1].split("<")[0]
                    + ": "
                    + line.split('"store-status align-right">')[1].split("<")[0]
                )
                daycount = daycount + 1
                if daycount <= 7:
                    if hours == "":
                        hours = hrs
                    else:
                        hours = hours + "; " + hrs
            if "Save as My Store</label>" in line:
                if (
                    "Ontario" in state
                    or "Alberta" in state
                    or "British Columbia" in state
                ):
                    country = "CA"
                if (
                    "Ohio" in state
                    or "California" in state
                    or "Oregon" in state
                    or "Arizona" in state
                ):
                    country = "US"
                if (
                    float(lng) < -50
                    and float(lat) > 10
                    and state != ""
                    and state != "Guatemala"
                    and state != "Distrito Federal"
                ):
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
    pages = 0
    r2 = session.get(
        "https://www.tumi.com/store-finder?q=95128&searchRadius=2500.0&page=0",
        headers=headers,
    )
    for line2 in r2.iter_lines():
        line2 = str(line2.decode("utf-8"))
        if "<p>Page 1 of " in line2:
            pages = int(line2.split("<p>Page 1 of ")[1].split("<")[0])
    logger.info("%s Pages..." % str(pages))
    for x in range(0, pages):
        url = (
            "https://www.tumi.com/store-finder?q=95128&searchRadius=2500.0&page="
            + str(x)
        )
        website = "tumi.com"
        country = "US"
        logger.info("Pulling Stores Page %s..." % str(x))
        r = session.get(url, headers=headers)
        for line in r.iter_lines():
            line = str(line.decode("utf-8"))
            if "','/store/" in line:
                store = line.split("','/store/")[1].split("?")[0]
                loc = "https://www.tumi.com/store/" + store
                typ = "<MISSING>"
                name = line.split("','")[2].split("'")[0]
                add = line.split("','','")[1].split("'")[0]
                city = line.split("','")[5]
                state = line.split("','")[6]
                zc = line.split("','")[7]
                phone = line.split("','")[8].split("'")[0]
            if 'id="pos_' in line:
                lat = (
                    line.split("','")[0]
                    .replace("\t", "")
                    .strip()
                    .replace(",", "")
                    .replace("'", "")
                )
                lng = line.split("','")[1].split("'")[0]
            if '<h2 class="boxTitle">HOURS</h2>' in line:
                hours = ""
                daycount = 0
            if 'class="day-name">' in line:
                hrs = (
                    line.split('class="day-name">')[1].split("<")[0]
                    + ": "
                    + line.split('"store-status align-right">')[1].split("<")[0]
                )
                daycount = daycount + 1
                if daycount <= 7:
                    if hours == "":
                        hours = hrs
                    else:
                        hours = hours + "; " + hrs
            if "Save as My Store</label>" in line:
                if (
                    "Ontario" in state
                    or "Alberta" in state
                    or "British Columbia" in state
                ):
                    country = "CA"
                if (
                    "Ohio" in state
                    or "California" in state
                    or "Oregon" in state
                    or "Arizona" in state
                ):
                    country = "US"
                if (
                    float(lng) < -50
                    and float(lat) > 10
                    and state != ""
                    and state != "Guatemala"
                    and state != "Distrito Federal"
                ):
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
