from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgwriter import SgWriter
from sglogging import sglog

session = SgRequests()

domain = "dsquared2.com"

logging = sglog.SgLogSetup().get_logger(logger_name=domain)

_header = {
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
}

api_url = "https://www.dsquared2.com/on/demandware.store/Sites-dsquared2-us-Site/en_US/Stores-FindStores?showMap=false&radius=50000&lat=28.80663839999999&long=-96.99609249999999"


def fetch_data():

    response = session.get(api_url, headers=_header)
    logging.info(f"Response Status: {response}")
    data = response.json()
    for poi in data["stores"]:
        try:
            phone_number = poi["phone"]
        except:
            phone_number = "<MISSING>"

        hoo = poi.get("storeHours")
        if hoo:
            hoo = " ".join(hoo.split())

        yield SgRecord(
            locator_domain=domain,
            page_url=f"https://www.dsquared2.com/us/storelocator/details?sid={poi['ID']}",
            location_name=poi["name"],
            street_address=" ".join(poi["address1"].split()),
            city=poi["city"],
            state=poi["stateCode"],
            zip_postal=poi["postalCode"],
            country_code=poi["countryCode"],
            store_number=poi["ID"],
            phone=phone_number,
            location_type=poi["shopType"],
            latitude=poi["latitude"],
            longitude=poi["longitude"],
            hours_of_operation=hoo,
        )


def scrape():
    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.StoreNumberId)
    ) as writer:
        for rec in fetch_data():
            writer.write_row(rec)


if __name__ == "__main__":
    scrape()
