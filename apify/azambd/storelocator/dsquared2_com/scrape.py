from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgwriter import SgWriter
from sglogging import sglog
from sgpostal.sgpostal import parse_address_intl

session = SgRequests()
MISSING = SgRecord.MISSING

domain = "dsquared2.com"

logging = sglog.SgLogSetup().get_logger(logger_name=domain)

_header = {
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
}

api_url = "https://www.dsquared2.com/on/demandware.store/Sites-dsquared2-us-Site/en_US/Stores-FindStores?showMap=false&radius=50000&lat=28.80663839999999&long=-96.99609249999999"


def get_address(raw_address):
    try:
        if raw_address is not None and raw_address != MISSING:
            data = parse_address_intl(raw_address)
            street_address = data.street_address_1
            if data.street_address_2 is not None:
                street_address = street_address + " " + data.street_address_2
            city = data.city
            state = data.state
            zip_postal = data.postcode

            if street_address is None or len(street_address) == 0:
                street_address = MISSING
            if city is None or len(city) == 0:
                city = MISSING
            if state is None or len(state) == 0:
                state = MISSING
            if zip_postal is None or len(zip_postal) == 0:
                zip_postal = MISSING
            return street_address, city, state, zip_postal
    except Exception as e:
        logging.info(f"No Address {e}")
        pass
    return MISSING, MISSING, MISSING, MISSING


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
            hoo = hoo.replace("&amp;", "&")

        street_address = " ".join(poi["address1"].split())
        city1 = poi["city"]
        zip_postal = poi["postalCode"]
        country_code = poi["countryCode"]
        raw_address = f"{street_address} {city1} {zip_postal}"
        street_address, city, state, zip_postal = get_address(raw_address)

        yield SgRecord(
            locator_domain=domain,
            page_url=f"https://www.dsquared2.com/us/storelocator/details?sid={poi['ID']}",
            location_name=poi["name"],
            street_address=" ".join(poi["address1"].split()),
            city=city1,
            state=state,
            zip_postal=zip_postal,
            country_code=country_code,
            store_number=poi["ID"],
            phone=phone_number,
            location_type=poi["shopType"],
            latitude=poi["latitude"],
            longitude=poi["longitude"],
            hours_of_operation=hoo,
            raw_address=raw_address,
        )


def scrape():
    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.StoreNumberId)
    ) as writer:
        for rec in fetch_data():
            writer.write_row(rec)


if __name__ == "__main__":
    scrape()
