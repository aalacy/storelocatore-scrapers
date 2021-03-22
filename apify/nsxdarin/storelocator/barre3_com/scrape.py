import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("barre3_com")


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
    url = "https://barre3.com/studio-locations"
    r = session.get(url, headers=headers)
    website = "barre3.com"
    typ = "<MISSING>"
    hours = "<MISSING>"
    country = "US"
    Found = True
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if "Locations in Philippines</h2>" in line:
            Found = False
        if "<a href='/studio-locations/" in line and Found:
            locs.append(
                "https://online.barre3.com/api/multiparts/studio-detail/"
                + line.split("<a href='/studio-locations/")[1].split("'")[0]
            )
    for loc in locs:
        logger.info(loc)
        lurl = (
            "https://online.barre3.com/studio-locations/"
            + loc.split("studio-detail/")[1]
        )
        r2 = session.get(loc, headers=headers)
        if r2.encoding is None:
            r2.encoding = "utf-8"
        for line2 in r2.iter_lines(decode_unicode=True):
            if '"id":' in line2:
                store = line2.split('"id":')[1].split(",")[0]
                name = line2.split('"name":"')[1].split('"')[0]
                add = line2.split(',"address1":"')[1].split('"')[0]
                try:
                    add = add + " " + line2.split('address2":"')[1].split('"')[0]
                except:
                    pass
                city = line2.split(',"city":"')[1].split('"')[0]
                state = line2.split(',"state":"')[1].split('"')[0]
                zc = line2.split(',"postalCode":"')[1].split('"')[0]
                lat = line2.split('"unformattedText7":"')[1].split('"')[0]
                lng = line2.split('"unformattedText8":"')[1].split('"')[0]
                try:
                    phone = line2.split(',"phone":"')[1].split('"')[0]
                except:
                    phone = "<MISSING>"
        if add == "":
            add = "<MISSING>"
        if "939-2510" in phone:
            phone = "480-939-2510"
        if phone is None or phone == "":
            phone = "<MISSING>"
        if " (" in zc:
            zc = zc.split(" (")[0]
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
