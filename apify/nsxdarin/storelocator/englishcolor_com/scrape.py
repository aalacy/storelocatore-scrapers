import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("englishcolor_com")


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
    url = "https://www.englishcolor.com/locations/"
    r = session.get(url, headers=headers)
    website = "englishcolor.com"
    typ = "<MISSING>"
    country = "US"
    loc = "http://www.englishcolor.com/locations/"
    store = "<MISSING>"
    hours = "<MISSING>"
    lat = "<MISSING>"
    lng = "<MISSING>"
    name = "Mobile"
    add = "912 Butler Dr"
    city = "Mobile"
    state = "AL"
    zc = "36693"
    phone = "(251) 662-3145"
    hours = "M-F 8:00-5:00; Saturday: 8:30-11:30"
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
    logger.info("Pulling Stores")
    lines = r.iter_lines()
    for line in lines:
        line = str(line.decode("utf-8"))
        if 'style="text-align: center;"><span class="Style45">' in line:
            add = line.split('<span class="Style45">')[1].split("<")[0].replace(",", "")
            g1 = next(lines)
            g2 = next(lines)
            g3 = next(lines)
            g4 = next(lines)
            g1 = str(g1.decode("utf-8"))
            g2 = str(g2.decode("utf-8"))
            g3 = str(g3.decode("utf-8"))
            g4 = str(g4.decode("utf-8"))
            city = g1.split('">')[1].split(",")[0]
            state = g1.split('">')[1].split(",")[1].strip().split(" ")[0]
            zc = g1.split('">')[1].split("<")[0].rsplit(" ", 1)[1]
            phone = g2.split('">')[1].split("<")[0]
            hours = g3.split('">')[1].split("<")[0]
            name = city.title()
            try:
                hours = hours + "; " + g4.split('">')[1].split("<")[0]
            except:
                hours = hours + "; " + g4.split("<")[0]
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
