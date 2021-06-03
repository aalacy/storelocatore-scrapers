import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup
import time

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("petstuff_com")


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
    session = SgRequests()
    locs = ["https://petstuff.com/ca-anaheim-hills-protein-for-pets"]
    alllocs = []
    url = "https://petstuff.com/store-locator"
    r = session.get(url, headers=headers)
    website = "petstuff.com"
    typ = "<MISSING>"
    country = "US"
    Found = False
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if "</a><li><a href=/" in line:
            items = line.split("</a><li><a href=/")
            for item in items:
                if "<html>" not in item:
                    lurl = item.split(" ")[0]
                    if ">Contact" in lurl:
                        Found = True
                    if "-" in lurl:
                        if (
                            lurl not in alllocs
                            and Found is False
                            and "stella-chewys" not in lurl
                        ):
                            alllocs.append(lurl)
                            locs.append("https://petstuff.com/" + lurl)
    for loc in locs:
        time.sleep(5)
        session = SgRequests()
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
            if "<title>" in line2:
                name = line2.split("<title>")[1].split("</title>")[0]
            if "ADDRESS:</strong></span><p><span style=font-size:12pt>" in line2:
                add = line2.split(
                    "ADDRESS:</strong></span><p><span style=font-size:12pt>"
                )[1].split("<")[0]
                addinfo = (
                    line2.split(
                        "ADDRESS:</strong></span><p><span style=font-size:12pt>"
                    )[1]
                    .split("</span><p><span style=font-size:12pt>")[1]
                    .split("<")[0]
                )
                city = addinfo.split(",")[0]
                zc = addinfo.rsplit(" ", 1)[1]
                state = addinfo.split(",")[1].strip().split(" ")[0]
            if "ADDRESS:</strong><p><span class=location_addr>" in line2:
                addinfo = line2.split("ADDRESS:</strong><p><span class=location_addr>")[
                    1
                ].split("<")[0]
                add = addinfo.split(",")[0]
                state = addinfo.split(",")[1].strip()
                zc = addinfo.split(",")[2].strip()
            if "PHONE:</strong>" in line2:
                phone = line2.split("PHONE:</strong>")[1].split("<")[0].strip()
            if "data-shoplatitude" in line2:
                lat = line2.split("data-shoplatitude=")[1].split(" ")[0]
                lng = line2.split("data-shoplongitude=")[1].split(" ")[0]
            if "HOURS:</strong></span><p><span style=font-size:12pt>" in line2:
                hours = line2.split(
                    "HOURS:</strong></span><p><span style=font-size:12pt>"
                )[1].split("</span><p><span style=font-size:12pt><strong>")[0]
                hours = hours.replace("</span><p><span style=font-size:12pt>", "; ")
        if "ga-whitemarsh" in loc:
            add = "4717 Highway 80 East"
            city = "Savannah"
            state = "GA"
            zc = "31410"
            hours = (
                "Monday - Friday: 10am - 8pm; Saturday: 10am - 6pm; Sunday: 10am - 6pm"
            )
        name = name.replace("&#x27;", "'")
        if "Thousand Oaks" in add:
            add = add.replace("Thousand Oaks", "").strip()
            city = "Thousand Oaks"
        if "/co-broomfield" in loc:
            zc = "80023"
            state = "CO"
            city = "Broomfield"
            add = "3800 W 144th Ave"
            phone = "(303)466-1180"
            hours = "Monday-Friday: 10:00am-6:00pm; Saturday-Sunday: 10:00am-4:00pm"
        if "ca-thousand-oaks-protein-for-pets" in loc:
            phone = "805-552-7892"
            hours = "Monday-Friday: 10:00am-6:00pm; Saturday-Sunday: 10:00a-4:00pm"
        if "ga-poochnpaws-peachtree" in loc:
            add = "5185 Peachtree Pkwy #102"
            city = "Peachtree Corners"
            state = "GA"
            zc = "30092"
            phone = "(770)446-6672"
            hours = "Sunday-Saturday: 10:00am-6:00pm"
        if "il-schaum" in loc:
            add = "1249 E. Higgins Rd."
            city = "Schaumburg"
            state = "IL"
            zc = "60173"
            phone = "(630) 635-2344"
        if "ca-anaheim-hills-protein-for-pets" in loc:
            add = "701 S. Weir Canyon Rd."
            city = "Anaheim"
            state = "CA"
            zc = "92808"
            phone = "(714) 395-4158"
            hours = (
                "Monday - Friday: 9am - 7pm; Saturday: 10am - 5pm; Sunday: 10am - 5pm"
            )
        hours = hours.replace("&amp;", "&").replace("amp;", "&")
        if "(Groom" in name:
            name = name.split("(Groom")[0].strip()
        if "| Bentley's Pet Stuff" in name:
            name = name.split("| Bentley's Pet Stuff")[0].strip()
        if "(" in name:
            name = name.split("(")[0].strip()
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
