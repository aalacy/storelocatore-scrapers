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

logger = SgLogSetup().get_logger("pizza-restoran_dominos_co_id")


def fetch_data():
    url = "https://pizza-restoran.dominos.co.id/robots.txt"
    sms = []
    locs = []
    r = session.get(url, headers=headers)
    for line in r.iter_lines():
        if "Sitemap:" in line and "/index.xml" not in line:
            sms.append(
                line.split("Sitemap:")[1].strip().replace("\r", "").replace("\n", "")
            )
    website = "pizza-restoran.dominos.co.id"
    typ = "<MISSING>"
    country = "ID"
    for sm in sms:
        logger.info(sm)
        r2 = session.get(sm, headers=headers)
        for line2 in r2.iter_lines():
            if "/Home</loc>" in line2:
                lurl = line2.split("<loc>")[1].split("<")[0]
                if lurl not in locs:
                    locs.append(lurl)
            if ".xml</loc>" in line2:
                smurl = line2.split("<loc>")[1].split("<")[0]
                logger.info(smurl)
                r3 = session.get(smurl, headers=headers)
                for line3 in r3.iter_lines():
                    if "/Home</loc>" in line3:
                        lurl2 = line3.split("<loc>")[1].split("<")[0]
                        if lurl2 not in locs:
                            locs.append(lurl2)
                    if ".xml</loc>" in line3:
                        sm2url = line3.split("<loc>")[1].split("<")[0]
                        logger.info(sm2url)
                        r4 = session.get(sm2url, headers=headers)
                        for line4 in r4.iter_lines():
                            if "/Home</loc>" in line4:
                                lurl3 = line4.split("<loc>")[1].split("<")[0]
                                if lurl3 not in locs:
                                    logger.info(lurl3)
                                    locs.append(lurl3)
    for loc in locs:
        logger.info(loc)
        name = ""
        store = loc.rsplit("-", 1)[1].split("/")[0]
        city = ""
        add = ""
        state = ""
        zc = ""
        phone = "<MISSING>"
        lat = ""
        lng = ""
        hours = ""
        r2 = session.get(loc, headers=headers)
        for line2 in r2.iter_lines():
            if "<title>" in line2:
                name = (
                    line2.split("<title>")[1]
                    .split("|")[0]
                    .strip()
                    .replace("&#039;", "'")
                )
            if '<a href="tel:' in line2:
                phone = line2.split('<a href="tel:')[1].split('"')[0]
            if '"streetAddress":"' in line2:
                add = line2.split('"streetAddress":"')[1].split('"')[0]
                city = line2.split('"addressLocality":"')[1].split('"')[0]
                state = line2.split('"addressRegion":"')[1].split('"')[0]
                zc = line2.split('"postalCode":"')[1].split('"')[0]
                lat = line2.split('"latitude":"')[1].split('"')[0]
                lng = line2.split('"longitude":"')[1].split('"')[0]
                state = line2.split('"addressRegion":"')[1].split('"')[0]
            if '"openingHoursSpecification":[' in line2:
                days = line2.split('"dayOfWeek":"')
                for day in days:
                    if ',"opens":"' in day:
                        hrs = (
                            day.split('"')[0]
                            + ": "
                            + day.split(',"opens":"')[1].split('"')[0]
                            + "-"
                            + day.split('"closes":"')[1].split('"')[0]
                        )
                        if hours == "":
                            hours = hrs
                        else:
                            hours = hours + "; " + hrs
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
