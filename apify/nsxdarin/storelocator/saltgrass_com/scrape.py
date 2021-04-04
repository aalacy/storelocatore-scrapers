import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("saltgrass_com")


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
    url = "https://www.saltgrass.com/store-locator/"
    r = session.get(url, headers=headers)
    website = "saltgrass.com"
    typ = "<MISSING>"
    country = "US"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if '"url": "https://www.saltgrass.com/location/' in line:
            items = line.split('"url": "https://www.saltgrass.com/location/')
            for item in items:
                if "locations:" not in item:
                    lurl = "https://www.saltgrass.com/location/" + item.split('"')[0]
                    if "-" in lurl:
                        locs.append(lurl)
    for loc in locs:
        logger.info(loc)
        name = ""
        add = ""
        city = ""
        state = ""
        zc = ""
        store = "<MISSING>"
        phone = ""
        lat = ""
        lng = ""
        hours = ""
        r2 = session.get(loc, headers=headers)
        for line2 in r2.iter_lines():
            line2 = str(line2.decode("utf-8"))
            if 'data-gmaps-lat="' in line2:
                lat = line2.split('data-gmaps-lat="')[1].split('"')[0]
                lng = line2.split('data-gmaps-lng="')[1].split('"')[0]
            if "<h1>" in line2:
                name = line2.split(">")[1].split("<")[0]
            if 'data-gmaps-address="' in line2:
                addinfo = line2.split('data-gmaps-address="')[1].split('"')[0]
                add = addinfo.split(",")[0]
                city = addinfo.split(",")[1].strip()
                state = addinfo.split(",")[2].strip().split(" ")[0]
                zc = addinfo.rsplit(" ", 1)[1]
            if '<a href="tel:' in line2:
                phone = line2.split('<a href="tel:')[1].split('"')[0]
            if "day:" in line2:
                hours = (
                    line2.split("</p><p>")[1].split("<br/><")[0].replace("<br/>", "; ")
                )
        if "san-antonio-riverwalk" in loc:
            name = "San Antonio Riverwalk"
        if "saltgrass-downtown-houston" in loc:
            hours = "Mon: Closed; Tues - Sun: Open at 11:00 AM"
        if "saltgrass-oklahoma-city" in loc:
            name = "Oklahoma City"
            add = "1445 West I-240 Service Rd, Suite 13"
            city = "Oklahoma City"
            state = "OK"
            zc = "73159"
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
