import csv
from sgrequests import SgRequests
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("victoriassecret_com")

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


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
    urls = [
        "https://api.victoriassecret.com/stores/v1/search?countryCode=CA",
        "https://api.victoriassecret.com/stores/v1/search?countryCode=US",
        "https://api.victoriassecret.com/stores/v1/search?countryCode=GB",
    ]
    for url in urls:
        logger.info(url)
        r = session.get(url, headers=headers)
        array = json.loads(r.content)
        for item in array:
            store = item["storeId"]
            purl = "https://www.victoriassecret.com/store-locator#store/" + store
            name = item["name"]
            add = item["address"]["streetAddress1"]
            city = item["address"]["city"]
            state = item["address"]["region"]
            zc = item["address"]["postalCode"]
            phone = item["address"]["phone"]
            lat = item["latitudeDegrees"]
            lng = item["longitudeDegrees"]
            typ = (
                str(item["productLines"])
                .replace("[", "")
                .replace("]", "")
                .replace("u'", "")
                .replace("'", "")
            )
            country = item["address"]["countryCode"]
            website = "victoriassecret.com"
            hours = ""
            lurl = "https://api.victoriassecret.com/stores/v1/store/" + store
            r2 = session.get(lurl, headers=headers)
            logger.info(lurl)
            week = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
            for day in json.loads(r2.content)["hours"]:
                if hours == "":
                    hours = (
                        week[day["day"] - 1] + ": " + day["open"] + "-" + day["close"]
                    )
                else:
                    hours = (
                        hours
                        + "; "
                        + week[day["day"] - 1]
                        + ": "
                        + day["open"]
                        + "-"
                        + day["close"]
                    )
            if typ == "":
                typ = "<MISSING>"
            if lat == "":
                lat = "<MISSING>"
                lng = "<MISSING>"
            if hours == "":
                hours = "<MISSING>"
            if "000" in phone:
                phone = "<MISSING>"
            if phone == "":
                phone = "<MISSING>"
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

    url = "https://api.victoriassecret.com/categories/v9/page?categoryId=3d2035d0-33e8-4eb3-933b-57b3ff481d7a&brand=vs&isPersonalized=true&activeCountry=US&cid=&platform=web&deviceType=&platformType=&perzConsent=true&tntId=87a6ce6e-f60b-4ac1-b2d6-df27b22d64ca.34_0&screenWidth=1920&screenHeight=1080"
    r = session.get(url, headers=headers)
    typ = "<MISSING>"
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if '"storeId\\":' in line:
            items = line.split('"storeId\\":')
            for item in items:
                if 'name\\":\\"' in item:
                    website = "victoriassecret.com"
                    purl = "<MISSING>"
                    store = item.split(",")[0]
                    name = item.split('name\\":\\"')[1].split('\\"')[0]
                    add = item.split('"streetAddress1\\":\\"')[1].split('\\"')[0]
                    city = item.split('"city\\":\\"')[1].split('\\"')[0]
                    zc = item.split('"postalCode\\":\\"')[1].split('\\"')[0]
                    lat = item.split('"latitudeDegrees\\":')[1].split(",")[0]
                    lng = item.split('"longitudeDegrees\\":')[1].split(",")[0]
                    hours = "<MISSING>"
                    state = "<MISSING>"
                    country = item.split('countryCode\\":\\"')[1].split('\\"')[0]
                    try:
                        phone = item.split('"phone\\":\\"')[1].split('\\"')[0]
                    except:
                        phone = "<MISSING>"
                    if add == "":
                        add = name
                    if zc == "":
                        zc = "<MISSING>"
                    if country != "GBR":
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
