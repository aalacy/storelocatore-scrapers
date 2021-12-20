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

logger = SgLogSetup().get_logger("dominos_lu")


def fetch_data():
    locs = []
    website = "dominos.lu"
    typ = "<MISSING>"
    country = "LU"
    for x in range(1000, 10000, 500):
        logger.info("Pulling Postal %s..." % str(x))
        url = "https://www.dominos.lu/fr/magasins?SearchCriteria=" + str(x)
        r = session.get(url, headers=headers)
        for line in r.iter_lines():
            if '<a id="store-details-' in line:
                lurl = "https://www.dominos.lu/" + line.split('href="')[1].split('"')[0]
                if lurl not in locs:
                    locs.append(lurl)
    for loc in locs:
        logger.info(loc)
        name = ""
        add = ""
        city = ""
        state = "<MISSING>"
        zc = ""
        phone = ""
        store = loc.rsplit("-", 1)[1]
        lat = "<MISSING>"
        lng = "<MISSING>"
        hours = ""
        r2 = session.get(loc, headers=headers)
        lines = r2.iter_lines()
        for line2 in lines:
            if '<span class="store-name"><a href=' in line2:
                name = (
                    line2.split('<span class="store-name"><a href=')[1]
                    .split('">')[1]
                    .split("<")[0]
                )
            if 'href="http://maps.google.com/' in line2 and "open-map" not in line2:
                g = next(lines)
                add = g.split(",")[0].strip().replace("\t", "").replace(",", "")
                city = g.split("<br/>")[1].split(" LU")[0]
                zc = g.split("<br/>")[1].strip().rsplit(" ", 1)[1]
            if '<a href="tel:' in line2:
                phone = line2.split('<a href="tel:')[1].split('"')[0]
            if '<span class="trading-day" aria-hidden="true">' in line2:
                g = next(lines)
                day = g.strip().replace("\t", "").replace("\r", "").replace("\n", "")
            if '<span class="visually-hidden">' in line2:
                g = next(lines)
                hrs = (
                    day
                    + ": "
                    + g.strip().replace("\t", "").replace("\r", "").replace("\n", "")
                )
                if hours == "":
                    hours = hrs
                else:
                    hours = hours + "; " + hrs
            if 'name="store-lat" id="store-lat" value="' in line2:
                lat = (
                    line2.split('name="store-lat" id="store-lat" value="')[1]
                    .split('"')[0]
                    .replace(",", ".")
                )
            if 'name="store-lon" id="store-lon" value="' in line2:
                lng = (
                    line2.split('name="store-lon" id="store-lon" value="')[1]
                    .split('"')[0]
                    .replace(",", ".")
                )
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
