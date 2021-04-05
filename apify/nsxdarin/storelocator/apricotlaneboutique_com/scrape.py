import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("apricotlaneboutique_com")


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
    url = "https://apricotlaneboutique.com/locations/"
    r = session.get(url, headers=headers)
    website = "apricotlaneboutique.com"
    typ = "<MISSING>"
    country = "US"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if (
            '<div class="store_details_page"><a href="https://apricotlaneboutique.com/store/'
            in line
        ):
            locs.append(line.split('href="')[1].split('"')[0])
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
        lines = r2.iter_lines()
        for line2 in lines:
            line2 = str(line2.decode("utf-8"))
            if "<title>" in line2:
                name = line2.split("<title>")[1].split("<")[0]
                if " |" in name:
                    name = name.split(" |")[0]
            if "<h5>Visit Our Store</h5>" in line2:
                g = next(lines)
                g = next(lines)
                g = str(g.decode("utf-8"))
                add = g.split(">")[1].split("<")[0]
                g = next(lines)
                g = str(g.decode("utf-8"))
                city = g.split(">")[1].split("&")[0]
                state = g.split("&nbsp;")[1]
                zc = g.split("&nbsp;&nbsp;")[1].split("<")[0]
            if "Phone : " in line2:
                phone = (
                    line2.split("Phone : ")[1].split("<")[0].strip().replace("\t", "")
                )
                phone = phone[:14]
            if "var uluru = {lat: " in line2:
                lat = line2.split("var uluru = {lat: ")[1].split(",")[0]
                lng = line2.split("lng: ")[1].split("}")[0]
            if '<td class="label">' in line2:
                hrs = line2.split('<td class="label">')[1].split("<")[0]
            if "pm</td>" in line2:
                hrs = hrs + ": " + line2.split(">")[1].split("<")[0]
                if hours == "":
                    hours = hrs
                else:
                    hours = hours + "; " + hrs
        if "/pittsburgh" in loc:
            phone = "(412) 932-2092"
        if "/prescott" in loc:
            phone = "(928) 237-9309"
        if "/sarasota" in loc:
            phone = "(941) 960-1435"
        if phone == "":
            phone = "<MISSING>"
        if hours == "":
            hours = "<MISSING>"
        if lat == "":
            lat = "<MISSING>"
            lng = "<MISSING>"
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
