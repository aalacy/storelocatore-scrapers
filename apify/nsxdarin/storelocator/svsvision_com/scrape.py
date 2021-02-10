import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
    "host": "www.svsvision.com",
    "cache-control": "max-age=0",
    "connection": "keep-alive",
    "cookie": "wc_wishlists_user[key]=069824ba681b8b882cd2d3597b1690895ffe23085e8a3; wc_wishlists_user[key]=069824ba681b8b882cd2d3597b1690895ffe2309ec367; __utmz=36930018.1610490646.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); _fbp=fb.1.1610490647432.153315600; poppup1313=1; MCPopupClosed=yes; __utma=36930018.65482460.1610490646.1610659828.1612830606.3; __utmc=36930018; __utmt=1; __utmb=36930018.1.10.1612830606; _uetsid=f54381106a6d11eb9fbf354ce3f7991f; _uetvid=f543ea706a6d11ebbe0c317b8022e2ad",
}

logger = SgLogSetup().get_logger("svsvision_com")


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
    url = "https://www.svsvision.com/contact/?state=all"
    r = session.get(url, headers=headers)
    website = "svsvision.com"
    typ = "<MISSING>"
    country = "US"
    loc = "<MISSING>"
    store = "<MISSING>"
    logger.info("Pulling Stores")
    lines = r.iter_lines()
    for line in lines:
        line = str(line.decode("utf-8"))
        if "<address id=addr" in line:
            items = line.split("<address id=addr")
            for item in items:
                if '<div class="span6">' in item:
                    name = item.split("<strong>")[1].split("<")[0]
                    add = item.split("</strong><br>")[1].split("<")[0]
                    city = name
                    state = item.split("<br>")[2].split(" ")[0]
                    zc = item.split("<br>")[2].rsplit(" ", 1)[1]
                    phone = item.split("<br><br>")[1].split("<")[0]
                    try:
                        lat = item.split("/@")[1].split(",")[0]
                        lng = item.split("/@")[1].split(",")[1]
                    except:
                        lat = "<MISSING>"
                        lng = "<MISSING>"
                    hours = item.split('<div class="span6">')[1].split("<")[0]
                    g = next(lines)
                    g = str(g.decode("utf-8"))
                    while "Friday" not in g:
                        hours = hours + "; " + g.split("<")[0]
                        g = next(lines)
                        g = str(g.decode("utf-8"))
                        if "Friday" in g:
                            hours = hours + "; " + g.split("<")[0]
                    sathrs = "Saturday 9:00-6:00"
                    if (
                        "Amherst" in name
                        or "Blasdell" in name
                        or "Caledonia" in name
                        or "Cincinnati" in name
                        or "Detroit" in name
                        or "Fairlawn" in name
                        or "Indianapolis" in name
                        or "Lansing" in name
                        or "Stockbridge" in name
                        or "Okemos" in name
                    ):
                        sathrs = "Saturday 9:00-1:00"
                    names = [
                        "Bloomfield Hills",
                        "Ann Arbor",
                        "Brighton",
                        "Eastpointe",
                        "Garden City",
                        "Gaylord",
                        "Grand Rapids",
                        "Holland",
                        "Kalamazoo",
                        "Jackson",
                        "Lenox Township",
                        "Lansing",
                        "Mentor",
                        "Louisville",
                        "Middleburg Heights",
                        "Northville",
                        "Plymouth",
                        "Overland Park",
                        "Saginaw",
                        "Redford",
                        "Sandusky",
                        "Sheffield",
                        "Southfield",
                        "South Euclid",
                        "Sterling Heights",
                        "Toledo",
                        "Traverse City",
                        "Troy",
                        "Walker",
                        "Wayne",
                        "Waterford",
                        "Wixom",
                    ]
                    if name in names:
                        sathrs = "Saturday: 9:00-3:00"
                    if name == "Detroit":
                        sathrs = "Saturday 10:00-5:00"
                    if name == "Flint" or name == "Mt. Clemens":
                        sathrs = "Saturday 8:30-6:00"
                    if name == "Trenton" or name == "Shelby Township":
                        sathrs = "Saturday 8:00-5:00"
                    hours = hours + "; SATHOURS"
                    hours = hours.replace("SATHOURS", sathrs)
                    if (
                        name == "Bloomfield Hills"
                        or name == "Brighton"
                        or name == "Allen Park"
                    ):
                        hours = hours + "; Sunday 10:00-4:00"
                    if name == "Midland":
                        hours = hours + "; Sunday 11:00-5:00"
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
    name = "Troy"
    add = "6828 Rochester Rd."
    city = "Troy"
    state = "MI"
    zc = "48085"
    phone = "248-710-1100"
    lat = "<MISSING>"
    lng = "<MISSING>"
    hours = "Monday: 9:00-8:00; Tuesday: 9:00-6:00; Wednesday: 9:00-6:00; Thursday: 9:00-6:00; Friday: 9:00-6:00; Saturday: 9:00-6:00"
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
