import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("redlion_com__canadas-best-value-inn")


session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def write_output(data):
    with open("data.csv", mode="w") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )
        writer.writerow(
            [
                "locator_domain",
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
    url = "https://www.redlion.com/sitemap.xml"
    locs = []
    r = session.get(url, headers=headers)
    if r.encoding is None:
        r.encoding = "utf-8"
    lines = r.iter_lines(decode_unicode=True)
    for line in lines:
        if "<loc>https://www.redlion.com/canadas-best-value-inn" in line:
            lurl = line.split("<loc>")[1].split("<")[0]
            if lurl != "https://www.redlion.com/canadas-best-value-inn":
                locs.append(line.split("<loc>")[1].split("<")[0])
    for loc in locs:
        logger.info(("Pulling Location %s..." % loc))
        r2 = session.get(loc, headers=headers)
        if r2.encoding is None:
            r2.encoding = "utf-8"
        lines = r2.iter_lines(decode_unicode=True)
        website = "redlion.com/canadas-best-value-inn"
        for line2 in lines:
            if '"entityId":"' in line2:
                store = line2.split('"entityId":"')[1].split('"')[0]
                name = (
                    line2.split('"entityTitle":"')[1]
                    .split('"')[0]
                    .replace("\\u0026", "&")
                )
            if "window.rawJson" in line2:
                zc = line2.split('"postal_code":"')[1].split('"')[0]
                add = line2.split('"address_line1":"')[1].split('"')[0]
                if '"address_line2":"' in line2:
                    add = add + " " + line2.split('"address_line2":"')[1].split('"')[0]
                city = line2.split('"locality":"')[1].split('"')[0]
                state = line2.split('"administrative_area":"')[1].split('"')[0]
                country = line2.split('"country_code":"')[1].split('"')[0]
                lat = line2.split('"geo":{"lat":')[1].split(",")[0]
                lng = line2.split(',"lon":')[1].split(",")[0]
                phone = line2.split('"phone":"')[1].split('"')[0]
                hours = "<MISSING>"
                typ = "Red Lion Hotels"
                yield [
                    website,
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
