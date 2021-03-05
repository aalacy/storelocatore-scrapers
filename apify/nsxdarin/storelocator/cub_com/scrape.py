import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("cub_com")


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
    urls = [
        "https://www.cub.com/stores/store-search-results.html?state=IL",
        "https://www.cub.com/stores/store-search-results.html?displayCount=250&state=MN",
    ]
    for url in urls:
        r = session.get(url, headers=headers)
        website = "cub.com"
        typ = "<MISSING>"
        country = "US"
        logger.info("Pulling Stores")
        for line in r.iter_lines():
            line = str(line.decode("utf-8"))
            if 'data-storelat="' in line:
                llat = line.split('data-storelat="')[1].split('"')[0]
                llng = line.split('data-storelng="')[1].split('"')[0]
            if 'href="/stores/view-store.' in line:
                locs.append(
                    "https://www.cub.com"
                    + line.split('href="')[1].split('"')[0]
                    + "|"
                    + llat
                    + "|"
                    + llng
                )
    for loc in locs:
        lurl = loc.split("|")[0]
        logger.info(lurl)
        name = ""
        add = ""
        city = ""
        state = ""
        zc = ""
        store = lurl.split("store.")[1].split(".")[0]
        phone = ""
        lat = loc.split("|")[1]
        lng = loc.split("|")[2]
        hours = ""
        HFound = False
        r2 = session.get(lurl, headers=headers)
        for line2 in r2.iter_lines():
            line2 = str(line2.decode("utf-8"))
            if '<h2 class="storeName" itemprop="name">' in line2:
                name = line2.split('<h2 class="storeName" itemprop="name">')[1].split(
                    "<"
                )[0]
            if '="streetAddress">' in line2:
                add = line2.split('="streetAddress">')[1].split("<")[0]
            if '"addressLocality">' in line2:
                city = line2.split('"addressLocality">')[1].split("<")[0]
                state = line2.split('"addressRegion">')[1].split("<")[0]
                zc = line2.split('"postalCode">')[1].split("<")[0]
            if 'itemprop="telephone" content="' in line2:
                phone = (
                    line2.split('itemprop="telephone" content="')[1]
                    .split('"')[0]
                    .replace("+", "")
                )
            if "ours:</b></p>" in line2 and hours == "":
                HFound = True
            if HFound and "</ul>" in line2:
                HFound = False
            if HFound and 'itemprop="openingHours"' in line2:
                hrs = line2.split('">')[1].split("<")[0]
                if hours == "":
                    hours = hrs
                else:
                    hours = hours + "; " + hrs
        if phone == "":
            phone = "<MISSING>"
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
