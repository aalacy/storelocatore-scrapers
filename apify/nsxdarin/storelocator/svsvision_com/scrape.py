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

logger = SgLogSetup().get_logger("svsvision_com")


def fetch_data():
    locs = []
    url = "https://www.svsvision.com/svs-locations-sitemap.xml"
    r = session.get(url, headers=headers)
    website = "svsvision.com"
    typ = "<MISSING>"
    country = "US"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        if "<loc>https://www.svsvision.com/locations/" in line:
            locs.append(line.split("<loc>")[1].split("<")[0])
    for loc in locs:
        try:
            logger.info(loc)
            name = ""
            add = ""
            city = ""
            state = ""
            zc = ""
            store = ""
            phone = ""
            lat = "<MISSING>"
            lng = "<MISSING>"
            hours = ""
            r2 = session.get(loc, headers=headers)
            lines = r2.iter_lines()
            for line2 in lines:
                if "<title>" in line2:
                    name = line2.split("<title>")[1].split("<")[0].split(" - ")[0]
                    store = line2.split(" - ")[1]
                if '<div class="elementor-shortcode">' in line2 and add == "":
                    add = line2.split('<div class="elementor-shortcode">')[1].split(
                        "<"
                    )[0]
                    g = next(lines)
                    city = name
                    state = g.split(",")[0]
                    zc = g.split(",")[1].split("<")[0].strip()
                if '<a href="tel:' in line2:
                    phone = line2.split('<a href="tel:')[1].split('"')[0]
                if 'class="day">' in line2:
                    hrs = line2.split('class="day">')[1].split("<")[0]
                if 'class="hours">' in line2:
                    hrs = hrs + ": " + line2.split('class="hours">')[1].split("<")[0]
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
        except:
            pass


def scrape():
    results = fetch_data()
    with SgWriter(deduper=SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        for rec in results:
            writer.write_row(rec)


scrape()
