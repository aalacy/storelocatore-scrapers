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

logger = SgLogSetup().get_logger("dominos_by")


def fetch_data():
    url = "https://www.dominos.by/restaurants"
    r = session.get(url, headers=headers)
    website = "dominos.by"
    typ = "<MISSING>"
    country = "BY"
    loc = "<MISSING>"
    store = "<MISSING>"
    phone = "<MISSING>"
    hours = "<MISSING>"
    lat = "<MISSING>"
    lng = "<MISSING>"
    zc = "<MISSING>"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if '}},"stores":{"' in line:
            items = (
                line.split('}},"stores":{"')[1].split(',"streets":')[0].split('"id":"')
            )
            for item in items:
                if "locationCode" in item:
                    store = item.split('"')[0]
                    add = item.split('"address":"')[1].split('"')[0]
                    state = "<MISSING>"
                    hours = "Sun-Sat: " + item.split('"workTime":"')[1].split('"')[0]
                    lat = item.split('{"lat":')[1].split(",")[0]
                    lng = item.split('"lng":')[1].split("}")[0]
                    loc = "https://www.dominos.by/restaurants/" + store
                    name = add
                    city = "Minsk"
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
