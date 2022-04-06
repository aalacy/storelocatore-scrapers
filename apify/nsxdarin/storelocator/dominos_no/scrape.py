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

logger = SgLogSetup().get_logger("dominos_no")


def fetch_data():
    url = "https://www.dominos.no/butikker"
    locs = []
    r = session.get(url, headers=headers)
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if '" href="/butikker/' in line:
            items = line.split('" href="/butikker/')
            for item in items:
                if "Mer info</p>" in item:
                    locs.append("https://www.dominos.no/butikker/" + item.split('"')[0])
    website = "dominos.no"
    typ = "<MISSING>"
    country = "NO"
    for loc in locs:
        r2 = session.get(loc, headers=headers)
        logger.info(loc)
        name = ""
        add = ""
        city = ""
        state = "<MISSING>"
        zc = ""
        phone = ""
        lat = ""
        lng = ""
        hours = ""
        store = "<MISSING>"
        for line2 in r2.iter_lines():
            line2 = str(line2.decode("utf-8"))
            if "<title>" in line2:
                name = line2.split("<title>")[1].split(" - ")[0]
            if '"street":"' in line2:
                add = line2.split('"street":"')[1].split('"')[0]
                city = line2.split('"city":"')[1].split('"')[0]
                zc = line2.split('"postalCode":"')[1].split('"')[0]
                lat = line2.split('"latitude":')[1].split(",")[0]
                lng = line2.split('"longitude":')[1].split(",")[0]
            if '<a href="tel:' in line2:
                phone = line2.split('<a href="tel:')[1].split('"')[0]
            if '"carryout":{"active":true,"hoursOfOperation":[' in line2:
                days = (
                    line2.split('"carryout":{"active":true,"hoursOfOperation":[')[1]
                    .split('},"')[0]
                    .split('"openingHours":"')
                )
                for day in days:
                    if "closingHours" in day:
                        hrs = (
                            day.split('"weekDay":"')[1].split('"')[0]
                            + ": "
                            + day.split('"')[0]
                            + "-"
                            + day.split('"closingHours":"')[1].split('"')[0]
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
