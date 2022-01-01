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

logger = SgLogSetup().get_logger("cavenders_com")


def fetch_data():
    url = "https://www.cavenders.com/storelocator"
    r = session.get(url, headers=headers)
    website = "cavenders.com"
    typ = "<MISSING>"
    country = "US"
    loc = "<MISSING>"
    store = "<MISSING>"
    hours = "<MISSING>"
    lat = "<MISSING>"
    lng = "<MISSING>"
    logger.info("Pulling Stores")
    lines = r.iter_lines()
    for line in lines:
        if '<span class="store-name"' in line:
            add = ""
            city = ""
            state = ""
            zc = ""
            phone = ""
            hours = ""
            store = ""
            name = line.split('">')[1].split("<")[0].replace("&#39;", "'")
        if '<a href="tel:' in line:
            phone = (
                line.split('<a href="tel:')[1]
                .split('"')[0]
                .replace("&#40;", "(")
                .replace("&#41;", ")")
            )
        if "DAY</span></td>" in line and "</strong>" not in line:
            day = line.split('">')[1].split("<")[0]
            g = next(lines)
            if ">CLOSED<" not in g:
                day = day + ": " + g.rsplit(';">', 1)[1].split("<")[0]
                g = next(lines)
                day = day + "-" + g.rsplit(';">', 1)[1].split("<")[0]
                if hours == "":
                    hours = day
                else:
                    hours = hours + "; " + day
            else:
                day = day + ": CLOSED"
                if hours == "":
                    hours = day
                else:
                    hours = hours + "; " + day
        if '"address1": "' in line:
            add = line.split('"address1": "')[1].split('"')[0]
        if '"city":"' in line:
            city = line.split('"city":"')[1].split('"')[0]
        if '"stateCode":"' in line:
            state = line.split('"stateCode":"')[1].split('"')[0]
        if '"postalCode":"' in line:
            zc = line.split('"postalCode":"')[1].split('"')[0]
        if '"storeID":"' in line:
            store = line.split('"storeID":"')[1].split('"')[0]
        if '"longitude":' in line:
            lng = line.split('"longitude":"')[1].split('"')[0]
        if '"latitude":' in line:
            lat = line.split('"latitude":"')[1].split('"')[0]
        if '"detailPage":"' in line:
            loc = (
                "https://www.cavenders.com"
                + line.split('"detailPage":"')[1].split('"')[0]
            )
        if '"index":""' in line:
            if phone == "":
                phone = "<MISSING>"
            if zc == "":
                zc = "<MISSING>"
            if state == "Texas":
                state = "TX"
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
