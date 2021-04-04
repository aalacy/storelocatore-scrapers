import csv
from sgrequests import SgRequests
import sgzip
from sglogging import SgLogSetup

session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
    "X-Requested-With": "XMLHttpRequest",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
}

logger = SgLogSetup().get_logger("kawasaki_com")


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
    ids = []
    for code in sgzip.for_radius(50):
        logger.info("Pulling Zip Code %s..." % code)
        url = "https://www.kawasaki.com/en-us/PurchaseTools/DealerLocator"
        payload = {"LocationFreeText": code}
        r = session.post(url, headers=headers, data=payload)
        for line in r.iter_lines():
            line = str(line.decode("utf-8"))
            if "var arrayOfDealers" in line:
                items = line.split('"Name')
                for item in items:
                    if '"City' in item:
                        website = "kawasaki.com"
                        purl = "<MISSING>"
                        name = (
                            item.split('\\":\\"')[1]
                            .split('\\",\\"Address')[0]
                            .replace("\\\\u0027", "'")
                            .replace("\\\\u0026", "&")
                        )
                        add = item.split('"Address\\":\\"')[1].split('\\",\\"Address2')[
                            0
                        ]
                        if '"Address2\\":null' not in item:
                            add = (
                                add
                                + " "
                                + item.split('"Address2\\":\\"')[1]
                                .split('\\",\\"City')[0]
                                .replace("\\\\u0027", "'")
                            )
                        city = (
                            item.split('"City\\":\\"')[1]
                            .split('\\",\\"StateOrProvince')[0]
                            .replace("\\\\u0027", "'")
                        )
                        state = item.split('"StateOrProvince\\":\\"')[1].split("\\")[0]
                        zc = item.split('"ZipCode\\":\\"')[1].split("\\")[0]
                        country = "US"
                        phone = item.split('"PhoneNumber\\":\\"')[1].split("\\")[0]
                        lat = item.split('"Latitude\\":')[1].split(",")[0]
                        lng = item.split('"Longitude\\":')[1].split(",")[0]
                        typ = "<MISSING>"
                        store = item.split('"KmcDealerNumber\\":\\"')[1].split("\\")[0]
                        hours = "<MISSING>"
                        try:
                            purl = item.split('"WebsiteUrl\\":\\"')[1].split("\\")[0]
                        except:
                            purl = "<MISSING>"
                        if purl == "":
                            purl = "<MISSING>"
                        if store not in ids:
                            ids.append(store)
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
