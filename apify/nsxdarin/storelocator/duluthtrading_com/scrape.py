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

logger = SgLogSetup().get_logger("duluthtrading_com")


def fetch_data():
    locs = []
    url = "https://www.duluthtrading.com/our-stores/?brand=duluth"
    r = session.get(url, headers=headers)
    website = "duluthtrading.com"
    typ = "<MISSING>"
    country = "US"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        if 'store-details-link" href="/locations/?StoreID=' in line:
            locs.append(
                "https://www.duluthtrading.com" + line.split('href="')[1].split("&")[0]
            )
    for loc in locs:
        try:
            logger.info(loc)
            name = ""
            add = ""
            city = ""
            state = ""
            zc = ""
            store = loc.split("StoreID=")[1]
            phone = ""
            hours = ""
            lat = "<MISSING>"
            lng = "<MISSING>"
            r2 = session.get(loc, headers=headers)
            lines = r2.iter_lines()
            for line2 in lines:
                if (
                    'href="https://www.google.com/maps/place/' in line2
                    and lat == "<MISSING>"
                    and "/@" in line2
                ):
                    lat = line2.split("/@")[1].split(",")[0]
                    lng = line2.split("/@")[1].split(",")[1]
                if '"address":{"' in line2:
                    name = line2.split('","name":"')[1].split('"')[0]
                    add = line2.split('"streetAddress":"')[1].split('"')[0]
                    city = line2.split('"addressLocality":"')[1].split('"')[0]
                    state = line2.split('"addressRegion":"')[1].split('"')[0]
                    zc = line2.split('"postalCode":"')[1].split('"')[0]
                    try:
                        phone = line2.split('"telephone":"')[1].split('"')[0]
                    except:
                        phone = "<MISSING>"
                if "day</div>" in line2:
                    day = line2.split(">")[1].split("<")[0]
                    next(lines)
                    g = next(lines)
                    day = (
                        day
                        + ": "
                        + g.replace("\t", "")
                        .replace("\r", "")
                        .replace("\n", "")
                        .strip()
                    )
                    if hours == "":
                        hours = day
                    else:
                        hours = hours + "; " + day
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
