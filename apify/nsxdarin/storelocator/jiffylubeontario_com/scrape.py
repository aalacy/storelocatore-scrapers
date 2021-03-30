import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("jiffylubeontario_com")

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
    "content-type": "application/x-www-form-urlencoded",
}
headers2 = {
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
    alllocs = []
    url = "https://www.jiffylubeontario.com/wp-admin/admin-ajax.php"
    cities = [
        "Toronto",
        "Ottawa",
        "Mississauga",
        "Brampton",
        "Hamilton",
        "London",
        "Markham",
        "Vaughan",
        "Kitchener",
        "Windsor",
        "Richmond Hill",
        "Oakville",
        "Burlington",
        "Greater Sudbury",
        "Oshawa",
        "Barrie",
        "St Catharines",
        "Guelph",
        "Cambridge",
        "Whitby",
        "Kingston",
        "Ajax",
        "Milton",
        "Thunder Bay",
        "Waterloo",
        "Chatham Kent",
        "Brantford",
        "Clarington",
        "Pickering",
        "Niagara Falls",
        "Newmarket",
        "Peterborough",
        "Kawartha Lakes",
        "Sault Ste Marie",
        "Sarnia",
        "Caledon",
        "Norfolk County",
        "Halton Hills",
        "Aurora",
        "Welland",
        "North Bay",
        "Belleville",
        "Cornwall",
        "Whitchurch Stouffville",
        "Haldimand County",
        "Georgina",
        "Quinte West",
        "Timmins",
        "Woodstock",
        "St Thomas",
        "Brant",
        "Lakeshore",
        "Innisfil",
        "Bradford West Gwillimbury",
        "New Tecumseth",
        "Stratford",
        "Orillia",
        "Fort Erie",
        "LaSalle",
        "Orangeville",
        "Leamington",
        "Grimsby",
        "Prince Edward County",
        "Clarence Rockland",
        "East Gwillimbury",
        "Lincoln",
        "Tecumseh",
        "Amherstburg",
        "Collingwood",
        "Kingsville",
        "Brockville",
        "Owen Sound",
        "Strathroy Caradoc",
        "Wasaga Beach",
        "Essex",
        "Huntsville",
        "Cobourg",
        "Thorold",
        "Port Colborne",
        "Niagara on the Lake",
        "Middlesex Centre",
        "Petawawa",
        "Pelham",
        "Midland",
        "Port Hope",
        "North Grenville",
        "Bracebridge",
        "Greater Napanee",
        "Tillsonburg",
        "Kenora",
        "West Nipissing",
        "Pembroke",
        "Saugeen Shores",
        "Thames Centre",
        "Mississippi Mills",
        "North Perth",
        "Trent Hills",
        "The Nation",
        "Ingersoll",
        "Central Elgin",
        "West Grey",
        "Gravenhurst",
        "Brighton",
        "Erin",
        "Kincardine",
        "Meaford",
    ]
    coords = []
    for city in cities:
        logger.info("Pulling City %s..." % city)
        payload = {
            "action": "load_map",
            "search[postal]": city,
            "search[config][map_height]": "176.5px",
            "search[map_case]": "load_locations_from_postal_code",
        }
        r = session.post(url, headers=headers, data=payload)
        count = 0
        for line in r.iter_lines():
            line = str(line.decode("utf-8"))
            if "new google.maps.LatLng(" in line and "(0, 0)" not in line:
                llat = line.split("new google.maps.LatLng(")[1].split(",")[0]
                llng = (
                    line.split("new google.maps.LatLng(")[1]
                    .split(",")[1]
                    .strip()
                    .split(")")[0]
                )
                coords.append(llat + "|" + llng)
            if '<span class="postal">' in line:
                lc = line.split(",")[0].strip().replace("\t", "")
                lp = line.split('<span class="postal">')[1].split("<")[0].strip()
            if '<a href="https://www.jiffylubeontario.com/' in line:
                lurl = line.split('href="')[1].split('"')[0]
                linfo = lurl + "|" + lp + "|" + lc
                linfo = (
                    linfo
                    + "|"
                    + coords[count].split("|")[0]
                    + "|"
                    + coords[count].split("|")[1]
                )
                if linfo not in locs:
                    locs.append(linfo)
                count = count + 1

    for loc in locs:
        logger.info("Pulling Location %s..." % loc)
        lurl = loc.split("|")[0]
        zc = loc.split("|")[1]
        city = loc.split("|")[2]
        website = "jiffylubeontario.com"
        country = "CA"
        state = "ON"
        typ = "<MISSING>"
        hours = ""
        add = ""
        lat = loc.split("|")[3]
        lng = loc.split("|")[4]
        phone = ""
        store = "<MISSING>"
        name = ""
        r2 = session.get(lurl, headers=headers2)
        lines = r2.iter_lines()
        hrurl = lurl + "/wp-admin/admin-ajax.php?action=load_hours"
        r3 = session.get(hrurl, headers=headers2)
        lines2 = r3.iter_lines()
        for line3 in lines2:
            line3 = str(line3.decode("utf-8"))
            if '<span class="textday">' in line3:
                g = next(lines2)
                g = str(g.decode("utf-8"))
                day = g.split("<")[0].strip().replace("\t", "")
            if "<strong>CLOSED</strong>" in line3:
                day = day + ": CLOSED"
                if hours == "":
                    hours = day
                else:
                    hours = hours + "; " + day
            if '<span class="hours-start">' in line3:
                day = (
                    day
                    + ": "
                    + line3.split('<span class="hours-start">')[1].split("<")[0]
                    + "-"
                    + line3.split('"hours-end">')[1].split("<")[0]
                )
                if hours == "":
                    hours = day
                else:
                    hours = hours + "; " + day
        for line2 in lines:
            line2 = str(line2.decode("utf-8"))
            if 'itemprop="name address">' in line2:
                g = next(lines)
                g = str(g.decode("utf-8"))
                add = g.split(">")[1].split("<")[0]
            if 'class="location-phone">' in line2:
                phone = line2.split('"tel:')[1].split('"')[0]
            if "<title>" in line2:
                name = line2.split("<title>")[1].split("|")[0].strip()
        if phone == "":
            phone = "<MISSING>"
        if lurl not in alllocs:
            alllocs.append(lurl)
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
