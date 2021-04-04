import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("themaxchallenge_com")


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
    locs = ["https://www.themaxchallenge.com/locations/new-albany-oh/"]
    url = "https://www.themaxchallenge.com/max-challenge-locations/"
    r = session.get(url, headers=headers)
    website = "themaxchallenge.com"
    typ = "<MISSING>"
    country = "US"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if '<a href="https://www.themaxchallenge.com/locations/' in line:
            items = line.split('<a href="https://www.themaxchallenge.com/locations/')
            for item in items:
                if "</a></h2></div>" in item:
                    locs.append(
                        "https://www.themaxchallenge.com/locations/"
                        + item.split('"')[0]
                    )
    for loc in locs:
        CS = False
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
        hours = "<MISSING>"
        r2 = session.get(loc, headers=headers)
        for line2 in r2.iter_lines():
            line2 = str(line2.decode("utf-8"))
            if "Coming Soon" in line2:
                CS = True
            if "<title>" in line2:
                name = line2.split("<title>")[1].split(" |")[0]
            if '"postalCode":"' in line2:
                zc = line2.split('"postalCode":"')[1].split('"')[0]
                state = line2.split('"addressRegion":"')[1].split('"')[0]
                add = line2.split('"streetAddress":"')[1].split('"')[0]
                city = line2.split('"addressLocality":"')[1].split('"')[0]
                lat = line2.split('"latitude":"')[1].split('"')[0]
                lng = line2.split('"longitude":"')[1].split('"')[0]
                zc = line2.split('"postalCode":"')[1].split('"')[0]
            if '<a href="tel:' in line2 and phone == "":
                phone = line2.split('<a href="tel:')[1].split('"')[0]
            if "saddr=&daddr=" in line2 and add == "":
                if "477 NJ-10" in line2:
                    add = "477 NJ-10"
                    city = "Randolph"
                    state = "NJ"
                    zc = "07869"
                elif "6401 Jericho Turnpike" in line2:
                    add = "6401 Jericho Turnpike 105"
                    city = "Commack"
                    state = "NY"
                    zc = "11725"
                elif "mill-basin" in loc:
                    add = "<MISSING>"
                    city = "Mill Basin"
                    state = "NY"
                    zc = "11234"
                elif "houston-tx" in loc:
                    add = "84 N Braeswood Blvd"
                    city = "Houston"
                    state = "TX"
                    zc = "77096"
                else:
                    addinfo = line2.split("saddr=&daddr=")[1].split('"')[0]
                    addinfo = (
                        addinfo.replace("Route 31", "Route 31,")
                        .replace("NJ", ",NJ")
                        .replace(",,", ",")
                    )
                    add = addinfo.split(",")[0]
                    city = addinfo.split(",")[1].strip()
                    state = addinfo.split(",")[2].strip().split(" ")[0]
                    zc = addinfo.split(",")[2].rsplit(" ", 1)[1]
            if lat == "" and "new google.maps.LatLng(" in line2:
                lat = line2.split("new google.maps.LatLng(")[1].split(",")[0]
                lng = (
                    line2.split("new google.maps.LatLng(")[1]
                    .split(",")[1]
                    .strip()
                    .split(")")[0]
                )
        if "new-albany-oh" in loc:
            add = "<MISSING>"
            city = "New Albany"
            state = "OH"
            zc = "<MISSING>"
        if add != "" and state != "USA" and CS is False:
            state = name.rsplit(",", 1)[1].strip()
            if phone == "":
                phone = "<MISSING>"
            if zc == "":
                zc = "<MISSING>"
            if "170 S Main" in add:
                zc = "10956"
            if "staten-island-arthur-kill-ny" in loc:
                add = "4295 Arthur Kill Rd"
                city = "Staten Island"
                state = "NY"
                zc = "10309"
            if "seminole-fl" in loc:
                zc = "33772"
            if "flemington-nj" in loc:
                add = "148 NJ-31 #3"
                city = "Flemington"
                state = "NJ"
                zc = "08822"
            if "hazlet-nj" in loc:
                add = "3043 NJ-35"
                city = "Hazlet"
                state = "NJ"
                zc = "07730"
            if "ocean-nj" in loc:
                add = "1710 NJ-35"
                city = "Ocean"
                state = "NJ"
                zc = "07755"
            if "lawrencevillepennington-nj" in loc:
                add = "25 NJ-31 #9"
                city = "Pennington"
                state = "NJ"
                zc = "08534"
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
