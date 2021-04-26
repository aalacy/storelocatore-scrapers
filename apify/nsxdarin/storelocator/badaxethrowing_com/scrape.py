import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("badaxethrowing_com")


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
    url = "https://badaxethrowing.com/locations/"
    r = session.get(url, headers=headers)
    website = "badaxethrowing.com"
    typ = "<MISSING>"
    Found = False
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if "<loc>https://order.capriottis.com/menu/" in line:
            locs.append(line.split("<loc>")[1].split("<")[0])
        if "UK</a>" in line:
            Found = True
        if 'class="menu-country' in line:
            country = line.split('#">')[1].split("<")[0]
            if country == "UK":
                country = "GB"
        if (
            Found
            and 'class="menu-item menu-item-type-post_type menu-item-object-pag' in line
        ):
            locs.append(line.split('href="')[1].split('"')[0] + "|" + country)
        if Found and "Our Locations" in line:
            Found = False
    for loc in locs:
        country = loc.split("|")[1]
        lurl = loc.split("|")[0]
        CS = False
        if lurl != "https://badaxethrowing.com/locations/":
            logger.info(lurl)
            name = ""
            add = ""
            city = ""
            state = ""
            zc = ""
            store = "<MISSING>"
            phone = ""
            lat = "<MISSING>"
            lng = "<MISSING>"
            hours = ""
            r2 = session.get(lurl, headers=headers)
            for line2 in r2.iter_lines():
                line2 = str(line2.decode("utf-8"))
                if "coming soon" in line2 and "wide variety coming soon" not in line2:
                    CS = True
                if "<title>" in line2:
                    name = line2.split("<title>")[1].split("<")[0]
                    if " |" in name:
                        name = name.split(" |")[0]
                if '"streetAddress">' in line2:
                    add = line2.split('"streetAddress">')[1].split("<")[0]
                    zc = add.rsplit(" ", 1)[1]
                    add = add.split(",")[0]
                if '"addressLocality" content="' in line2:
                    city = line2.split('"addressLocality" content="')[1].split('"')[0]
                if '"addressRegion" content="' in line2:
                    state = line2.split('"addressRegion" content="')[1].split('"')[0]
                if '"telephone": "' in line2:
                    phone = line2.split('"telephone": "')[1].split('"')[0]
            hours = "Mon-Sun: 8:00AM-11:00PM"
            if city == "London" and country == "GB":
                state = "<MISSING>"
                zc = "HA9 0JT"
                add = "Boxpark Wembley, Units 32&33, 18 Olympic Way"
                city = "Wembley"
            if "Windsor" in name:
                add = "2451 Dougall Ave"
                city = "Windsor"
                state = "ON"
                zc = "N8X 1T3"
            name = name.replace("&amp;", "&")
            if "https://badaxethrowing.com/locations/axe-throwing-burlington" in loc:
                zc = "<MISSING>"
            if "https://badaxethrowing.com/locations/axe-throwing-kitchener" in loc:
                zc = "<MISSING>"
            if (
                "ottawa" in loc
                or "mississ" in loc
                or "vaughan" in loc
                or "waterloo" in loc
                or "surrey" in loc
                or "winnipeg" in loc
            ):
                zc = "<MISSING>"
            if CS is False:
                if (
                    "0" not in zc
                    and "1" not in zc
                    and "2" not in zc
                    and "3" not in zc
                    and "4" not in zc
                    and "5" not in zc
                    and "6" not in zc
                    and "7" not in zc
                    and "8" not in zc
                ):
                    zc = "<MISSING>"
                if "#" in zc:
                    zc = "<MISSING>"
                if "Evarts St" in add:
                    zc = "20018"
                if "30 Hill St" in add:
                    zc = "94014"
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
