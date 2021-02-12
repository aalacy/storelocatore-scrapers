import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("ginospizza_com")


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
    url = "http://ginospizza.com/Locations.aspx"
    r = session.get(url, headers=headers)
    website = "ginospizza.com"
    typ = "<MISSING>"
    country = "US"
    loc = "<MISSING>"
    logger.info("Pulling Stores")
    coords = []
    cnum = -1
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if "BasicGoogleMaps_map," in line:
            llat = line.split("BasicGoogleMaps_map,")[1].split(",")[0].strip()
            llng = line.split("BasicGoogleMaps_map,")[1].split(",")[1].strip()
            lid = line.split("BasicGoogleMaps[")[1].split("]")[0]
            coords.append(lid + "|" + llat + "|" + llng)
    r = session.get(url, headers=headers)
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if "ctl01_BasicGoogleMaps.push(" in line:
            lat = ""
            lng = ""
            cnum = cnum + 1
            for pair in coords:
                if pair.split("|")[0] == str(cnum):
                    lat = pair.split("|")[1]
                    lng = pair.split("|")[2]
            name = line.split('"Header\\">')[1].split("<")[0].strip()
            add = line.split("</span><br />")[1].split("<")[0].strip()
            csz = line.split("<br />")[2].split("<")[0].strip()
            city = csz.split(",")[0]
            store = "<MISSING>"
            state = csz.split(",")[1].strip().split(" ")[0]
            zc = csz.rsplit(" ", 1)[1]
            phone = line.split("<br />")[3].strip()
            hours = (
                line.split("<br />")[4].strip().replace("  ", " ").replace("  ", " ")
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
