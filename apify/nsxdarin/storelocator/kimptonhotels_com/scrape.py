import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("kimptonhotels_com")

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


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
    locs = []
    url = "https://www.ihg.com/bin/sitemapindex.xml"
    r = session.get(url, headers=headers)
    brand = "kimptonhotels"
    brand_string = brand + ".en.hoteldetail.xml"
    smurl = ""
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if brand_string in line:
            smurl = line.split("<loc>")[1].split("<")[0]
    r = session.get(smurl, headers=headers)
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if 'hreflang="en" rel="alternate">' in line:
            lurl = line.split('href="')[1].split('"')[0]
            if lurl not in locs:
                locs.append(lurl.replace("localhost:4503", ""))
    for loc in locs:
        logger.info(loc)
        r2 = session.get(loc, headers=headers)
        website = "kimptonhotels.com"
        name = ""
        city = ""
        state = ""
        country = ""
        add = ""
        zc = ""
        typ = "Hotel"
        phone = ""
        hours = "<MISSING>"
        lat = ""
        lng = ""
        rawadd = ""
        store = loc.split("/hoteldetail")[0].rsplit("/", 1)[1]
        for line2 in r2.iter_lines():
            line2 = str(line2.decode("utf-8"))
            if 'property="og:title" content="' in line2 and name == "":
                name = line2.split('property="og:title" content="')[1].split('"')[0]
            if '<span class="visible-content">' in line2 and rawadd == "":
                rawadd = line2.split('<span class="visible-content">')[1].split(
                    "</span>"
                )[0]
                country = rawadd.rsplit("<br/>", 1)[1]
                add = rawadd.split("<br/>")[0]
                if rawadd.count("<br/>") == 3:
                    add = add + " " + rawadd.split("<br/>")[1]
                    city = rawadd.split("<br/>")[2].rsplit(" ", 1)[0]
                    state = "<MISSING>"
                    zc = rawadd.split("<br/>")[2].rsplit(" ", 1)[1]
                else:
                    zc = rawadd.split("<br/>")[1].rsplit(" ", 1)[1]
                    city = rawadd.split("<br/>")[1].rsplit(" ", 1)[0]
            if 'property="place:location:latitude"' in line2:
                lat = (
                    line2.split('property="place:location:latitude')[1]
                    .split('content="')[1]
                    .split('"')[0]
                )
            if 'property="place:location:longitude"' in line2:
                lng = (
                    line2.split('property="place:location:longitude"')[1]
                    .split('content="')[1]
                    .split('"')[0]
                )
            if phone == "" and '<a href="tel:' in line2:
                phone = line2.split('<a href="tel:')[1].split('"')[0]
        if " Hotels" not in name and name != "":
            if country == "United States":
                state = city.rsplit(" ", 1)[1]
                city = city.rsplit(" ", 1)[0]
            if state == "":
                state = "<MISSING>"
            if country == "United Kingdom":
                state = "<MISSING>"
            if country == "Canada":
                state = city.split(" ")[1]
                zc = city.rsplit(" ", 1)[1] + " " + zc
                city = city.split(" ")[1]
            if country == "United Kingdom":
                state = "<MISSING>"
                zc = city.rsplit(" ", 1)[1] + " " + zc
                city = city.split(" ")[1]
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
