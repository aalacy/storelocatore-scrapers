import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("mayoclinichealthsystem_org")


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
    url = "https://www.mayoclinichealthsystem.org/HealthSystemInternet/LocationAddress/GetLocationMapRailResults?page=1&pageSize=100&sourceLat=44.02209&sourceLong=-92.46997&activeSite=hsinternet"
    r = session.get(url, headers=headers)
    infos = []
    website = "mayoclinichealthsystem.org"
    typ = "<MISSING>"
    country = "US"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if '<a href="/locations/' in line:
            locs.append(
                "https://www.mayoclinichealthsystem.org"
                + line.split('href="')[1].split('"')[0]
            )
    for loc in locs:
        logger.info(loc)
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
        r2 = session.get(loc, headers=headers)
        for line2 in r2.iter_lines():
            line2 = str(line2.decode("utf-8"))
            if '<h5 class="list-item-name">' in line2 and "</h5>" in line2:
                if add != "":
                    addinfo = add + "|" + city + "|" + typ
                    if phone == "":
                        phone = "<MISSING>"
                    if addinfo not in infos:
                        infos.append(addinfo)
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
                add = ""
                city = ""
                state = ""
                zc = ""
                hours = ""
                phone = ""
                typ = line2.split('<h5 class="list-item-name">')[1].split("<")[0]
            if '<address class="list-item-address">' in line2 and add == "":
                addinfo = line2.split('<address class="list-item-address">')[1].split(
                    "<"
                )[0]
                if addinfo.count(",") == 2:
                    add = line2.split('<address class="list-item-address">')[1].split(
                        ","
                    )[0]
                    city = line2.split(",")[1].strip()
                    state = line2.split(",")[2].strip().split(" ")[0]
                    name = city + ", " + state
                    zc = line2.split(",")[2].strip().split(" ")[1].split("<")[0]
                elif addinfo.count(",") == 3:
                    add = line2.split('<address class="list-item-address">')[1].split(
                        ","
                    )[0]
                    add = add + " " + line2.split(",")[1].strip()
                    city = line2.split(",")[2].strip()
                    state = line2.split(",")[3].strip().split(" ")[0]
                    zc = line2.split(",")[3].strip().split(" ")[1].split("<")[0]
                else:
                    add = line2.split('<address class="list-item-address">')[1].split(
                        ","
                    )[0]
                    add = add + " " + line2.split(",")[1].strip()
                    add = add + " " + line2.split(",")[2].strip()
                    city = line2.split(",")[3].strip()
                    state = line2.split(",")[4].strip().split(" ")[0]
                    zc = line2.split(",")[4].strip().split(" ")[1].split("<")[0]
            if "href='tel://" in line2:
                phone = line2.split("href='tel://")[1].split("'")[0]
            if "Hours:</li><li><span>" in line2:
                hours = line2.split("Hours:</li><li><span>")[1].split("</ul>")[0]
                hours = (
                    hours.replace("</span>", ": ")
                    .replace("</li><li><span>", "; ")
                    .replace("</li>", "")
                )
                hours = hours.replace("::", ":")
                if "<li>" in hours:
                    hours = hours.split("<li>")[0].strip()
            if "</html>" in line2:
                if add != "":
                    addinfo = add + "|" + city + "|" + typ
                    if phone == "":
                        phone = "<MISSING>"
                    if addinfo not in infos:
                        infos.append(addinfo)
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
