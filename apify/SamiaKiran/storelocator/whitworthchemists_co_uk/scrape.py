from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgpostal.sgpostal import parse_address_intl
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "whitworthchemists_co_uk"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36"
}

DOMAIN = "https://whitworthchemists.co.uk"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        url = "https://whitworthchemists.co.uk/api/collections/branches/entries?limit=100&fields=address_1,address_2,id,latitude,longitude,opening_times,postcode,services,telephone,title,url"
        loclist = session.get(url, headers=headers).json()["data"]
        for loc in loclist:
            page_url = DOMAIN + loc["url"]
            phone = loc["telephone"]
            log.info(page_url)
            location_name = loc["title"]
            r = session.get(page_url, headers=headers)
            soup = BeautifulSoup(r.text, "html.parser")
            raw_address = (
                soup.find("div", {"class": "branch-masthead__address"})
                .get_text(separator="|", strip=True)
                .split(",")
            )
            raw_address = " ".join(
                x.strip().replace("Find us at:|", "") for x in raw_address
            )
            pa = parse_address_intl(raw_address)

            street_address = pa.street_address_1
            street_address = street_address if street_address else MISSING

            city = pa.city
            city = city.strip() if city else MISSING

            state = MISSING
            zip_postal = raw_address.split()
            zip_postal = zip_postal[-2] + " " + zip_postal[-1]
            country_code = "UK"
            latitude = loc["latitude"]
            longitude = loc["longitude"]
            hours_of_operation = (
                loc["opening_times"].split("Christmas")[0].replace("\n", " ")
            )
            yield SgRecord(
                locator_domain=DOMAIN,
                page_url=page_url,
                location_name=location_name,
                street_address=street_address.strip(),
                city=city.strip(),
                state=state.strip(),
                zip_postal=zip_postal.strip(),
                country_code=country_code,
                store_number=MISSING,
                phone=phone.strip(),
                location_type=MISSING,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hours_of_operation,
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
