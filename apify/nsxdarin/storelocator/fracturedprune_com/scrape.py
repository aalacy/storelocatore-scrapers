import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("fracturedprune_com")

session = SgRequests()
headers = {
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
    url = "https://fracturedprune.com/locations/"
    locs = []
    website = "fracturedprune.com"
    r = session.get(url, headers=headers, verify=False)
    if r.encoding is None:
        r.encoding = "utf-8"
    for line in r.iter_lines(decode_unicode=True):
        if '<h3><a href="https://fracturedprune.com/location/' in line:
            locs.append(line.split('href="')[1].split('"')[0])
    logger.info(("Found %s Locations." % str(len(locs))))
    for loc in locs:
        lurl = loc.split("|")[0]
        typ = "<MISSING>"
        name = ""
        add = ""
        city = ""
        state = ""
        store = ""
        lat = ""
        lng = ""
        hours = ""
        country = ""
        zc = ""
        phone = ""
        logger.info(("Pulling Location %s..." % lurl))
        r2 = session.get(lurl, headers=headers)
        if r2.encoding is None:
            r2.encoding = "utf-8"
        lines = r2.iter_lines(decode_unicode=True)
        for line2 in lines:
            if "<title>" in line2:
                name = line2.split("<title>")[1].split(" |")[0].replace("&#8211;", "-")
            if "Phone: " in line2:
                phone = line2.split("Phone: ")[1].split("<")[0]
            if '<span class="address">' in line2:
                g = next(lines)
                addinfo = g.split("</span>")[0].replace("\t", "").strip()
                if addinfo.count("<br/>") == 1:
                    add = addinfo.split("<")[0]
                    city = addinfo.split("<br/>")[1].strip().split(",")[0]
                    state = (
                        addinfo.split("<br/>")[1]
                        .strip()
                        .split(",")[1]
                        .split("<")[0]
                        .strip()
                        .rsplit(" ", 1)[0]
                    )
                    zc = (
                        addinfo.split("<br/>")[1]
                        .strip()
                        .split(",")[1]
                        .split("<")[0]
                        .strip()
                        .rsplit(" ", 1)[1]
                    )
                else:
                    add = (
                        addinfo.split("<")[0] + " " + addinfo.split("<br/>")[1].strip()
                    )
                    city = addinfo.split("<br/>")[2].strip().split(",")[0]
                    state = (
                        addinfo.split("<br/>")[2]
                        .strip()
                        .split(",")[1]
                        .split("<")[0]
                        .strip()
                        .rsplit(" ", 1)[0]
                    )
                    zc = (
                        addinfo.split("<br/>")[2]
                        .strip()
                        .split(",")[1]
                        .split("<")[0]
                        .strip()
                        .rsplit(" ", 1)[1]
                    )
                country = "US"
                store = "<MISSING>"
            if '<span class="day">' in line2:
                day = line2.split('<span class="day">')[1].split("<")[0]
                g = next(lines)
                hrs = g.split("<span>")[1].split("<")[0]
                if hours == "":
                    hours = day + ": " + hrs
                else:
                    hours = hours + "; " + day + ": " + hrs
            if 'class="latitude">' in line2:
                lat = line2.split('class="latitude">')[1].split("<")[0]
                lng = line2.split('<span class="longitude">')[1].split("<")[0]
        if hours == "":
            hours = "<MISSING>"
        if lat == "":
            lat = "<MISSING>"
        if lng == "":
            lng = "<MISSING>"
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
