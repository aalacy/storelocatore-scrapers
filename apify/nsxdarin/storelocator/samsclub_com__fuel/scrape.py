import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup
import time

logger = SgLogSetup().get_logger("samsclub_com__fuel")

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
    session = SgRequests()
    url = "https://www.samsclub.com/sitemap_locators.xml"
    r = session.get(url, headers=headers)
    if r.encoding is None:
        r.encoding = "utf-8"
    for line in r.iter_lines(decode_unicode=True):
        if "<loc>https://www.samsclub.com/club/" in line:
            lurl = line.split("<loc>")[1].split("<")[0]
            locs.append(lurl)
    for loc in locs:
        Fuel = False
        logger.info(("Pulling Location %s..." % loc))
        website = "samsclub.com/fuel"
        typ = "Gas"
        hours = ""
        name = ""
        country = "US"
        city = ""
        add = ""
        zc = ""
        state = ""
        lat = ""
        lng = ""
        phone = ""
        session = SgRequests()
        time.sleep(3)
        store = loc.rsplit("/", 1)[1]
        locurl = "https://www.samsclub.com/api/node/clubfinder/" + store
        r2 = session.get(locurl, headers=headers)
        if r2.encoding is None:
            r2.encoding = "utf-8"
        for line2 in r2.iter_lines(decode_unicode=True):
            if '"postalCode":"' in line2 and '"displayName":"Fuel Center"' in line2:
                Fuel = True
                name = line2.split('"name":"')[1].split('"')[0]
                zc = line2.split('"postalCode":"')[1].split('"')[0]
                try:
                    add = line2.split('"address1":"')[1].split('"')[0]
                except:
                    add = ""
                try:
                    add = add + " " + line2.split('"address2":"')[1].split('"')[0]
                except:
                    pass
                city = line2.split('"city":"')[1].split('"')[0]
                state = line2.split('"state":"')[1].split('"')[0]
                phone = line2.split('"phone":"')[1].split('"')[0]
                lat = line2.split('"latitude":')[1].split("}")[0]
                lng = line2.split('"longitude":')[1].split(",")[0]
                try:
                    fcinfo = line2.split(
                        '"displayName":"Fuel Center","operationalHours":{'
                    )[1].split("}}},")[0]
                    days = fcinfo.split('},"')
                    for day in days:
                        hrs = (
                            day.split('"startHr":"')[1].split('"')[0]
                            + "-"
                            + day.split('"endHr":"')[1].split('"')[0]
                        )
                        dname = day.split('Hrs":')[0].replace('"', "")
                        hrs = dname + ": " + hrs
                        hrs = hrs.replace("To", "-")
                        if hours == "":
                            hours = hrs
                        else:
                            hours = hours + "; " + hrs
                except:
                    hours = ""
        if hours == "":
            hours = "<MISSING>"
        if phone == "":
            phone = "<MISSING>"
        if Fuel is True and add != "":
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
