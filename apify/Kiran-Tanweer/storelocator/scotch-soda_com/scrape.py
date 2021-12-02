from sglogging import sglog
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from bs4 import BeautifulSoup
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries


session = SgRequests()
website = "scotch-soda_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "https://www.scotch-soda.com/"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        search = DynamicGeoSearch(
            country_codes=[
                SearchableCountries.USA,
                SearchableCountries.CANADA,
                SearchableCountries.BRITAIN,
            ]
        )
        for lat, lng in search:
            search_url = (
                "https://www.scotch-soda.com/on/demandware.store/Sites-ScotchSoda-EU-Site/en_GG/Stores-JSON?officialstores=&outletstores=&lat="
                + str(lat)
                + "&lng="
                + str(lng)
                + "&distance=8.910617196322027"
            )
            stores_req = session.get(search_url, headers=headers).json()
            if stores_req != []:
                for store in stores_req["stores"]:
                    title = store["name"]
                    street = store["address"]
                    city = store["city"]
                    pcode = store["postalCode"]
                    phone = store["phone"]
                    hours = store["hours"]
                    lat = store["lat"]
                    lng = store["lng"]
                    link = store["pageUrl"]
                    state = MISSING
                    hours = hours.replace("<br/>", " ")
                    hours = BeautifulSoup(hours, "html.parser")
                    hours = hours.text

                    yield SgRecord(
                        locator_domain=DOMAIN,
                        page_url=link,
                        location_name=title,
                        street_address=street.strip(),
                        city=city.strip(),
                        state=state.strip(),
                        zip_postal=pcode,
                        country_code="US",
                        store_number=MISSING,
                        phone=phone,
                        location_type=MISSING,
                        latitude=lat,
                        longitude=lng,
                        hours_of_operation=hours.strip(),
                    )


def scrape():
    log.info("Started")
    count = 0
    deduper = SgRecordDeduper(
        SgRecordID({SgRecord.Headers.LATITUDE, SgRecord.Headers.LONGITUDE})
    )
    with SgWriter(deduper) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1
    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
