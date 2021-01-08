import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("batterysystems_net")


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
    url = "https://www.batterysystems.net/pointofsale"
    r = session.get(url, headers=headers)
    website = "batterysystems.com"
    typ = "<MISSING>"
    country = "US"
    loc = "<MISSING>"
    store = "<MISSING>"
    lat = "<MISSING>"
    lng = "<MISSING>"
    logger.info("Pulling Stores")
    lines = r.iter_lines()
    for line in lines:
        line = str(line.decode("utf-8"))
        if '<i class="porto-icon-down-open" style=""></i>' in line:
            name = line.split('">')[1].split("<")[0]
        if 'style="display:none">' in line:
            next(lines)
            g = next(lines)
            g = str(g.decode("utf-8"))
            add = g.split("<br")[0].strip().replace("\t", "")
            if "/>" in add:
                add = add.split("/>")[1].strip()
            g = next(lines)
            g = str(g.decode("utf-8"))
            csz = g.split("<")[0].strip().replace("  ", " ")
            if csz.count(" ") == 2:
                city = csz.split(" ")[0]
                state = csz.split(" ")[1]
                zc = csz.split(" ")[2]
            elif csz.count(" ") == 3:
                city = csz.split(" ")[0] + " " + csz.split(" ")[1]
                state = csz.split(" ")[2]
                zc = csz.split(" ")[3]
            else:
                city = (
                    csz.split(" ")[0]
                    + " "
                    + csz.split(" ")[1]
                    + " "
                    + csz.split(" ")[2]
                )
                state = csz.split(" ")[3]
                zc = csz.split(" ")[4]
            g = next(lines)
            g = str(g.decode("utf-8"))
            try:
                phone = g.split(" ")[1]
            except:
                phone = "<MISSING>"
            g = next(lines)
            g = str(g.decode("utf-8"))
            if '="margin-top:10px"><strong>' in g:
                hours = g.split('="margin-top:10px"><strong>')[1].split("<")[0]
            else:
                hours = "<MISSING>"
            if phone == "":
                phone = "<MISSING>"
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
