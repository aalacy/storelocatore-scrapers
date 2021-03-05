import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("ae_com")


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
    url = "https://storelocations.ae.com/sitemap.xml"
    r = session.get(url, headers=headers)
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if (
            "<loc>https://storelocations.ae.com/ca/" in line
            or "<loc>https://storelocations.ae.com/us/" in line
        ):
            lurl = line.split(">")[1].split("<")[0]
            count = lurl.count("/")
            if count == 6:
                locs.append(lurl)
    for loc in locs:
        logger.info("Pulling Location %s..." % loc)
        website = "ae.com"
        typ = ""
        hours = ""
        phone = ""
        name = ""
        add = ""
        lat = ""
        lng = ""
        city = ""
        store = ""
        state = ""
        zc = ""
        if ".com/ca/" in loc:
            country = "CA"
        else:
            country = "US"
        r2 = session.get(loc, headers=headers)
        for line2 in r2.iter_lines():
            line2 = str(line2.decode("utf-8"))
            if "<title>" in line2:
                name = line2.split("<title>")[1].split("<")[0].replace("&amp;", "&")
            if "days='[" in line2:
                days = line2.split("days='[")[1].split("]}]'")[0].split('"day":"')
                for day in days:
                    if '"intervals":' in day:
                        dname = day.split('"')[0]
                        try:
                            hrs = (
                                day.split('"start":')[1].split("}")[0]
                                + "-"
                                + day.split('"end":')[1].split(",")[0]
                            )
                            if hours == "":
                                hours = dname + ": " + hrs
                            else:
                                hours = hours + "; " + dname + ": " + hrs
                        except:
                            hours = "CLOSED"
            if '<span class="c-address-street-1">' in line2:
                add = line2.split('<span class="c-address-street-1">')[1].split("<")[0]
                if '<span class="c-address-street-2">' in line2:
                    add = (
                        add
                        + " "
                        + line2.split('<span class="c-address-street-2">')[1].split(
                            "<"
                        )[0]
                    )
                city = line2.split('<span class="c-address-city">')[1].split("<")[0]
                state = line2.split('itemprop="addressRegion">')[1].split("<")[0]
                zc = line2.split('itemprop="postalCode">')[1].split("<")[0]
                phone = line2.split('itemprop="telephone">')[1].split("<")[0]
                lat = line2.split('type="text/data">{"latitude":')[1].split(",")[0]
                lng = line2.split(',"longitude":')[1].split("}")[0]
        if hours == "":
            hours = "<MISSING>"
        if phone == "":
            phone = "<MISSING>"
        if "American Eagle" in name:
            if "Aerie" in name:
                typ = "American Eagle & Aerie"
            else:
                typ = "American Eagle"
        if "Aerie" in name and "American Eagle" not in name:
            typ = "Aerie"
        store = "<MISSING>"
        if city != "" and hours != "CLOSED":
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
