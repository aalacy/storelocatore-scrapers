import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("weightwatchers_com")


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
    locinfo = []
    url = "https://www.weightwatchers.com/us/sitemap-location.xml"
    r = session.get(url, headers=headers, stream=True)
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if "<loc>https://www.weightwatchers.com/us/find-a-workshop/" in line:
            lurl = line.split("<loc>")[1].split("<")[0]
            if lurl not in locs:
                locs.append(lurl)
    website = "weightwatchers.com"
    country = "US"
    for loc in locs:
        logger.info(loc)
        name = ""
        typ = "<MISSING>"
        add = ""
        city = ""
        state = ""
        zc = ""
        store = ""
        phone = ""
        lat = ""
        lng = ""
        hours = ""
        r2 = session.get(loc, headers=headers)
        for line2 in r2.iter_lines():
            line2 = str(line2.decode("utf-8"))
            if '{"locationInfo":' in line2:
                name = line2.split('"name":"')[1].split('"')[0]
                store = line2.split('"id":')[1].split(",")[0]
                add = (
                    line2.split('"address":{"address1":"')[1].split('"')[0]
                    + " "
                    + line2.split('"address2":"')[1].split('"')[0]
                )
                add = add.strip()
                city = line2.split('"city":"')[1].split('"')[0]
                state = line2.split('"state":"')[1].split('"')[0]
                zc = line2.split('"zipCode":"')[1].split('"')[0]
                lat = line2.split('"latitude":')[1].split(",")[0]
                lng = line2.split('"longitude":')[1].split("}")[0]
                phone = "<MISSING>"
            if '<div class="dayName' in line2:
                days = line2.split('<div class="dayName')
                for day in days:
                    if '<div class="times' in day:
                        day = (
                            day.replace("<!-- -->", "")
                            .replace('</span><span class="time-35INk">', ", ")
                            .replace("</span>", "")
                            .replace('<span class="time-35INk">', "")
                        )
                        hrs = (
                            day.split('">')[1].split("<")[0]
                            + ": "
                            + day.split('<div class="times')[1]
                            .split('">')[1]
                            .split("</div></div>")[0]
                        )
                        if hours == "":
                            hours = hrs
                        else:
                            hours = hours + "; " + hrs
        if hours == "":
            hours = "<MISSING>"
        info = add + "|" + city
        if info not in locinfo and city != "":
            locinfo.append(info)
            if "Zoom.com" in add:
                add = "<MISSING>"
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
