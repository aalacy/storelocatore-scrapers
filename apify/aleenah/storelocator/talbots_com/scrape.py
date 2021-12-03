from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

logger = SgLogSetup().get_logger("talbots_com")


def write_output(data):
    with SgWriter(
        deduper=SgRecordDeduper(RecommendedRecordIds.StoreNumberId)
    ) as writer:
        for row in data:
            writer.write_row(row)


session = SgRequests()


def fetch_data():
    # Your scraper here
    res = session.get(
        "https://www.talbots.com/on/demandware.store/Sites-talbotsus-Site/default/Stores-GetNearestStores?latitude=37.090240&longitude=-95.712891&maxdistance=5000"
    )
    jso = res.json()["stores"]

    for id, js in jso.items():
        name = js["name"]
        if "OUTLET" in name:
            name = "Talbots Outlet"
        elif "CLEARANCE" in name:
            name = "Talbots Clearance Store"
        else:
            name = "Talbots"

        yield SgRecord(
            locator_domain="https://www.talbots.com",
            page_url="https://www.talbots.com/on/demandware.store/Sites-talbotsus-Site/default/Stores-GetNearestStores?latitude=37.090240&longitude=-95.712891&maxdistance=5000",
            location_name=name,
            street_address=js["address2"],
            city=js["city"],
            state=js["stateCode"],
            zip_postal=js["postalCode"],
            country_code=js["countryCode"],
            store_number=id,
            phone=js["phone"],
            location_type="<MISSING>",
            latitude=js["longitude"],
            longitude="<MISSING>",
            hours_of_operation=js["storeHours"].replace("<br>", ", ").strip(),
        )


def scrape():
    write_output(fetch_data())


scrape()
