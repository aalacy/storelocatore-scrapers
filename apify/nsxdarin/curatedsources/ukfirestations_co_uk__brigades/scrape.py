import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgpostal import parse_address_intl

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("ukfirestations_co_uk__brigades")


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
    divs = []
    url = "http://www.ukfirestations.co.uk/brigades/"
    r = session.get(url, headers=headers)
    website = "ukfirestations.co.uk/brigades"
    typ = "<MISSING>"
    country = "GB"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if (
            '<a href="http://www.ukfirestations.co.uk/stations/' in line
            and "info.slug" not in line
        ):
            divs.append(line.split('href="')[1].split('"')[0])
    for div in divs:
        r2 = session.get(div, headers=headers)
        logger.info(div)
        for line2 in r2.iter_lines():
            line2 = str(line2.decode("utf-8"))
            if (
                '<a href="http://www.ukfirestations.co.uk/station/' in line2
                and "info.slug" not in line2
            ):
                locs.append(line2.split('href="')[1].split('"')[0])
    for loc in locs:
        logger.info(loc)
        name = ""
        add = ""
        city = ""
        state = "<MISSING>"
        zc = ""
        store = "<MISSING>"
        phone = "<MISSING>"
        lat = ""
        lng = ""
        hours = "<MISSING>"
        r2 = session.get(loc, headers=headers)
        for line2 in r2.iter_lines():
            line2 = str(line2.decode("utf-8"))
            if "Address</strong><br/>" in line2:
                rawadd = line2.split("Address</strong><br/>")[1].split("<")[0]
                rawadd = rawadd.replace(", UK", "").replace(", United Kingdom", "")
                addr = parse_address_intl(rawadd)
                city = addr.city
                zc = addr.postcode
                add = addr.street_address_1
            if "LatLng(" in line2:
                lat = line2.split("LatLng(")[1].split(",")[0]
                lng = line2.split("LatLng(")[1].split(",")[1].strip().split(")")[0]
            if '[{"name":"' in line2:
                name = line2.split('[{"name":"')[1].split('"')[0]
        if add == "" or add is None:
            add = "<MISSING>"
        if city == "" or city is None:
            city = "<MISSING>"
        if zc == "" or zc is None:
            zc = "<MISSING>"
        name = name.replace("&amp;#039;", "'").replace("&amp;", "&")
        add = add.replace("&amp;#039;", "'").replace("&amp;", "&")
        if city == "Keynes":
            city = "Milton Keynes"
        if city == "<MISSING>" and "Headquarters" not in loc:
            city = loc
        if "(" in city:
            city = city.split("(")[0].strip()
        if "station/alderney-1/" in loc:
            add = "St Martins"
        if "station/south-elmsall" in loc:
            add = "Barnsley Road"
        if "headquarters-12" in loc:
            add = "Barmston Mere"
        if ", Ireland" not in rawadd and ", Spain" not in rawadd:
            if add == "<MISSING>":
                try:
                    add = rawadd.split(",")[0].strip()
                except:
                    pass
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
