from sglogging import SgLogSetup
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgrequests import SgRequests
import json
import ssl


try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification

SOTRE_LOCATOR = "https://www.cashwise.com/storelocator"


logger = SgLogSetup().get_logger("cashwise_com")

headers = {
    "accept": "*/*",
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 Safari/537.36",
}

API_ENDPOINT_URL = "https://knowledgetags.yextpages.net/embed?key=-668exv0m03CTGweOOgstodtcXsQs32vTknFtZZuGe2EDA_CHG4JGlr2oiM1j6wN&account_id=2903957495944679166&entity_id=3004&entity_id=3009&entity_id=3011&entity_id=3012&entity_id=3013&entity_id=3014&entity_id=3015&entity_id=3020&entity_id=3041&entity_id=3042&entity_id=3043&entity_id=3044&entity_id=3045&entity_id=3046&entity_id=3047&entity_id=3048&entity_id=3049&entity_id=3050&entity_id=3051&entity_id=7036&entity_id=7039&entity_id=7042&entity_id=7043&entity_id=7044&entity_id=7055&entity_id=3008&locale=en"


def fetch_records():
    with SgRequests() as http:
        r = http.get(API_ENDPOINT_URL, headers=headers)
        logger.info(f"HTTPStatusCode: {r.status_code}")
        text = r.text
        raw_dict = text.split("Yext._embed(")[-1].replace(")", "")
        js = json.loads(raw_dict)
        data_entities = js["entities"]
        for idx, item in enumerate(data_entities[0:]):
            attr = item["attributes"]
            name = attr["name"]
            logger.info(f"[{idx}] [LOCATION_NAME: {name}]")
            city = attr["address.city"]
            cc = attr["address.countryCode"]
            zc = attr["address.postalCode"]
            region = attr["address.region"]
            sta = attr["address.line1"]
            try:
                lat = attr["yextDisplayCoordinate.latitude"]
                lng = attr["yextDisplayCoordinate.longitude"]
            except:

                logger.info(f" [{idx}] ITEM: {attr}\n\n")
                lat = ""
                lng = ""
            store_number = attr["id"]
            page_url = (
                SOTRE_LOCATOR.replace("storelocator", "") + "CWstore" + store_number
            )
            loctype = ", ".join(attr["meta.schemaTypes"])
            phone = attr["phone"].lstrip("(")
            fri = attr["hours-friday"]
            mon = attr["hours-monday"]
            sat = attr["hours-saturday"]
            sun = attr["hours-sunday"]
            thu = attr["hours-thursday"]
            tue = attr["hours-tuesday"]
            wed = attr["hours-wednesday"]
            hours = f"Friday: {fri}, Saturday: {sat}, Sunday: {sun}, Monday: {mon}, Thursday: {thu}, Tuesday: {tue}, Wednesday: {wed}"
            item = SgRecord(
                locator_domain="cashwise.com",
                page_url=page_url,
                location_name=name,
                street_address=sta,
                city=city,
                state=region,
                zip_postal=zc,
                country_code=cc,
                store_number=store_number,
                phone=phone,
                location_type=loctype,
                latitude=lat,
                longitude=lng,
                hours_of_operation=hours,
                raw_address="",
            )
            yield item


def scrape():
    logger.info("Scrape Started")
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.PAGE_URL,
                    SgRecord.Headers.STORE_NUMBER,
                    SgRecord.Headers.PHONE,
                }
            )
        )
    ) as writer:
        results = fetch_records()
        for rec in results:
            writer.write_row(rec)

    logger.info("Finished")


if __name__ == "__main__":
    scrape()
