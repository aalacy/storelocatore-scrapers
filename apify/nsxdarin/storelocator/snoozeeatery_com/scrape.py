from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

logger = SgLogSetup().get_logger("snoozeeatery_com")

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def fetch_data():
    url = "https://www.snoozeeatery.com/wpsl_stores-sitemap.xml"
    locs = []
    r = session.get(url, headers=headers, verify=False)
    if r.encoding is None:
        r.encoding = "utf-8"
    for line in r.iter_lines(decode_unicode=True):
        if "<loc>https://www.snoozeeatery.com/restaurant/" in line:
            locs.append(line.split("<loc>")[1].split("<")[0])
    logger.info(("Found %s Locations." % str(len(locs))))
    for loc in locs:
        name = "Snooze Eatery"
        logger.info(("Pulling Location %s..." % loc))
        website = "snoozeeatery.com"
        typ = "Restaurant"
        add = ""
        city = ""
        state = ""
        zc = ""
        hours = ""
        lat = ""
        lng = ""
        r2 = session.get(loc, headers=headers)
        lines = r2.iter_lines()
        for line2 in lines:
            line2 = str(line2.decode("utf-8"))
            if "href='https://www.snoozeeatery.com/?p=" in line2:
                store = line2.split("href='https://www.snoozeeatery.com/?p=")[1].split(
                    "'"
                )[0]
            if 'restaurant__address">' in line2:
                g = next(lines)
                g = str(g.decode("utf-8"))
                add = g.split("<")[0].strip()
                g = next(lines)
                g = str(g.decode("utf-8"))
                csz = g.strip().replace("\r", "").replace("\n", "").replace("\t", "")
                city = csz.split(",")[0]
                state = csz.split(",")[1].strip().split(" ")[0]
                zc = csz.rsplit(" ", 1)[1]
            if "Phone:</label>" in line2:
                g = next(lines)
                g = str(g.decode("utf-8"))
                phone = g.strip().replace("\t", "").replace("\r", "").replace("\n", "")
            if "&#8211;" in line2 and "PM<" in line2:
                hrs = line2.split(">")[1].split("<")[0].replace("&#8211;", "-")
                if hours == "":
                    hours = "Today: " + hrs
                else:
                    hours = hours + "; " + hrs
        country = "US"
        if "denver-international-airport" in loc:
            phone = "303-342-6612"
        if "Sun:" not in hours:
            hours = hours.replace("Today:", "Sun:")
        if "Mon:" not in hours:
            hours = hours.replace("Today:", "Mon:")
        if "Tue:" not in hours:
            hours = hours.replace("Today:", "Tue:")
        if "Wed:" not in hours:
            hours = hours.replace("Today:", "Wed:")
        if "Thu:" not in hours:
            hours = hours.replace("Today:", "Thu:")
        if "Fri:" not in hours:
            hours = hours.replace("Today:", "Fri:")
        if "Sat:" not in hours:
            hours = hours.replace("Today:", "Sat:")
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
