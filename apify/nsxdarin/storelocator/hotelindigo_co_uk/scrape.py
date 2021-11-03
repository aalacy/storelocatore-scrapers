import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("hotelindigo_co_uk")

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
    alllocs = []
    cities = []
    urls = ["https://www.ihg.com/hotelindigo/destinations/gb/en/united-kingdom-hotels"]
    for url in urls:
        r = session.get(url, headers=headers)
        if r.encoding is None:
            r.encoding = "utf-8"
        for line in r.iter_lines(decode_unicode=True):
            if "Hotels</span></a>" in line or "hotels</span></a>" in line:
                cities.append(line.split('href="')[1].split('"')[0])
    for city in cities:
        logger.info(("Pulling City %s..." % city))
        r3 = session.get(city, headers=headers)
        if r3.encoding is None:
            r3.encoding = "utf-8"
        for line3 in r3.iter_lines(decode_unicode=True):
            if (
                "https://www.ihg.com/hotelindigo/hotels/" in line3
                and '{"@context":"https://www.schema.org"' in line3
                and '"@type":"Brand","name":"Hotel Indigo",' in line3
            ):
                lurl = line3.split('"url":"')[1].split('"')[0]
                if lurl not in alllocs:
                    alllocs.append(lurl)
                    website = "hotelindigo.co.uk"
                    typ = "Hotel"
                    hours = "<MISSING>"
                    name = line3.split('"name":"')[1].split('"')[0]
                    add = line3.split('"streetAddress":"')[1].split('"')[0]
                    city = line3.split('"addressLocality":"')[1].split('"')[0]
                    try:
                        state = line3.split('"addressRegion":"')[1].split('"')[0]
                    except:
                        state = "<MISSING>"
                    zc = line3.split('"postalCode":"')[1].split('"')[0]
                    country = "GB"
                    try:
                        phone = line3.split('"telephone":"')[1].split('"')[0]
                    except:
                        phone = "<MISSING>"
                    lat = line3.split(',"latitude":')[1].split(",")[0]
                    lng = line3.split('"longitude":')[1].split("}")[0]
                    store = lurl.replace("/hoteldetail", "").rsplit("/", 1)[1]
                    if (
                        store == "pdxvc"
                        or store == "omasd"
                        or store == "nycfq"
                        or store == "hougo"
                    ):
                        hours = ""
                    else:
                        phone = phone.replace("+5", "").strip()
                        yield [
                            website,
                            lurl,
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
