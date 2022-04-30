from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
import json

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("dominos_com_tr")


def fetch_data():
    for x in range(1, 100):
        url = "https://fe.dominos.com.tr/api/store/location?cityCode=" + str(x)
        r = session.get(url, headers=headers)
        website = "dominos.com.tr"
        typ = "<MISSING>"
        country = "TR"
        PFound = False
        trycount = 0
        while PFound is False and trycount <= 3:
            trycount = trycount + 1
            logger.info(str(x))
            try:
                for item in json.loads(r.content):
                    PFound = True
                    store = item["id"]
                    hours = item["availableFrom"] + "-" + item["availableUntil"]
                    name = item["name"]
                    add = item["address"]
                    phone = item["phone"]
                    lng = item["longitude"]
                    lat = item["lattitude"]
                    city = item["city"]["name"]
                    state = "<MISSING>"
                    zc = "<MISSING>"
                    yield SgRecord(
                        locator_domain=website,
                        page_url=url,
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
    with SgWriter(
        deduper=SgRecordDeduper(RecommendedRecordIds.StoreNumberId)
    ) as writer:
        for rec in results:
            writer.write_row(rec)


scrape()
