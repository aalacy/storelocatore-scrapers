import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("uk_coach_com")


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
    for x in range(0, 100, 15):
        url = (
            "https://uk.coach.com/on/demandware.store/Sites-Coach_EU-Site/en_GB/Stores-FilterResult?firstQuery=GB_country&showRFStoreDivider=true&showRStoreDivider=true&showDStoreDivider=false&showFStoreDivider=false&start="
            + str(x)
            + "&sz=15&format=ajax"
        )
        r = session.get(url, headers=headers)
        website = "uk.coach.com"
        typ = "<MISSING>"
        country = "GB"
        logger.info("Pulling Stores")
        for line in r.iter_lines():
            line = str(line.decode("utf-8"))
            if 'meta itemprop="name" content="' in line:
                items = line.split('meta itemprop="name" content="')
                for item in items:
                    if 'data-address="' in item:
                        name = item.split('"')[0]
                        loc = "<MISSING>"
                        add = (
                            item.split('"streetAddress">')[1]
                            .split("</span>")[0]
                            .replace("<br />", "")
                            .strip()
                            .replace("  ", " ")
                        )
                        city = item.split('rop="addressLocality">')[1].split("<")[0]
                        state = "<MISSING>"
                        zc = item.split('"postalCode">')[1].split("<")[0]
                        try:
                            phone = item.split('itemprop="telephone">')[1].split("<")[0]
                        except:
                            phone = "<MISSING>"
                        phone = phone.replace("&#40;", "(").replace("&#41;", ")")
                        lat = "<MISSING>"
                        lng = "<MISSING>"
                        store = "<MISSING>"
                        hours = (
                            item.split('<span itemprop="openingHours">')[1]
                            .split("<")[0]
                            .strip()
                        )
                        name = name.replace("&amp;", "&")
                        add = add.replace("&amp;", "&")
                        name = name.replace("&#39;", "'")
                        add = add.replace("&#39;", "'")
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
