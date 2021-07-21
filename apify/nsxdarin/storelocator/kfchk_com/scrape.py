import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("kfchk_com")


def write_output(data):
    with open("data.csv", mode="w", encoding="utf-8") as output_file:
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
    url = "https://corp.kfchk.com/filemanager/system/en/js/restaurant.js"
    r = session.get(url, headers=headers)
    website = "kfchk.com"
    typ = "<MISSING>"
    country = "HK"
    loc = "<MISSING>"
    store = "<MISSING>"
    lat = "<MISSING>"
    lng = "<MISSING>"
    locs = {}
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if ".name='" in line and "//" not in line:
            name = line.split(".name='")[1].split("';")[0]
            rid = line.split(".name")[0].strip().replace("\t", "")
            add = ""
            phone = ""
            hrs = ""
            state = ""
        if ".address='" in line and "//" not in line:
            add = line.split(".address='")[1].split("';")[0]
        if ".openingtime.push('" in line and "//" not in line:
            hrs = line.split(".openingtime.push('")[1].split("');")[0]
        if ".tel.push('" in line and "//" not in line:
            phone = line.split(".tel.push('")[1].split("');")[0]
        if ".fax.push(" in line:
            locs[rid] = name + "|" + add + "|" + phone + "|" + hrs
        if (
            ".addChild(" in line
            and "//" not in line
            and "root_restaurant" not in line
            and "hki.addChild" not in line
            and "kowloon.addChild" not in line
            and "nt.addChild" not in line
            and "macau.addChild" not in line
            and "outlying_islands." not in line
        ):
            rid = line.split("(")[1].split(")")[0]
            info = locs[rid]
            name = info.split("|")[0]
            add = info.split("|")[1]
            phone = info.split("|")[2]
            hours = info.split("|")[3]
            zc = "<MISSING>"
            city = "<MISSING>"
            state = "<MISSING>"
            name = name.replace("\\'", "'")
            add = add.replace("\\'", "'")
            if "Hong Kong" in add:
                city = "Hong Kong"
                add = add.replace("Hong Kong", "").strip()
            if "Kowloon" in add:
                city = "Kowloon"
                add = add.replace("Kowloon", "").strip()
            if "Macau" in add:
                city = "Macau"
                add = add.replace("Macau", "").strip()
                country = "MO"
            if hours == "":
                hours = "<MISSING>"
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
