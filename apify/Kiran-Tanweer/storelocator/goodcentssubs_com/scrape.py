from sglogging import sglog
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from bs4 import BeautifulSoup
from sgzip.dynamic import DynamicZipSearch, SearchableCountries


session = SgRequests()
website = "goodcentssubs_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:97.0) Gecko/20100101 Firefox/97.0"
}

DOMAIN = "https://goodcentssubs.com/"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        search = DynamicZipSearch(
            country_codes=[
                SearchableCountries.USA,
            ]
        )
        for zip_code in search:
            url = (
                "https://locations.goodcentssubs.com/modules/multilocation/?near_location="
                + zip_code
            )
            stores_req = session.get(url, headers=headers).json()
            for stores in stores_req["objects"]:
                state = stores["state"]
                phone = stores["phonemap_e164"]["phone"]
                pcode = stores["postal_code"]
                storeid = stores["id"]
                link = stores["location_url"]
                city = stores["city"]
                title = stores["location_name"]
                lng = stores["lon"]
                lat = stores["lat"]
                street = stores["street"]
                country = stores["country"]
                req = session.get(link, headers=headers)
                soup = BeautifulSoup(req.text, "html.parser")
                hours = soup.find("div", {"class": "hours-box"}).text
                hours = hours.strip()
                hours = hours.replace("\n", " ")

                yield SgRecord(
                    locator_domain=DOMAIN,
                    page_url=link,
                    location_name=title,
                    street_address=street.strip(),
                    city=city.strip(),
                    state=state.strip(),
                    zip_postal=pcode,
                    country_code=country.strip(),
                    store_number=storeid,
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
