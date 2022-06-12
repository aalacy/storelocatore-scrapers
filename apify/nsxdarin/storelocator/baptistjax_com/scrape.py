import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("baptistjax_com")


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
    url = "https://www.baptistjax.com/sitemap.xml"
    r = session.get(url, headers=headers)
    website = "baptistjax.com"
    typ = "<MISSING>"
    country = "US"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if (
            "<loc>https://www.baptistjax.com/locations/" in line
            and "directions<" not in line
        ):
            locs.append(line.split(">")[1].split("<")[0])
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
            if '"introTitle":"' in line2:
                name = line2.split('"introTitle":"')[1].split('"')[0]
                lat = line2.split('"lat":')[1].split(",")[0]
                lng = line2.split('"lng":')[1].split(",")[0]
                try:
                    phone = line2.split('"Main:","number":"')[1].split('"')[0]
                except:
                    phone = "<MISSING>"
                add = line2.split('"address1":"')[1].split('"')[0]
                try:
                    add = add + " " + line2.split('"address2":"')[1].split('"')[0]
                except:
                    pass
                add = add.strip()
                city = line2.split('"city":"')[1].split('"')[0]
                state = line2.split('"state":"')[1].split('"')[0]
                zc = line2.split('"zip":"')[1].split('"')[0]
                days = line2.split('{"dayOfWeek":"')
                for day in days:
                    if '"openTime":"' in day:
                        hrs = (
                            day.split('"')[0]
                            + ": "
                            + day.split('"openTime":"')[1].split('"')[0]
                            + "-"
                            + day.split('"closeTime":"')[1].split('"')[0]
                        )
                        if hours == "":
                            hours = hrs
                        else:
                            hours = hours + "; " + hrs
        if hours == "":
            hours = "<MISSING>"
        if add != "":
            name = name.replace("\\u0026", "&")
            if " - " in name:
                typ = name.split(" - ")[0]
            if "14985 Old" in add:
                phone = "904.288.9491"
            if "1577 Roberts Drive" in add:
                phone = "904.247.3324"
            if "14540 Old St" in add:
                phone = "904.202.2222"
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
    url = "https://www.baptistjax.com/doctors/baptist-primary-care/locations"
    r = session.get(url, headers=headers)
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        typ = "Primary Care"
        if '{"guid":"' in line:
            items = line.split('{"guid":"')
            for item in items:
                if '"name":"' in item:
                    name = item.split('"name":"')[1].split('"')[0]
                    add = item.split('"address1":"')[1].split('"')[0]
                    try:
                        add = add + " " + item.split('"address2":"')[1].split('"')[0]
                    except:
                        pass
                    try:
                        add = add + " " + item.split('"address3":"')[1].split('"')[0]
                    except:
                        pass
                    city = item.split('"city":"')[1].split('"')[0]
                    state = item.split('"state":"')[1].split('"')[0]
                    zc = item.split('"zip":"')[1].split('"')[0]
                    lat = item.split('"lat":')[1].split(",")[0]
                    lng = item.split('"lng":')[1].split(",")[0]
                    try:
                        phone = item.split('"text":"Main:","number":"')[1].split('"')[0]
                    except:
                        phone = "<MISSING>"
                    loc = "<MISSING>"
                    store = "<MISSING>"
                    hours = "<MISSING>"
                    if "14985 Old" in add:
                        phone = "904.288.9491"
                    if "1577 Roberts Drive" in add:
                        phone = "904.247.3324"
                    if "14540 Old St" in add:
                        phone = "904.202.2222"
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
    urls = [
        "https://www.baptistjax.com/locations/sleep-centers",
        "https://www.baptistjax.com/locations/rehabilitation-centers",
        "https://www.baptistjax.com/locations/surgery-centers",
        "https://www.baptistjax.com/locations/wound-care",
        "https://www.baptistjax.com/locations/medical-imaging",
        "https://www.baptistjax.com/locations/labs",
        "https://www.baptistjax.com/locations/heart-and-vascular-testing-centers",
    ]
    for url in urls:
        typ = url.rsplit("/", 1)[1].replace("-", " ").title()
        r2 = session.get(url, headers=headers)
        for line2 in r2.iter_lines():
            line2 = str(line2.decode("utf-8"))
            if '{"guid":"' in line2:
                items = line2.split('{"guid":"')
                for item in items:
                    if '"name":"' in item:
                        name = item.split('"name":"')[1].split('"')[0]
                        add = item.split('"address1":"')[1].split('"')[0]
                        try:
                            add = (
                                add + " " + item.split('"address2":"')[1].split('"')[0]
                            )
                        except:
                            pass
                        try:
                            add = (
                                add + " " + item.split('"address3":"')[1].split('"')[0]
                            )
                        except:
                            pass
                        city = item.split('"city":"')[1].split('"')[0]
                        state = item.split('"state":"')[1].split('"')[0]
                        zc = item.split('"zip":"')[1].split('"')[0]
                        lat = item.split('"lat":')[1].split(",")[0]
                        lng = item.split('"lng":')[1].split(",")[0]
                        try:
                            phone = item.split('"text":"Main:","number":"')[1].split(
                                '"'
                            )[0]
                        except:
                            phone = "<MISSING>"
                        loc = "<MISSING>"
                        store = "<MISSING>"
                        hours = "<MISSING>"
                        if "14985 Old" in add:
                            phone = "904.288.9491"
                        if "1577 Roberts Drive" in add:
                            phone = "904.247.3324"
                        if "14540 Old St" in add:
                            phone = "904.202.2222"
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
