from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sglogging import SgLogSetup
from sgrequests import SgRequests

logger = SgLogSetup().get_logger("questdiagonstics.com")


def fetch_data():
    session = SgRequests()
    response = session.get(
        "https://auchan.ua/graphql/?query=query%20getWarehouses%20{%20getAuchanWarehouses%20{%20warehouses%20{%20code%20city%20city_ru%20hours%20address%20title%20position%20{%20latitude%20longitude%20__typename%20}%20__typename%20}%20__typename%20}%20}%20&operationName=getWarehouses&variables={}"
    )
    result = response.json()
    locations = result["data"]["getAuchanWarehouses"]["warehouses"]

    for location in locations:
        locator_domain = "auchan.ua"
        page_url = "https://auchan.ua/map"
        location_name = location["title"]
        street_address = location["address"]
        city = location["city_ru"]
        state = location["code"]

        geo = location["position"]
        latitude = geo["latitude"]
        longitude = geo["longitude"]
        phone = "0 800 300 551"

        yield SgRecord(
            locator_domain=locator_domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            country_code="ua",
            latitude=latitude,
            longitude=longitude,
            phone=phone,
        )


if __name__ == "__main__":
    data = fetch_data()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.GeoSpatialId)) as writer:
        for row in data:
            writer.write_row(row)
