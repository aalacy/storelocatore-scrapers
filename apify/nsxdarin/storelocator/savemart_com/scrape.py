import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

headers2 = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
    "x-csrf-token": "zc_E8epwKjSATpvVIYsNTGCX2g0Vt4k8KtIzhsDKpqM",
    "cookie": "__cfduid=d8cbc7c319285905869cfbf96e802dcc41609168361; has_js=1; session=1609168360692.c3ojkl; _ga=GA1.2.397327870.1609168361; _gid=GA1.2.1355532542.1609168361; SSESS9959bebbc61026450395fb229e88697e=O5ihuF5rruNfRypmeXXstai5nb6Mjp6v9Yn9Ip6KkM0; Srn-Auth-Token=8e5d3f0a711b0c80e122cbb539d2e29dc568dbf045c309942a9bce41d727ef66; XSRF-TOKEN=zc_E8epwKjSATpvVIYsNTGCX2g0Vt4k8KtIzhsDKpqM; _fbp=fb.1.1609168362033.2134773812; __zlcmid=11sjh1vinok8Ou0; _gat_UA-104557963-1=1; _gat_UA-102256819-1=1",
}

logger = SgLogSetup().get_logger("savemart_com")


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
    url = "https://www.savemart.com/sitemap.xml?page=2"
    r = session.get(url, headers=headers)
    website = "savemart.com"
    typ = "<MISSING>"
    country = "US"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if "<url><loc>https://www.savemart.com/stores/" in line:
            locs.append(line.split("<loc>")[1].split("<")[0])
    for loc in locs:
        logger.info(loc)
        name = ""
        add = ""
        city = ""
        state = ""
        zc = ""
        store = loc.rsplit("/", 1)[1]
        purl = "https://www.savemart.com/api/m_store_location/" + store
        phone = ""
        lat = ""
        lng = ""
        hours = ""
        r2 = session.get(purl, headers=headers2)
        for line2 in r2.iter_lines():
            line2 = str(line2.decode("utf-8"))
            if '"storeName":"' in line2:
                name = line2.split('"storeName":"')[1].split('"')[0]
                phone = line2.split('"phone":"')[1].split('"')[0]
                lng = line2.split('"longitude":')[1].split(",")[0]
                lat = line2.split('"latitude":')[1].split(",")[0]
                add = line2.split('"address":"')[1].split('"')[0]
                city = line2.split('"city":"')[1].split('"')[0]
                state = line2.split('"state":"')[1].split('"')[0]
                zc = line2.split('"zip":"')[1].split('"')[0]
                days = line2.split('"store_hours":[')[1].split("]")[0].split('"day":')
                hours = (
                    "Sun: "
                    + days[1].split('"open":"')[1].split('"')[0]
                    + "-"
                    + days[1].split('"close":"')[1].split('"')[0]
                )
                hours = (
                    hours
                    + "; Mon: "
                    + days[2].split('"open":"')[1].split('"')[0]
                    + "-"
                    + days[2].split('"close":"')[1].split('"')[0]
                )
                hours = (
                    hours
                    + "; Tue: "
                    + days[3].split('"open":"')[1].split('"')[0]
                    + "-"
                    + days[3].split('"close":"')[1].split('"')[0]
                )
                hours = (
                    hours
                    + "; Wed: "
                    + days[4].split('"open":"')[1].split('"')[0]
                    + "-"
                    + days[4].split('"close":"')[1].split('"')[0]
                )
                hours = (
                    hours
                    + "; Thu: "
                    + days[5].split('"open":"')[1].split('"')[0]
                    + "-"
                    + days[5].split('"close":"')[1].split('"')[0]
                )
                hours = (
                    hours
                    + "; Fri: "
                    + days[6].split('"open":"')[1].split('"')[0]
                    + "-"
                    + days[6].split('"close":"')[1].split('"')[0]
                )
                hours = (
                    hours
                    + "; Sat: "
                    + days[7].split('"open":"')[1].split('"')[0]
                    + "-"
                    + days[7].split('"close":"')[1].split('"')[0]
                )
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
