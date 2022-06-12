import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("hoag_org")


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
    infos = []
    url = "https://www.hoag.org/locations/"
    r = session.get(url, headers=headers)
    website = "hoag.org"
    typ = ""
    country = "US"
    logger.info("Pulling Stores")
    lines = r.iter_lines()
    for line in lines:
        line = str(line.decode("utf-8"))
        if '<li class="location-item">' in line:
            g = next(lines)
            g = str(g.decode("utf-8"))
            lurl = g.split('href="')[1].split('"')[0]
            if "#" in lurl:
                lurl = lurl.split("#")[0]
            if "http" not in lurl:
                lurl = "https://www.hoag.org/" + lurl
            lurl = lurl.replace("//loc", "/loc")
            if lurl not in locs:
                locs.append(lurl + "|" + typ)
        if "</h2>" in line and "<h2>" in line:
            typ = line.split("<h2>")[1].split("<")[0]
    allinfo = []
    for loc in locs:
        lurl = loc.split("|")[0]
        typ = loc.split("|")[1]
        logger.info(lurl)
        name = ""
        add = ""
        city = ""
        state = ""
        zc = ""
        store = "<MISSING>"
        phone = ""
        lat = ""
        lng = ""
        hours = ""
        if "hoagurgentcare" in lurl:
            r2 = session.get(lurl, headers=headers)
            lines2 = r2.iter_lines()
            for line2 in lines2:
                line2 = str(line2.decode("utf-8"))
                if '<a name="' in line2:
                    lineinfo = line2.replace('<span style="color: #003e68;">', "")
                    name = lineinfo.split('"></a>')[1].split("<")[0]
                if 'href="https://www.google.com/maps/dir/' in line2:
                    lat = line2.split("/@")[1].split(",")[0]
                    lng = line2.split("/@")[1].split(",")[1]
                if "ADDRESS:</strong><br />" in line2:
                    g = next(lines2)
                    h = next(lines2)
                    g = str(g.decode("utf-8"))
                    h = str(h.decode("utf-8"))
                    add = g.split("<")[0]
                    city = h.split(",")[0]
                    state = h.split(",")[1].strip().split(" ")[0]
                    zc = h.split("<")[0].rsplit(" ", 1)[1]
                if "PHONE:" in line2:
                    phone = line2.split("PHONE:")[1].split(">")[1].split("<")[0]
                    if add != "":
                        info = name + "|" + add + "|" + city
                        if info not in allinfo:
                            allinfo.append(info)
                            if " - " in name:
                                name = name.split(" - ")[0]
                            if phone == "":
                                phone = "<MISSING>"
                            addinfo = add + "|" + city + "|" + zc
                            if addinfo not in infos:
                                infos.append(addinfo)
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
                if "HOURS:" in line2 and "HOLIDAY" not in line2:
                    g = next(lines2)
                    h = next(lines2)
                    g = str(g.decode("utf-8"))
                    h = str(h.decode("utf-8"))
                    hours = g.split("<")[0] + "; " + h.split("<")[0]
        if "hoag.org/locations/" in lurl:
            r2 = session.get(lurl, headers=headers)
            lines2 = r2.iter_lines()
            lat = "<MISSING>"
            lng = "<MISSING>"
            for line2 in lines2:
                line2 = str(line2.decode("utf-8"))
                if "<title>" in line2:
                    name = line2.split("<title>")[1].split("<")[0]
                    if " | " in name:
                        name = name.split(" | ")[0]
                if 'itemprop="streetAddress">' in line2:
                    add = line2.split('itemprop="streetAddress">')[1].split("<")[0]
                if 'itemprop="addressLocality">' in line2:
                    city = line2.split('itemprop="addressLocality">')[1].split("<")[0]
                if 'itemprop="addressRegion">' in line2:
                    state = line2.split('itemprop="addressRegion">')[1].split("<")[0]
                if 'itemprop="postalCode">' in line2:
                    zc = line2.split('itemprop="postalCode">')[1].split("<")[0]
                if '"telephone"' in line2:
                    phone = line2.split('"telephone"')[1].split(">")[1].split("<")[0]
            hours = "<MISSING>"
            if " - " in name:
                name = name.split(" - ")[0]
            if add != "":
                if phone == "":
                    phone = "<MISSING>"
                addinfo = add + "|" + city + "|" + zc
                if addinfo not in infos:
                    infos.append(addinfo)
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
    url = "https://www.hoagorthopedicinstitute.com/locations/"
    r = session.get(url, headers=headers)
    locs = []
    typ = "Orthopedic"
    hours = "<MISSING>"
    store = "<MISSING>"
    country = "US"
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if '<meta itemprop="name" content="' in line:
            name = line.split('<meta itemprop="name" content="')[1].split('"')[0]
        if '<meta itemprop="telephone" content="' in line:
            phone = line.split('<meta itemprop="telephone" content="')[1].split('"')[0]
        if '<meta itemprop="streetAddress" content="' in line:
            add = line.split('<meta itemprop="streetAddress" content="')[1].split('"')[
                0
            ]
        if '<meta itemprop="addressLocality" content="' in line:
            city = line.split('<meta itemprop="addressLocality" content="')[1].split(
                '"'
            )[0]
        if '<meta itemprop="addressRegion" content="' in line:
            state = line.split('<meta itemprop="addressRegion" content="')[1].split(
                '"'
            )[0]
        if '<meta itemprop="postalCode" content="' in line:
            zc = line.split('<meta itemprop="postalCode" content="')[1].split('"')[0]
        if 'data-latitude="' in line:
            lat = line.split('data-latitude="')[1].split('"')[0]
            lng = line.split('data-longitude="')[1].split('"')[0]
        if '<a href="tel:' in line:
            phone = line.split('<a href="tel:')[1].split('"')[0]
        if '<meta itemprop="url" content="' in line:
            lurl = line.split('<meta itemprop="url" content="')[1].split('"')[0]
            addinfo = add + "|" + city + "|" + zc
            if addinfo not in infos:
                infos.append(addinfo)
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
