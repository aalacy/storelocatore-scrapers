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
    website = "batterysystems.net"
    typ = "<MISSING>"
    country = "US"
    locinfo = []
    alllocs = []
    loc = "<MISSING>"
    store = "<MISSING>"
    lat = "<MISSING>"
    lng = "<MISSING>"
    logger.info("Pulling Stores")
    lines = r.iter_lines()
    for line in lines:
        line = str(line.decode("utf-8"))
        if "pointofsale.places" in line:
            items = line.split('{"id":"')
            for item in items:
                if '"title":' in item:
                    iid = item.split('"')[0]
                    ilat = item.split('"lat":"')[1].split('"')[0]
                    ilng = item.split('"lng":"')[1].split('"')[0]
                    locinfo.append(iid + "|" + ilat + "|" + ilng)
        if '<i class="porto-icon-down-open" style=""></i>' in line:
            store = line.split('id="')[1].split('"')[0]
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
            if (
                "a" not in csz
                and "e" not in csz
                and "i" not in csz
                and "o" not in csz
                and "u" not in csz
            ):
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
            loc = "https://www.batterysystems.net/pointofsale"
            if "Sioux Falls South" in city:
                city = "Sioux Falls"
                state = "South Dakota"
            if "Fargo North" in city:
                city = "Fargo"
                state = "North Dakota"
            if "West Caldwell New" in city:
                city = "West Caldwell"
                state = "New Jersey"
            if "Albuquerque New" in city:
                city = "Albuquerque"
                state = "New Mexico"
            if "Charlotte North" in city or "Clayton North" in city:
                city = city.replace(" North", "")
                state = "North Carolina"
            if state == "York":
                state = "New York"
                city = city.replace(" New", "")
            infotext = []
            infotext.append(website)
            infotext.append(loc)
            infotext.append(name)
            infotext.append(add)
            infotext.append(city)
            infotext.append(state)
            infotext.append(zc)
            infotext.append(country)
            infotext.append(store)
            infotext.append(phone)
            infotext.append(typ)
            infotext.append(lat)
            infotext.append(lng)
            infotext.append(hours)
            alllocs.append(infotext)
    for item in alllocs:
        for sitem in locinfo:
            if sitem.split("|")[0] == item[8]:
                item[11] = sitem.split("|")[1]
                item[12] = sitem.split("|")[2]
                yield [
                    item[0],
                    item[1],
                    item[2],
                    item[3],
                    item[4],
                    item[5],
                    item[6],
                    item[7],
                    item[8],
                    item[9],
                    item[10],
                    item[11],
                    item[12],
                    item[13],
                ]


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
