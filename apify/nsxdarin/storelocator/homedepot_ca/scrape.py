from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

logger = SgLogSetup().get_logger("homedepot_ca")

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def fetch_data():
    locs = []
    url = "https://stores.homedepot.ca/sitemap.xml"
    r = session.get(url, headers=headers)
    for line in r.iter_lines():
        if "<loc>https://stores.homedepot.ca/" in line and ".html" in line:
            lurl = line.split("<loc>")[1].split("<")[0]
            if (
                "/bricolage-" not in lurl
                and "-hs" not in lurl
                and "fr.html" not in lurl
            ):
                locs.append(lurl)
    for loc in locs:
        logger.info("Pulling Location %s..." % loc)
        website = "homedepot.ca"
        typ = "<MISSING>"
        hours = ""
        name = ""
        add = ""
        city = ""
        state = ""
        zc = ""
        phone = ""
        country = "CA"
        lat = ""
        lng = ""
        store = loc.rsplit("-", 1)[1].split(".")[0]
        r2 = session.get(loc, headers=headers)
        for line2 in r2.iter_lines():
            if '<span class="location-name mb-5">' in line2:
                name = line2.split('<span class="location-name mb-5">')[1].split("<")[0]
            if '"streetAddress": "' in line2:
                add = line2.split('"streetAddress": "')[1].split('"')[0]
            if '"addressLocality": "' in line2:
                city = line2.split('"addressLocality": "')[1].split('"')[0]
            if '"addressRegion": "' in line2:
                state = line2.split('"addressRegion": "')[1].split('"')[0]
            if '"postalCode": "' in line2:
                zc = line2.split('"postalCode": "')[1].split('"')[0]
            if '"telephone": "' in line2:
                phone = line2.split('"telephone": "')[1].split('"')[0]
            if '"latitude": "' in line2:
                lat = line2.split('"latitude": "')[1].split('"')[0]
            if '"longitude": "' in line2:
                lng = line2.split('"longitude": "')[1].split('"')[0]
            if '"openingHours": "' in line2:
                hours = line2.split('"openingHours": "')[1].split('"')[0].strip()
        if hours == "":
            hours = "<MISSING>"
        hours = (
            hours.replace("Su", "Sun").replace(" Mo", "; Mon").replace(" Tu", "; Tue")
        )
        hours = hours.replace(" We", "; Wed")
        hours = hours.replace(" Th", "; Thu")
        hours = hours.replace(" Fr", "; Fri")
        hours = hours.replace(" Sa", "; Sat")
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
    with SgWriter(deduper=SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        for rec in results:
            writer.write_row(rec)


scrape()
