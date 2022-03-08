from sgrequests import SgRequests
from sglogging import SgLogSetup
import json
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("wowbao_com")


def fetch_data():
    url = "https://api.storepoint.co/v1/15fe0bd667ae7b/locations?lat=41.8756&long=-87.6244&radius=500000"
    r = session.get(url, headers=headers)
    website = "wowbao.com"
    typ = "<MISSING>"
    country = "US"
    loc = "<MISSING>"
    hours = "<MISSING>"
    for item in json.loads(r.content)["results"]["locations"]:
        store = item["id"]
        lat = item["loc_lat"]
        lng = item["loc_long"]
        name = item["name"]
        addinfo = item["streetaddress"]
        add = "<MISSING>"
        if addinfo.count(",") == 1:
            city = addinfo.split(",")[0]
            state = addinfo.split(",")[1].strip()
        else:
            add = addinfo.split(",")[0]
            city = addinfo.split(",")[1].strip()
            state = addinfo.split(",")[2].strip()
        zc = "<MISSING>"
        phone = "<MISSING>"
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
        deduper=SgRecordDeduper(
            RecommendedRecordIds.GeoSpatialId, duplicate_streak_failure_factor=-1
        )
    ) as writer:
        for rec in results:
            writer.write_row(rec)


scrape()
