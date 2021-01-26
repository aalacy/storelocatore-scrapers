import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("crossfit_com")


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
    url = "https://map.crossfit.com/getAllAffiliates.php"
    r = session.get(url, headers=headers)
    website = "crossfit.com"
    typ = "<MISSING>"
    country = "US"
    hours = "<MISSING>"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if "],[" in line:
            items = line.split("],[")
            for item in items:
                llat = item.split(",")[0].replace("[", "")
                llng = item.split(",")[1].replace("]", "")
                locs.append(
                    item.split('","')[1].split('"')[0] + "|" + llat + "|" + llng
                )
    for loc in locs:
        lurl = "https://map.crossfit.com/getAffiliateInfo.php?aid=" + loc.split("|")[0]
        store = loc.split("|")[0]
        lat = loc.split("|")[1]
        lng = loc.split("|")[2]
        logger.info(lurl)
        r2 = session.get(lurl, headers=headers)
        for line2 in r2.iter_lines():
            line2 = str(line2.decode("utf-8"))
            if '"name":"' in line2:
                name = line2.split('"name":"')[1].split('"')[0]
                try:
                    purl = line2.split('"website":"')[1].split('"')[0].replace("\\", "")
                except:
                    purl = "<MISSING>"
                add = line2.split('"address":"')[1].split('"')[0]
                city = line2.split('"city":"')[1].split('"')[0]
                try:
                    state = line2.split('"state":"')[1].split('"')[0]
                except:
                    state = "<MISSING>"
                country = line2.split('"country":"')[1].split('"')[0]
                zc = line2.split('"zip":"')[1].split('"')[0]
                try:
                    phone = line2.split('"phone":"')[1].split('"')[0]
                except:
                    phone = "<MISSING>"
        if country == "United States" or country == "Canada":
            yield [
                website,
                purl,
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
