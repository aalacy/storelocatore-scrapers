import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("volvocars_co_uk")


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
    urls = [
        "https://www.volvocars.com/data/retailer?countryCode=GB&languageCode=EN&northToSouthSearch=False&serviceType=Service&isOxp=True&sc_site=uk",
        "https://www.volvocars.com/data/retailer?countryCode=GB&languageCode=EN&northToSouthSearch=False&serviceType=Sales&isOxp=True&sc_site=uk",
    ]
    for url in urls:
        r = session.get(url, headers=headers)
        website = "volvocars.co.uk"
        typ = "<MISSING>"
        country = "GB"
        hours = "<MISSING>"
        logger.info("Pulling Stores")
        for line in r.iter_lines():
            line = str(line.decode("utf-8"))
            if '{"DealerId":"' in line:
                items = line.split('{"DealerId":"')
                for item in items:
                    if '"Name":"' in item:
                        name = item.split('"Name":"')[1].split('"')[0]
                        store = item.split('"')[0]
                        add = item.split('"AddressLine1":"')[1].split('"')[0]
                        add = add.strip()
                        city = item.split('"City":"')[1].split('"')[0]
                        state = item.split('"District":"')[1].split('"')[0]
                        zc = item.split(',"ZipCode":"')[1].split('"')[0]
                        phone = item.split('"Phone":"')[1].split('"')[0]
                        lat = item.split('"Latitude":')[1].split(",")[0]
                        lng = item.split('"Longitude":')[1].split("}")[0]
                        if '"ServiceType":"new_car_sales","OpeningHours":"' in item:
                            hours = item.split(
                                '"ServiceType":"new_car_sales","OpeningHours":"'
                            )[1].split('"')[0]
                        else:
                            hours = "<MISSING>"
                        if ',"Url":"' in item:
                            loc = item.split(',"Url":"')[1].split('"')[0]
                        else:
                            loc = "<MISSING>"
                        if store not in locs:
                            if hours == "":
                                hours = "<MISSING>"
                            locs.append(store)
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
