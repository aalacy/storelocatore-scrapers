import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("tkmaxx_com")


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
    url = "https://www.tkmaxx.com/medias/Store-en-GBP-14037155091650361914.xml?context=bWFzdGVyfHJvb3R8OTIxNTd8dGV4dC94bWx8aDU5L2gwOS8xMTY0NTQyOTQ4MTUwMi54bWx8ZTNkOTExNDdhMjE2NmIxNjhjMWQzZDI0OTdhODA4NGIwMzM3Mjk2MjhhYjdjMDZlYWQ2NGFmZWQzZmU3OTYyYw"
    r = session.get(url, headers=headers)
    website = "tkmaxx.com"
    typ = "<MISSING>"
    country = "GB"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if "<loc>https://www.tkmaxx.com/uk/en/store/" in line:
            locs.append(line.split("<loc>")[1].split("?")[0])
    for loc in locs:
        logger.info(loc)
        name = ""
        add = ""
        city = ""
        state = ""
        zc = ""
        store = loc.rsplit("/", 1)[1]
        phone = ""
        lat = ""
        lng = ""
        hours = ""
        r2 = session.get(loc, headers=headers)
        for line2 in r2.iter_lines():
            line2 = str(line2.decode("utf-8"))
            if '"description" content="' in line2:
                name = line2.split('"description" content="')[1].split('"')[0]
            if '"latitude":"' in line2:
                lat = line2.split('"latitude":"')[1].split('"')[0]
                lng = line2.split('"longitude":"')[1].split('"')[0]
                addinfo = (
                    line2.split('"name":"')[1]
                    .split("</div><div>", 1)[1]
                    .split("</div><div>United Kingdom")[0]
                )
                if addinfo.count("</div><div>") == 3:
                    add = (
                        addinfo.split("</div><div>")[0]
                        + " "
                        + addinfo.split("</div><div>")[1]
                    )
                    city = addinfo.split("</div><div>")[2]
                    state = "<MISSING>"
                    zc = addinfo.split("</div><div>")[3]
                else:
                    add = addinfo.split("</div><div>")[0]
                    city = addinfo.split("</div><div>")[1]
                    state = "<MISSING>"
                    zc = addinfo.split("</div><div>")[2]
            if '<a href="tel://' in line2:
                phone = line2.split('<a href="tel://')[1].split('"')[0]
            if '--day">' in line2:
                hrs = line2.split('--day">')[1].split("<")[0].strip()
            if '--time">' in line2:
                hrs = hrs + ": " + line2.split('--time">')[1].split("<")[0].strip()
                if hours == "":
                    hours = hrs
                else:
                    hours = hours + "; " + hrs
        if "TK Maxx" in name:
            typ = "TK Maxx"
        if "Homesense" in name:
            typ = "Homesense"
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
