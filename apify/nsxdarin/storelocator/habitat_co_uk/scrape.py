import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("habitat_co_uk")

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
    url = "https://www.habitat.co.uk/storelocator"
    r = session.get(url, headers=headers)
    if r.encoding is None:
        r.encoding = "utf-8"
    for line in r.iter_lines(decode_unicode=True):
        if 'target="_self" href="//www.habitat.co.uk/stores/' in line:
            items = line.split('target="_self" href="//www.habitat.co.uk/stores/')
            for item in items:
                if "More information<" in item:
                    locs.append(
                        "https://www.habitat.co.uk/stores/" + item.split("?")[0]
                    )
    for loc in locs:
        logger.info(("Pulling Location %s..." % loc))
        website = "habitat.co.uk"
        typ = ""
        hours = ""
        name = ""
        add = ""
        city = ""
        state = "<MISSING>"
        zc = ""
        country = "GB"
        store = "<MISSING>"
        phone = ""
        lat = "<MISSING>"
        lng = "<MISSING>"
        r2 = session.get(loc, headers=headers)
        if r2.encoding is None:
            r2.encoding = "utf-8"
        for line2 in r2.iter_lines(decode_unicode=True):
            if "<title>" in line2:
                name = line2.split("<title>")[1].split("<")[0]
            if '"Opening hours","bodyCopy":"' in line2:
                hours = line2.split('"Opening hours","bodyCopy":"')[1].split('",')[0]
                hours = hours.replace("\\u003Cbr \\u002F\\u003E", "; ").replace(
                    "\\u003C\\u002Fp\\u003E", ""
                )
                hours = hours.replace("\\u003Cp\\u003E", "")
            if "Address</h3><div" in line2:
                add = (
                    line2.split("Address</h3><div")[1]
                    .split('text"><p>')[0]
                    .replace(",&nbsp;", "")
                )
                city = line2.split("Address</h3>")[1].split("<br />")[1].split(",")[0]
            if "<strong>0" in line2:
                phone = "0" + line2.split("<strong>0")[1].split("<")[0]
        if hours == "":
            hours = "<MISSING>"
        if phone == "":
            phone = "<MISSING>"
        add = add.replace("\\u2019", "'")
        name = name.replace("\\u2019", "'")
        if "Inside" in add:
            if "," in add:
                add = add.split(",", 1)[1].strip()
        if city == "":
            city = add.split(",")[1].strip()
            add = add.split(",")[1].strip()
        if "," in city:
            add = city.split(",")[0].strip()
            city = city.split(",")[1].strip()
        if "nine-elms" in loc:
            city = "London"
            add = "62 Wandsworth Road"
        if "wandsworth" in loc:
            city = "London"
            add = "45 Garratt Lane"
        if "heaton-newcastle" in loc:
            city = "Newcastle"
            add = "Etherstone Avenue"
        if "London" in name:
            city = "London"
        if "finchley" in loc:
            typ = "Outlet Store"
        else:
            typ = "Showroom"
        if "finchley" in loc:
            add = "02 Centre, 255 Finchley Road"
            city = "London"
            zc = "NW3 6LU"
        if "brighton" in loc:
            add = "23-25 North Street"
            zc = "BN1 1EB"
        if "leeds" in loc:
            add = "Moor Allerton Centre"
            zc = "LS17 5NY"
        if "westfield" in loc:
            add = "Home Quarter, Level -2, Westfield White City"
            zc = "W12 7GF"
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
