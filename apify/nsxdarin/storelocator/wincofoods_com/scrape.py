import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
    "x-csrf-token": "ae618debb03189714dffd32b4a92ac2065bb298fa6aee086dbe3debf6b28cf64",
    "cookie": "__cfduid=d3f0ad60c59bf494146d9559d50011da91608677359; SSESS8b7f44864f67025d34bfcc2502aa6dad=LFEGEO2tyoA5vPTP-KRscjaZNpvgodX69xvskLK-HK0; Thin-Proxy=1; has_js=1; session=1608677361820.765gila; _ga=GA1.2.907230235.1608677362; _gid=GA1.2.492763197.1608677362; Srn-Auth-Token=10e7801c20ba9b8469266ef60364ecc1c0b32d498552c45240df945757f2d621; _gat_UA-107931429-1=1; _gat_UA-18308088-1=1; XSRF-TOKEN=ae618debb03189714dffd32b4a92ac2065bb298fa6aee086dbe3debf6b28cf64",
}

logger = SgLogSetup().get_logger("wincofoods_com")


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
    url = "https://www.wincofoods.com/proxy/store/getall?store_type_ids=1,2,3"
    r = session.get(url, headers=headers)
    website = "wincofoods.com"
    typ = "<MISSING>"
    country = "US"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if '"locationID":"' in line:
            items = line.split('"locationID":"')
            for item in items:
                if '"store_number":"' in item:
                    store = item.split('"')[0]
                    loc = "https://www.wincofoods.com/stores/" + store
                    name = item.split('"storeName":"')[1].split('"')[0]
                    add = item.split('"address":"')[1].split('"')[0]
                    city = item.split('"city":"')[1].split('"')[0]
                    state = item.split('"state":"')[1].split('"')[0]
                    zc = item.split('"zip":"')[1].split('"')[0]
                    lat = item.split('"latitude":')[1].split(",")[0]
                    lng = item.split('"longitude":')[1].split(",")[0]
                    phone = item.split('"phone":"')[1].split('"')[0]
                    hours = (
                        "Sun: "
                        + item.split('{"day":0')[1].split('"open":"')[1].split('"')[0]
                        + "-"
                        + item.split('{"day":0')[1].split('"close":"')[1].split('"')[0]
                    )
                    hours = (
                        hours
                        + "; Mon: "
                        + item.split('{"day":1')[1].split('"open":"')[1].split('"')[0]
                        + "-"
                        + item.split('{"day":1')[1].split('"close":"')[1].split('"')[0]
                    )
                    hours = (
                        hours
                        + "; Tue: "
                        + item.split('{"day":2')[1].split('"open":"')[1].split('"')[0]
                        + "-"
                        + item.split('{"day":2')[1].split('"close":"')[1].split('"')[0]
                    )
                    hours = (
                        hours
                        + "; Wed: "
                        + item.split('{"day":3')[1].split('"open":"')[1].split('"')[0]
                        + "-"
                        + item.split('{"day":3')[1].split('"close":"')[1].split('"')[0]
                    )
                    hours = (
                        hours
                        + "; Thu: "
                        + item.split('{"day":4')[1].split('"open":"')[1].split('"')[0]
                        + "-"
                        + item.split('{"day":4')[1].split('"close":"')[1].split('"')[0]
                    )
                    hours = (
                        hours
                        + "; Fri: "
                        + item.split('{"day":5')[1].split('"open":"')[1].split('"')[0]
                        + "-"
                        + item.split('{"day":5')[1].split('"close":"')[1].split('"')[0]
                    )
                    hours = (
                        hours
                        + "; Sat: "
                        + item.split('{"day":6')[1].split('"open":"')[1].split('"')[0]
                        + "-"
                        + item.split('{"day":6')[1].split('"close":"')[1].split('"')[0]
                    )
                    hours = hours.replace("24 Hours-", "24 Hours")
                    if phone == "":
                        phone = "<MISSING>"
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
