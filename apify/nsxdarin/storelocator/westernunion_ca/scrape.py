import urllib.request
import urllib.error
import urllib.parse
from sgrequests import SgRequests
import gzip
from sglogging import SgLogSetup
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

logger = SgLogSetup().get_logger("westernunion_ca")

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def get(url, headers, attempts=0):
    global session

    try:
        r = session.get(url, headers=headers)
        logger.info(f"Status {r.status_code} for URL: {url}")
        r.raise_for_status()
        return r
    except Exception as ex:
        logger.info(f"---  Resetting session after exception --> {ex} ")
        session = SgRequests()
        return get(url, headers, attempts + 1)


def fetch_data():
    locs = []
    for x in range(1, 5):
        logger.info(("Pulling Sitemap %s..." % str(x)))
        smurl = "http://locations.westernunion.com/sitemap-" + str(x) + ".xml.gz"
        with open("branches.xml.gz", "wb") as f:
            f.write(urllib.request.urlopen(smurl).read())
            f.close()
            with gzip.open("branches.xml.gz", "rt") as f:
                for line in f:
                    if "<loc>http://locations.westernunion.com/ca/" in line:
                        locs.append(line.split("<loc>")[1].split("<")[0])
        logger.info((str(len(locs)) + " Locations Found..."))
    for loc in locs:
        logger.info(loc)
        purl = loc
        website = "westernunion.ca"
        typ = "<MISSING>"
        store = "<MISSING>"
        hours = "<MISSING>"
        city = ""
        add = ""
        state = ""
        zc = ""
        if "/us/" in loc:
            country = "US"
        if "/ca/" in loc:
            country = "CA"
        name = ""
        phone = ""
        lat = ""
        lng = ""
        r = get(loc, headers=headers)
        lines = r.iter_lines()
        AFound = False
        for line in lines:
            if '<h1 class="wu_LocationCard' in line:
                name = (
                    line.split('<h1 class="wu_LocationCard')[1]
                    .split('">')[1]
                    .split("<")[0]
                )
                if "Western Union Agent Location" in name:
                    name = name.replace(name[:32], "")
                    name = name.strip()
                name = name.replace("&amp;", "&")
            if '"streetAddress":"' in line and AFound is False:
                AFound = True
                add = (
                    line.split('"streetAddress":"')[1]
                    .split('"')[0]
                    .replace("&amp;", "&")
                )
                state = line.split('"state":"')[1].split('"')[0]
                city = line.split('"city":"')[1].split('"')[0]
                zc = line.split('"postal":"')[1].split('"')[0]
                lat = line.split('"latitude":')[1].split(",")[0]
                lng = line.split('"longitude":')[1].split(",")[0]
                if phone == "":
                    phone = line.split('","phone":"')[1].split('"')[0]
                if store == "<MISSING>":
                    store = line.split('"id":"')[1].split('"')[0]
            if '"desktopHours":{"desktopHours":{' in line:
                hours = line.split('"desktopHours":{"desktopHours":{')[1].split("}}")[0]
                hours = hours.replace('","', "; ").replace('"', "")
        if hours == "":
            hours = "<MISSING>"
        if phone == "":
            phone = "<MISSING>"
        yield SgRecord(
            locator_domain=website,
            page_url=purl,
            location_name=name,
            street_address=add,
            city=city,
            state=state,
            zip_postal=zc,
            country_code=country,
            phone=phone,
            location_type=typ,
            store_number=store,
            latitude=lat,
            longitude=lng,
            hours_of_operation=hours,
        )


def scrape():
    results = fetch_data()
    with SgWriter(deduper=SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        for rec in results:
            writer.write_row(rec)


scrape()
