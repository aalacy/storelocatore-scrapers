import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("health-street_net")

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
    locs = []
    sms = []
    locinfo = []
    url = "https://www.health-street.net/sitemap_index.xml"
    r = session.get(url, headers=headers)
    website = "health-street.net"
    country = "US"
    typ = "<MISSING>"
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if "<loc>https://www.health-street.net/location-sitemap" in line:
            sms.append(line.split("<loc>")[1].split("<")[0])
    for sm in sms:
        r2 = session.get(sm, headers=headers)
        for line2 in r2.iter_lines():
            line2 = str(line2.decode("utf-8"))
            if "<loc>https://www.health-street.net/location/" in line2:
                locs.append(line2.split("<loc>")[1].split("<")[0])
    for loc in locs:
        names = []
        logger.info(loc)
        lat = ""
        lng = ""
        hours = ""
        phone = ""
        rll = session.get(loc, headers=headers)
        for line2 in rll.iter_lines():
            line2 = str(line2.decode("utf-8"))
            if "lat:" in line2:
                try:
                    lat = line2.split("lat:")[1].split(",")[0].strip()
                except:
                    lat = "<MISSING>"
            if "lng:" in line2:
                try:
                    lng = line2.split("lng:")[1].split("}")[0].strip()
                except:
                    lng = "<MISSING>"
        r2 = session.get(loc, headers=headers)
        lines = r2.iter_lines()
        for line2 in lines:
            line2 = str(line2.decode("utf-8"))
            if 'class="contact-us-span">(' in line2 and '<a href="tel:' in line:
                phone = line2.split('<a href="tel:')[1].split('"')[0]
            if '"telephone" : "' in line2 and phone == "":
                phone = line2.split('"telephone" : "')[1].split('"')[0]
            if 'font-weight: bold; font-size: 1.4em;">' in line2:
                items = line2.split('font-weight: bold; font-size: 1.4em;">')
                for item in items:
                    if "<em>Clinic Hours and Information</em>" not in item:
                        hours = ""
                        cname = item.split("</span>")[0].replace("|", "-")
                        try:
                            days = item.split("<span>")
                            for day in days:
                                if "day:" in day:
                                    if "<" in day:
                                        hrs = day.split("<")[0]
                                    else:
                                        hrs = day
                                    if hours == "":
                                        hours = hrs
                                    else:
                                        hours = hours + "; " + hrs
                        except:
                            pass
                        names.append(cname + "|" + hours)
            if "position:" in line2 and "lat:" in line2:
                lat = line2.split("lat:")[1].split(",")[0].strip()
                lng = line2.split("lng:")[1].split("}")[0].strip()
            if '<span itemprop="streetaddress">' in line2:
                stores = line2.split('<span itemprop="streetaddress">')
                for sitem in stores:
                    if '<span itemprop="addresslocality">' in sitem:
                        add = (
                            line2.split('"streetaddress">')[1]
                            .split("<span")[0]
                            .replace("<br>", " ")
                            .strip()
                            .replace("</span>", "")
                        )
                        city = line2.split('<span itemprop="addresslocality">')[
                            1
                        ].split("<")[0]
                        state = line2.split('"addressregion">')[1].split("<")[0]
                        zc = line2.split('<span itemprop="postalcode">')[1].split("<")[
                            0
                        ]
                        aname = line2.split('<span itemprop="streetaddress">')[1].split(
                            "<"
                        )[0]
                        for pname in names:
                            if aname == pname.split("|")[0]:
                                hours = pname.split("|")[1]
                        if hours == "":
                            hours = "<MISSING>"
                        store = "<MISSING>"
                        hours = hours.replace("&#8211;", "-")
                        if lat == "":
                            lat = "<MISSING>"
                        if lng == "":
                            lng = "<MISSING>"
                        aname = aname.replace("&amp;", "&").replace("&amp", "&")
                        add = add.replace("&amp;", "&").replace("&amp", "&")
                        infotext = aname + "|" + add + "|" + city + "|" + state
                        hours = hours.replace("&#8211;", "-")
                        if aname == "":
                            aname = (
                                loc.split("/location/")[1]
                                .replace("/", "")
                                .replace("-", "")
                                .title()
                            )
                        if add == "":
                            add = "<MISSING>"
                        if city == "":
                            city = "<MISSING>"
                        if state == "":
                            state = "<MISSING>"
                        if zc == "":
                            zc = "<MISSING>"
                        if phone == "":
                            phone = "<MISSING>"
                        if infotext not in locinfo:
                            locinfo.append(infotext)
                            yield [
                                website,
                                loc,
                                aname,
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
