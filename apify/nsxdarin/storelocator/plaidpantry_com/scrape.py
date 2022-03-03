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

logger = SgLogSetup().get_logger("plaidpantry_com")


def fetch_data():
    locs = []
    url = "https://www.plaidpantry.com/store-locator/"
    r = session.get(url, headers=headers)
    website = "plaidpantry.com"
    typ = "<MISSING>"
    country = "US"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        if "location.push('https://www.plaidpantry.com/store/" in line:
            locs.append(line.split("('")[1].split("'")[0])
    for loc in locs:
        logger.info(loc)
        name = ""
        add = ""
        city = ""
        state = ""
        zc = ""
        phone = ""
        store = "<MISSING>"
        lat = ""
        lng = ""
        hours = ""
        r2 = session.get(loc, headers=headers)
        lines = r2.iter_lines()
        for line2 in lines:
            if '<h2 class="h1">' in line2:
                name = line2.split('<h2 class="h1">')[1].split("<")[0]
            if "<title>" in line2:
                store = line2.split("Plaid Pantry ")[1].split("<")[0]
            if '<p class="store-address"><strong><a' in line2:
                addinfo = (
                    line2.split('<p class="store-address"><strong><a')[1]
                    .split('">')[1]
                    .split("<")[0]
                )
                add = addinfo.split(",")[0]
                if "Portland OR" in addinfo:
                    city = "Portland"
                    state = "OR"
                else:
                    city = addinfo.split(",")[1].strip()
                    state = addinfo.split(",")[2].strip().split(" ")[0]
                zc = addinfo.rsplit(" ", 1)[1]
            if '<h6><strong><a href="tel:' in line2:
                phone = line2.split('<h6><strong><a href="tel:')[1].split('"')[0]
            if "window.storeLat = " in line2:
                lat = line2.split("window.storeLat = ")[1].split(";")[0]
            if "window.storeLong = " in line2:
                lng = line2.split("window.storeLong = ")[1].split(";")[0]
            if "day:</td>" in line2:
                day = line2.split(">")[1].split("<")[0]
                g = next(lines)
                hrs = day + " " + g.split(">")[1].split("<")[0]
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
