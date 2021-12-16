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

logger = SgLogSetup().get_logger("dominos_com_mx")


def fetch_data():
    coords = []
    url = "https://www.dominos.com.mx/api/stores"
    r = session.get(url, headers=headers)
    website = "dominos.com.mx"
    typ = "<MISSING>"
    country = "MX"
    loc = "<MISSING>"
    store = "<MISSING>"
    hours = "<MISSING>"
    logger.info("Pulling Stores")
    for item in json.loads(r.content):
        store = item["storenumber"]
        name = item["name"]
        if item["streetnumber"] is None:
            add = ""
        else:
            add = item["streetnumber"]
        add = add + " " + item["streetname"]
        if item["unitnumber"] is not None:
            add = add + " " + item["unitnumber"]
        city = item["city"]
        state = item["state"]
        zc = item["zipcode"]
        phone = item["phonenumber"]
        lat = item["latitude"]
        lng = item["longitude"]
        hours = "<MISSING>"
        latlng = lat + ":" + lng
        if latlng not in coords:
            coords.append(latlng)
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
    with SgWriter(deduper=SgRecordDeduper(RecommendedRecordIds.GeoSpatialId)) as writer:
        for rec in results:
            writer.write_row(rec)


scrape()
