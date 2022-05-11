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

logger = SgLogSetup().get_logger("dominos_com_ve")


def fetch_data():
    url = "https://www.dominos.com.ve/3f4ffc51d73f13dc216b6e313d8b353510e98d16-3ce40378df7b92875f99.js"
    r = session.get(url, headers=headers)
    website = "dominos.com.ve"
    typ = "<MISSING>"
    country = "VE"
    loc = "<MISSING>"
    lat = "<MISSING>"
    lng = "<MISSING>"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        if '{"id":' in line:
            items = line.split('{"id":')
            for item in items:
                if '"nombre":"' in item:
                    store = item.split(",")[0]
                    name = item.split('"nombre":"')[1].split('"')[0]
                    add = item.split('"direccion":"')[1].split('"')[0]
                    city = item.split('"municipio":"')[1].split('"')[0]
                    state = item.split('"estado":"')[1].split('"')[0]
                    phone = item.split('"telefono":"')[1].split('"')[0]
                    hours = item.split('"horario":"')[1].split('"')[0]
                    zc = "<MISSING>"
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
    with SgWriter(
        deduper=SgRecordDeduper(RecommendedRecordIds.StoreNumberId)
    ) as writer:
        for rec in results:
            writer.write_row(rec)


scrape()
