import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("jiffylube_ca")

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
    "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
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
    url = "https://jiffylubeservice.ca/locations/"
    r = session.get(url, headers=headers)
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if '<div class="locations-tabs-content" id="' in line:
            states = line.split('<div class="locations-tabs-content" id="')
            for state in states:
                if 'class="store" href="' in state:
                    sname = state.split('"')[0]
                    items = state.split('class="store" href="')
                    for item in items:
                        if "View Store" in item:
                            locs.append(item.split('"')[0] + "|" + sname)
    for loc in locs:
        lurl = loc.split("|")[0]
        sname = loc.split("|")[1]
        if sname == "alberta":
            state = "AB"
        if sname == "british-columbia":
            state = "BC"
        if sname == "nova-scotia":
            state = "NS"
        if sname == "saskatchewan":
            state = "SK"
        if sname == "territories":
            state = "NT"
        logger.info(("Pulling Location %s..." % lurl))
        r2 = session.post(lurl, headers=headers)
        website = "jiffylube.ca"
        country = "CA"
        typ = "<MISSING>"
        name = ""
        add = ""
        city = ""
        zc = ""
        store = "<MISSING>"
        phone = ""
        lat = ""
        lng = ""
        hours = "<MISSING>"
        for line2 in r2.iter_lines():
            line2 = str(line2.decode("utf-8"))
            if 'class="taxonomy city"><span property="name">' in line2:
                city = line2.split('class="taxonomy city"><span property="name">')[
                    1
                ].split("<")[0]
            if "<h1>" in line2:
                name = line2.split("<h1>")[1].split("<")[0]
            if '<div class="marker"' in line2:
                lat = line2.split('data-pin="jiffy" data-lat="')[1].split('"')[0]
                lng = line2.split('data-lng="')[1].split('"')[0]
                add = line2.split("<h2>")[1].split("<")[0].strip()
                zc = line2.split("<span>")[1].split("<")[0].strip()
                phone = line2.split('<span><a href="tel:')[1].split('"')[0]
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
