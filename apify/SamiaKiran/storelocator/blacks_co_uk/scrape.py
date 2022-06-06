import json
import html
from sglogging import sglog
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "blacks_co_uk"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36"
}

DOMAIN = "https://www.blacks.co.uk"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        STORE_LOCATOR = "https://www.blacks.co.uk/google/store-locator"
        API_ENDPOINT_URL = f"{STORE_LOCATOR}?postcode=london&submit=Find+stores&submit=1&radius=50000&ac_store_limit=500&current_view=list&fascias%5B%5D=BL&fascias%5B%5D=ML&fascias%5B%5D=TI&fascias%5B%5D=UO&fascias%5B%5D=GO"
        with SgRequests(proxy_country="gb") as http:
            r = http.post(API_ENDPOINT_URL, headers=headers)
            log.info(f"[HTTPStatusCode: {r.status_code}]")
            txt = r.text
            txt2 = txt.split("stores = ")[-1]
            smarty_pc = "".join(txt2.split("smarty_postcode")).lstrip("[")
            checkout_store_finder100 = (
                "[" + smarty_pc.split(', = "",checkout_store_finder')[0]
            )
            loclist = json.loads(checkout_store_finder100)
            log.info(f"[TotalStores: {len(loclist)}]")
            for loc in loclist:
                page_url = DOMAIN + loc["url"]
                location_name = loc["name"]
                store_number = loc["id"]
                phone = loc["telephone"]
                try:
                    street_address = loc["address_1"] + " " + loc["address_2"]
                except:
                    street_address = loc["address_1"]
                street_address = html.unescape(street_address)
                log.info(page_url)
                city = loc["town"]
                state = MISSING
                zip_postal = loc["postcode"]
                country_code = loc["country"]
                latitude = loc["lat"]
                longitude = loc["lng"]
                hours_of_operation = str(loc["opening_hours"]).replace("<br/>", " ")
                yield SgRecord(
                    locator_domain=DOMAIN,
                    page_url=page_url,
                    location_name=location_name,
                    street_address=street_address,
                    city=city,
                    state=state,
                    zip_postal=zip_postal,
                    country_code=country_code,
                    store_number=store_number,
                    phone=phone,
                    location_type=MISSING,
                    latitude=latitude,
                    longitude=longitude,
                    hours_of_operation=hours_of_operation,
                )


def scrape():
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {SgRecord.Headers.LOCATION_NAME, SgRecord.Headers.STREET_ADDRESS}
            )
        )
    ) as writer:
        for item in fetch_data():
            writer.write_row(item)


if __name__ == "__main__":
    scrape()
