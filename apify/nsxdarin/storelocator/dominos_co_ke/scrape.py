from sglogging import SgLogSetup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
import json

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("dominos_co_ke")


def fetch_data():
    country = "KE"
    website = "dominos.co.ke"
    typ = "<MISSING>"
    url = "https://apiv4.ordering.co/v400/en/dominoskenya/business?type=2&location=-1.349598738214966,36.8983472837448&params=name,slug,logo,header,location,description,food,alcohol,groceries,laundry,zones,delivery_price,minimum,schedule,featured,reviews,about,delivery_time,pickup_time,offers&limit=50"
    r = session.get(url, headers=headers)
    for item in json.loads(r.content)["result"]:
        name = item["name"]
        store = item["id"]
        loc = "https://dominos.co.ke/" + item["slug"]
        lat = item["location"]["lat"]
        lng = item["location"]["lng"]
        add = "<MISSING>"
        city = "Nairobi"
        state = "<MISSING>"
        if "CITY MALL" in name:
            city = "Mombasa"
        hours = "Sun-Sat: 9:00AM - 9:00PM"
        zc = "<MISSING>"
        phone = "<INACCESSIBLE>"
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
