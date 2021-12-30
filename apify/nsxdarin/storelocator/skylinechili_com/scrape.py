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

logger = SgLogSetup().get_logger("skylinechili_com")


def fetch_data():
    locs = []
    url = "https://locations.skylinechili.com/sitemap.xml"
    r = session.get(url, headers=headers)
    for line in r.iter_lines():
        if "<loc>https://locations.skylinechili.com/" in line:
            locs.append(line.split("<loc>")[1].split("<")[0])
    website = "skylinechili.com"
    typ = "<MISSING>"
    country = "US"
    logger.info("Pulling Stores")
    for loc in locs:
        hours = ""
        phone = ""
        store = loc.split("-chili-")[1]
        r2 = session.get(loc, headers=headers)
        logger.info(loc)
        for line2 in r2.iter_lines():
            if "Skyline Chili</h2><" in line2:
                name = (
                    line2.split("Skyline Chili</h2><")[1].split('">')[1].split("<")[0]
                )
            if '"addressLocality":"' in line2:
                city = line2.split('"addressLocality":"')[1].split('"')[0]
                state = line2.split('"addressRegion":"')[1].split('"')[0]
                zc = line2.split('"postalCode":"')[1].split('"')[0]
                add = line2.split('"streetAddress":"')[1].split('"')[0]
                lat = line2.split('"latitude":')[1].split(",")[0]
                lng = line2.split('"longitude":')[1].split("}")[0]
            if '"telephone":"' in line:
                phone = line.split('"telephone":"')[1].split('"')[0].replace("+", "")
            if '{"@type":"OpeningHoursSpecification"' in line2:
                days = line2.split('{"@type":"OpeningHoursSpecification"')
                for day in days:
                    if '"dayOfWeek":"' in day:
                        try:
                            hrs = (
                                day.split('"dayOfWeek":"')[1].split('"')[0]
                                + ": "
                                + day.split('"opens":"')[1].split('"')[0]
                                + "-"
                                + day.split('"closes":"')[1].split('"')[0]
                            )
                            if hours == "":
                                hours = hrs
                            else:
                                hours = hours + "; " + hrs
                        except:
                            pass
        if phone == "":
            phone = "<MISSING>"
        if hours == "":
            hours = "<MISSING>"
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
