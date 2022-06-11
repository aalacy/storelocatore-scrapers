from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

logger = SgLogSetup().get_logger("jimmyjohns_com")

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def fetch_data():
    url = "https://locations.jimmyjohns.com/sitemap.xml"
    locs = []
    while len(locs) < 2700:
        r = session.get(url, headers=headers)
        for line in r.iter_lines():
            if ".html</loc>" in line and "/sandwiches-" in line:
                lurl = line.split("<loc>")[1].split("<")[0]
                if lurl not in locs:
                    locs.append(lurl)
    logger.info(("Found %s Locations." % str(len(locs))))
    for loc in locs:
        add = ""
        city = ""
        state = ""
        zc = ""
        country = "US"
        phone = ""
        hours = ""
        store = loc.rsplit(".", 1)[0].rsplit("-", 1)[1]
        name = "Jimmy John's #" + store
        website = "jimmyjohns.com"
        typ = "Restaurant"
        r2 = session.get(loc, headers=headers)
        for line2 in r2.iter_lines():
            if '"telephone": "' in line2:
                phone = line2.split('"telephone": "')[1].split('"')[0]
            if '"streetAddress": "' in line2:
                add = line2.split('"streetAddress": "')[1].split('"')[0]
            if '"addressLocality": "' in line2:
                city = line2.split('"addressLocality": "')[1].split('"')[0]
            if '"addressRegion": "' in line2:
                state = line2.split('"addressRegion": "')[1].split('"')[0]
            if '"postalCode": "' in line2:
                zc = line2.split('"postalCode": "')[1].split('"')[0]
            if '"latitude": "' in line2:
                lat = line2.split('"latitude": "')[1].split('"')[0]
            if '"longitude": "' in line2:
                lng = line2.split('"longitude": "')[1].split('"')[0]
            if '"openingHours": "' in line2:
                hours = line2.split('"openingHours": "')[1].split('"')[0].strip()
        if hours == "":
            hours = "<MISSING>"
        if hours.lower().count("closed") == 7:
            hours = "Temporarily Closed"
        if phone == "":
            phone = "<MISSING>"
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
    with SgWriter(
        deduper=SgRecordDeduper(RecommendedRecordIds.StoreNumberId)
    ) as writer:
        for rec in results:
            writer.write_row(rec)


scrape()
