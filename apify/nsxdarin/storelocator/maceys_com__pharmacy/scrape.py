import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("maceys_com__pharmacy")


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
    url = "https://maceys.com/all"
    locs = []
    hrlist = []
    r = session.get(url, headers=headers)
    website = "maceys.com/pharmacy"
    typ = "<MISSING>"
    country = "US"
    store = "<MISSING>"
    hours = "<MISSING>"
    lat = "<MISSING>"
    lng = "<MISSING>"
    logger.info("Pulling Stores")
    Found = False
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if "Grocery Locations</h4>" in line:
            Found = True
        if Found and "Show more</a></>" in line:
            Found = False
        if Found and 'href="' in line:
            locs.append("https://maceys.com" + line.split('href="')[1].split('"')[0])
    url = "https://afsshareportal.com/lookUpFeatures.php?callback=jsonpcallbackHours&action=storeInfo&website_url=maceys.com&expandedHours=true"
    r = session.get(url, headers=headers)
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if '{"store_id":"' in line:
            items = line.split('{"store_id":"')
            for item in items:
                if (
                    '"store_department_name":"Store"' not in item
                    and "jsonpcallbackHours" not in item
                ):
                    sname = (
                        item.split('"store_name":"Macey\'s')[1].split('"')[0].strip()
                    )
                    shrs = "Sun: " + item.split('"Sunday":"')[1].split('"')[0]
                    shrs = shrs + "; Mon: " + item.split('"Monday":"')[1].split('"')[0]
                    shrs = shrs + "; Tue: " + item.split('"Tuesday":"')[1].split('"')[0]
                    shrs = (
                        shrs + "; Wed: " + item.split('"Wednesday":"')[1].split('"')[0]
                    )
                    shrs = (
                        shrs + "; Thu: " + item.split('"Thursday":"')[1].split('"')[0]
                    )
                    shrs = shrs + "; Fri: " + item.split('"Friday":"')[1].split('"')[0]
                    shrs = (
                        shrs + "; Sat: " + item.split('"Saturday":"')[1].split('"')[0]
                    )
                    shrs = shrs.replace("Closed to Closed", "Closed")
                    hrlist.append(sname + "|" + shrs)
    for loc in locs:
        logger.info(loc)
        r2 = session.get(loc, headers=headers)
        lines = r2.iter_lines()
        phone = ""
        add = ""
        city = ""
        state = ""
        zc = ""
        name = ""
        for line2 in lines:
            line2 = str(line2.decode("utf-8"))
            if "<title>" in line2:
                name = line2.split("<title>")[1].split("<")[0]
            if "Pharmacy Phone Number:</h5>" in line2:
                next(lines)
                g = next(lines)
                g = str(g.decode("utf-8"))
                phone = g.split('<a href="tel:')[1].split('"')[0]
            if "Address:</h5>" in line2:
                next(lines)
                g = next(lines)
                h = next(lines)
                g = str(g.decode("utf-8"))
                h = str(h.decode("utf-8"))
                add = g.split("<")[0].strip().replace("\t", "")
                city = g.split(">")[1].split(",")[0].strip()
                zc = h.split(";")[1].split("<")[0].strip().replace("\t", "")
                state = h.split("&")[0].strip().replace("\t", "")
        name = name.replace("Macey's - ", "")
        for item in hrlist:
            if item.split("|")[0] == name:
                hours = item.split("|")[1]
        if "santaquin" in loc:
            hours = "Mon-Fri: 9 AM to 7 PM; Saturday: 9 AM to 6 PM; Sunday: Closed"
        if "west_jordan" in loc:
            hours = (
                "Mon-Fri: 8 AM to 8 PM; Saturday: 9 AM to 7 PM; Sunday: 10 AM to 4 PM"
            )
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
