import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("basspro_com")


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
    url = "https://stores.basspro.com/"
    r = session.get(url, headers=headers)
    website = "basspro.com"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if ',"type":"main","url":"' in line:
            items = line.split(',"type":"main","url":"')
            for item in items:
                if '"website":"' in item:
                    lurl = item.split('"website":"')[1].split('"')[0]
                    if "stores." in lurl:
                        if '"location-name-brand-inline">Cabela' in item:
                            locs.append(lurl + "|Cabelas")
                        else:
                            locs.append(lurl + "|Bass Pro")

    for loc in locs:
        lurl = loc.split("|")[0]
        typ = loc.split("|")[1]
        country = "US"
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
        if ".com/ca" in lurl:
            country = "CA"
        r2 = session.get(lurl, headers=headers)
        for line2 in r2.iter_lines():
            line2 = str(line2.decode("utf-8"))
            if 'property="og:title" content="' in line2:
                name = line2.split('property="og:title" content="')[1].split('"')[0]
                name = name.split(" |")[0]
            if '<span class="c-address-street-1">' in line2 and add == "":
                add = line2.split('<span class="c-address-street-1">')[1].split("<")[0]
                city = line2.split('"addressLocality">')[1].split("<")[0]
                state = line2.split('itemprop="addressRegion">')[1].split("<")[0]
                zc = line2.split('itemprop="postalCode">')[1].split("<")[0].strip()
                phone = line2.split('main-number-link" href="tel:+')[1].split('"')[0]
            if 'itemprop="latitude" content="' in line2:
                lat = line2.split('itemprop="latitude" content="')[1].split('"')[0]
                lng = line2.split('itemprop="longitude" content="')[1].split('"')[0]
            if "Regular Store Hours</h3>" in line2 and hours == "":
                days = (
                    line2.split("Regular Store Hours</h3>")[1]
                    .split("data-days='[")[1]
                    .split("]}]")[0]
                    .split('"day":"')
                )
                for day in days:
                    if '"end":' in day:
                        hrs = (
                            day.split('"')[0]
                            + ": "
                            + day.split('"start":')[1].split("}")[0]
                            + "-"
                            + day.split('"end":')[1].split(",")[0]
                        )
                        if hours == "":
                            hours = hrs
                        else:
                            hours = hours + "; " + hrs
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
    yield [
        website,
        "<MISSING>",
        "Cabela's Calgary",
        "851-64th Avenue Northeast",
        "Calgary",
        "AB",
        "T2E 3B8",
        "CA",
        "<MISSING>",
        "(403) 910-0200",
        "Cabelas",
        "<MISSING>",
        "<MISSING>",
        "<MISSING>",
    ]
    yield [
        website,
        "<MISSING>",
        "Cabela's Edmonton",
        "15320 37 Street Northwest",
        "Edmonton",
        "AB",
        "T5Y 0S5",
        "CA",
        "<MISSING>",
        "(780) 670-6100",
        "Cabelas",
        "<MISSING>",
        "<MISSING>",
        "<MISSING>",
    ]
    yield [
        website,
        "<MISSING>",
        "Cabela's Edmonton",
        "6150 Currents Drive Northwest",
        "Edmonton",
        "AB",
        "T6W 0L7",
        "CA",
        "<MISSING>",
        "(780) 628-9200",
        "Cabelas",
        "<MISSING>",
        "<MISSING>",
        "<MISSING>",
    ]
    yield [
        website,
        "<MISSING>",
        "Cabela's Nanaimo",
        "6902 Island Highway North",
        "Nanaimo",
        "BC",
        "V9V 1P6",
        "CA",
        "<MISSING>",
        "(250) 390-7800",
        "Cabelas",
        "<MISSING>",
        "<MISSING>",
        "<MISSING>",
    ]
    yield [
        website,
        "<MISSING>",
        "Cabela's Abbotsford",
        "6150 Currents Drive Northwest",
        "Abbotsford",
        "BC",
        "V4M0B3",
        "CA",
        "<MISSING>",
        "(604) 948-6200",
        "Cabelas",
        "<MISSING>",
        "<MISSING>",
        "<MISSING>",
    ]
    yield [
        website,
        "<MISSING>",
        "Cabela's Winnipeg",
        "580 Sterling Lyon Parkway",
        "Winnipeg",
        "MB",
        "R3P 1E9",
        "CA",
        "<MISSING>",
        "(204) 786-8966",
        "Cabelas",
        "<MISSING>",
        "<MISSING>",
        "<MISSING>",
    ]
    yield [
        website,
        "<MISSING>",
        "Cabela's Barrie",
        "Park Place Center 50 Concert Way",
        "Barrie",
        "ON",
        "L4N 6N5",
        "CA",
        "<MISSING>",
        "(705) 735-8900",
        "Cabelas",
        "<MISSING>",
        "<MISSING>",
        "<MISSING>",
    ]
    yield [
        website,
        "<MISSING>",
        "Cabela's Ottawa",
        "3065 Palladium Drive",
        "Ottawa",
        "ON",
        "K2T 0N2",
        "CA",
        "<MISSING>",
        "(613) 319-8600",
        "Cabelas",
        "<MISSING>",
        "<MISSING>",
        "<MISSING>",
    ]
    yield [
        website,
        "<MISSING>",
        "Cabela's Regina",
        "4901 Gordon Road",
        "Regina",
        "SK",
        "S4W 0B7",
        "CA",
        "<MISSING>",
        "(306) 523-5900",
        "Cabelas",
        "<MISSING>",
        "<MISSING>",
        "<MISSING>",
    ]
    yield [
        website,
        "<MISSING>",
        "Cabela's Saskatoon",
        "1714 Preston Avenue North",
        "Saskatoon",
        "SK",
        "S7N 4Y1",
        "CA",
        "<MISSING>",
        "(306) 343-4868",
        "Cabelas",
        "<MISSING>",
        "<MISSING>",
        "<MISSING>",
    ]


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
