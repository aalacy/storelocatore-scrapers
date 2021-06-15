import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("arlohotels_com")

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
    locs = []
    url = "https://www.arlohotels.com"
    r = session.get(url, headers=headers)
    if r.encoding is None:
        r.encoding = "utf-8"
    for line in r.iter_lines(decode_unicode=True):
        if '<li class="location">' in line:
            items = line.split('<li class="location">')
            for item in items:
                if (
                    '<div class="hotel-row"><div id="footer-sidebar2"' not in item
                    and '<a href="/' in item
                ):
                    stub = (
                        "https://www.arlohotels.com/"
                        + item.split('<a href="/')[1].split('"')[0]
                    )
                    if "com//" not in stub:
                        locs.append(stub)
    website = "arlohotels.com"
    typ = "<MISSING>"
    country = "US"
    store = "<MISSING>"
    hours = "<MISSING>"
    for loc in locs:
        logger.info(("Pulling Location %s..." % loc))
        name = ""
        add = ""
        city = ""
        state = ""
        zc = ""
        lat = ""
        lng = ""
        phone = ""
        r2 = session.get(loc, headers=headers)
        for line2 in r2.iter_lines():
            line2 = str(line2.decode("utf-8"))
            if '<h3 class="address__hotel-name">' in line2:
                name = line2.split('<h3 class="address__hotel-name">')[1].split("<")[0]
                try:
                    phone = line2.split('href="tel:')[1].split('"')[0]
                except:
                    phone = "<MISSING>"
            if 'Address"><span>' in line2:
                fulladd = (
                    line2.split('Address"><span>')[1]
                    .split("<")[0]
                    .replace(",USA", "")
                    .replace(", USA", "")
                )
                if "arlo-midtown" not in loc:
                    add = fulladd.split(",")[0]
                    city = fulladd.split(",")[1].strip()
                    state = fulladd.split(",")[2].strip().split(" ")[0]
                    zc = fulladd.rsplit(" ", 1)[1]
                else:
                    city = "New York"
                    state = "NY"
                    zc = "10018"
                    add = "351 W 38th St"
            if 'data-center-lat="' in line2:
                lat = line2.split('data-center-lat="')[1].split('"')[0]
                lng = line2.split('lng="')[1].split('"')[0]
        if add != "":
            if "arlo-nomad" in loc:
                phone = "212.806.7000"
            if "arlo-soho" in loc:
                phone = "212.342.7000"
            if "nautilus-miami-beach" in loc:
                phone = "305.503.5700"
            if "arlo-midtown" in loc:
                phone = "212.343.7000"
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
