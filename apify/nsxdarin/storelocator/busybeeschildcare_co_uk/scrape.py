from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("busybeeschildcare_co_uk")


def fetch_data():
    locs = []
    url = "https://www.busybeeschildcare.co.uk/sitemap.xml"
    r = session.get(url, headers=headers)
    website = "busybeeschildcare.co.uk"
    typ = "<MISSING>"
    country = "GB"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        if "<loc>https://www.busybeeschildcare.co.uk/nursery/" in line:
            items = line.split("<loc>https://www.busybeeschildcare.co.uk/nursery/")
            for item in items:
                if 'xmlns="http://www.sitemaps' not in item:
                    lurl = (
                        "https://www.busybeeschildcare.co.uk/nursery/"
                        + item.split("<")[0]
                    )
                    locs.append(lurl)
    for loc in locs:
        r = session.get(loc, headers=headers)
        logger.info(loc)
        hours = ""
        store = "<MISSING>"
        for line in r.iter_lines():
            if '<h2 class="nurseryName pb-1">' in line:
                name = line.split('<h2 class="nurseryName pb-1">')[1].split("<")[0]
                days = ""
            if '"latitude":' in line:
                lat = line.split('"latitude":')[1].split(",")[0]
            if '"longitude":' in line:
                lng = line.split('"longitude":')[1].split("}")[0].strip()
            if '"streetAddress":"' in line:
                add = line.split('"streetAddress":"')[1].split('"')[0]
                state = "<MISSING>"
            if '"addressLocality":"' in line:
                city = line.split('"addressLocality":"')[1].split('"')[0]
            if '"postalCode":"' in line:
                zc = line.split('"postalCode":"')[1].split('"')[0]
            if 'day"' in line and "today" not in line:
                if days == "":
                    days = line.split('"')[1]
                else:
                    days = days + "," + line.split('"')[1]
            if '"opens": "' in line:
                hrs = line.split('"opens": "')[1].split('"')[0]
            if '"closes": "' in line:
                hrs = hrs + "-" + line.split('"closes": "')[1].split('"')[0]
                hrs = days + ": " + hrs
                days = ""
                if hours == "":
                    hours = hrs
                else:
                    hours = hours + "; " + hrs
            if '"telephone":"' in line:
                phone = line.split('"telephone":"')[1].split('"')[0]
        if "0" not in hours:
            hours = "<MISSING>"
        if "ReviewBody,Monday" in hours:
            hours = hours.split("ReviewBody,")[1].strip()
        if "Friday: -" in hours:
            hours = "<MISSING>"
        if ",Monday" in hours:
            hours = "Monday" + hours.split(",Monday")[1]
        yield SgRecord(
            locator_domain=website,
            page_url=loc,
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
    with SgWriter(deduper=SgRecordDeduper(RecommendedRecordIds.GeoSpatialId)) as writer:
        for rec in results:
            writer.write_row(rec)


scrape()
