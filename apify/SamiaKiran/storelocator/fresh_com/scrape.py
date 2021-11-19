from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgpostal.sgpostal import parse_address_intl
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "fresh_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)


headers = {
    "authority": "www.fresh.com",
    "cache-control": "max-age=0",
    "sec-ch-ua": '"Google Chrome";v="95", "Chromium";v="95", ";Not A Brand";v="99"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "sec-fetch-site": "cross-site",
    "sec-fetch-mode": "navigate",
    "sec-fetch-user": "?1",
    "sec-fetch-dest": "document",
    "accept-language": "en-US,en;q=0.9",
}

DOMAIN = "https://fresh.com/"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        url = "https://www.fresh.com/on/demandware.store/Sites-fresh-Site/en_US/Stores-FindStores?format=ajax"
        r = session.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        loclist = soup.find("div", {"id": "boutique"}).findAll(
            "div", {"class": "card store_card"}
        )
        for loc in loclist:
            address = loc.find("div", {"class": "show-in-map"})
            store_number = address["data-store-id"]
            location_name = address["data-store-name"]
            log.info(location_name)
            coords = address["data-store-coord"].split(",")
            latitude = coords[0]
            longitude = coords[1]
            try:
                phone = (
                    loc.find("div", {"class": "store-card-bottom d-flex"})
                    .find_next("div", {"class": "store_phone"})
                    .find_next("span")
                    .text
                )
            except:
                phone = MISSING
            try:
                hours_of_operation = (
                    loc.find("div", {"class": "store-card-bottom d-flex"})
                    .find_next("div", {"class": "store_hours"})
                    .find_next("span")
                    .text
                )
            except:
                hours_of_operation = MISSING
            raw_address = address.text
            pa = parse_address_intl(raw_address)

            street_address = pa.street_address_1
            street_address = street_address if street_address else MISSING

            city = pa.city
            city = city.strip() if city else MISSING

            state = pa.state
            state = state.strip() if state else MISSING

            zip_postal = pa.postcode
            zip_postal = zip_postal.strip() if zip_postal else MISSING
            if "US" in store_number:
                country_code = "US"
            else:
                country_code = MISSING
            yield SgRecord(
                locator_domain=DOMAIN,
                page_url="https://www.fresh.com/us/stores",
                location_name=location_name,
                street_address=street_address.strip(),
                city=city.strip(),
                state=state.strip(),
                zip_postal=zip_postal.strip(),
                country_code=country_code,
                store_number=store_number,
                phone=phone.strip(),
                location_type=MISSING,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hours_of_operation.strip(),
                raw_address=raw_address,
            )


def scrape():
    log.info("Started")
    count = 0
    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.GeoSpatialId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
