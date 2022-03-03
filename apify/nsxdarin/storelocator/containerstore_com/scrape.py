from sgrequests import SgRequests
from sglogging import SgLogSetup
import time
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("containerstore_com")


def fetch_data():
    locs = []
    session = SgRequests()
    url = "https://www.containerstore.com/locations/index.htm"
    r = session.get(url, headers=headers)
    website = "containerstore.com"
    typ = "<MISSING>"
    country = "US"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if '<a href="/locations/showStore.htm?store=' in line:
            locs.append(
                "https://www.containerstore.com" + line.split('href="')[1].split('"')[0]
            )
    logger.info(len(locs))
    for loc in locs:
        session = SgRequests()
        logger.info(loc)
        name = ""
        add = ""
        city = ""
        state = ""
        zc = ""
        store = loc.split("store=")[1]
        phone = ""
        lat = ""
        lng = ""
        hours = ""
        r2 = session.get(loc, headers=headers)
        for line2 in r2.iter_lines():
            line2 = str(line2.decode("utf-8"))
            if '"name": "' in line2 and name == "":
                name = line2.split('"name": "')[1].split('"')[0]
            if '"streetAddress": "' in line2:
                add = line2.split('"streetAddress": "')[1].split('"')[0]
            if '"addressRegion": "' in line2:
                state = line2.split('"addressRegion": "')[1].split('"')[0]
            if '"addressLocality": "' in line2:
                city = line2.split('"addressLocality": "')[1].split('"')[0]
            if '"postalCode": "' in line2:
                zc = line2.split('"postalCode": "')[1].split('"')[0]
            if '"latitude": ' in line2:
                lat = line2.split('"latitude": ')[1].split(",")[0]
            if '"longitude": ' in line2:
                lng = "-" + (
                    line2.split('"longitude": ')[1]
                    .strip()
                    .replace("\t", "")
                    .replace("\r", "")
                    .replace("\n", "")
                )
            if '"phone-color" href="tel:' in line2 and phone == "":
                phone = line2.split('"phone-color" href="tel:')[1].split('"')[0]
            if '"dayOfWeek": "http://schema.org/' in line2:
                day = line2.split('"dayOfWeek": "http://schema.org/')[1].split('"')[0]
            if '"opens": "' in line2:
                day = day + ": " + line2.split('"opens": "')[1].split(':00"')[0]
            if '"closes": "' in line2:
                day = day + "-" + line2.split('"closes": "')[1].split(':00"')[0]
                if hours == "":
                    hours = day
                else:
                    hours = hours + "; " + day
        if phone == "":
            phone = "<MISSING>"
        if "store=NOR" in loc:
            name = "Northbrook"
            add = "101 Skokie Blvd."
            city = "Northbrook"
            state = "IL"
            zc = "60062"
            phone = "(847) 559-8222"
            hours = "Mon-Sat: 10:00 AM - 8:00 PM; Sun: 11:00 AM - 7:00 PM"
            lat = "42.152"
            lng = "87.8007"
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
        time.sleep(15)


def scrape():
    results = fetch_data()
    with SgWriter(deduper=SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        for rec in results:
            writer.write_row(rec)


scrape()
