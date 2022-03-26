import unicodedata
from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgpostal.sgpostal import parse_address_intl
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "boulangerielouise_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "https://www.boulangerielouise.com"
MISSING = SgRecord.MISSING


def strip_accents(text):

    text = unicodedata.normalize("NFD", text).encode("ascii", "ignore").decode("utf-8")

    return str(text)


def fetch_data():
    if True:
        url = "https://www.boulangerielouise.com/trouvez-une-boulangerie/"
        r = session.get(url, headers=headers)
        loclist = (
            r.text.split("var locations = [")[1].split("];")[0].split("','https")[1:]
        )
        for loc in loclist:
            page_url = "https" + loc.split("'],")[0]
            log.info(page_url)
            r = session.get(page_url, headers=headers)
            store_number = r.text.split('"location_id":')[1].split(",")[0]
            latitude = r.text.split('"lat":"')[1].split('"')[0]
            longitude = r.text.split('"lng":"')[1].split('"')[0]
            soup = BeautifulSoup(r.text, "html.parser")
            temp = (
                soup.find("div", {"class": "section-title"})
                .get_text(separator="|", strip=True)
                .split("|")
            )
            if ".com" in temp[-1]:
                del temp[-1]
            elif "@" in temp[-1]:
                del temp[-1]
            phone = temp[-1]
            if "/" in phone:
                phone = phone.split("/")[0]
            location_name = temp[0]
            hours_of_operation = (
                soup.find("table").get_text(separator="|", strip=True).replace("|", " ")
            )
            raw_address = strip_accents(temp[1])
            pa = parse_address_intl(raw_address)

            street_address = pa.street_address_1
            street_address = street_address if street_address else MISSING

            city = pa.city
            city = city.strip() if city else MISSING

            state = pa.state
            state = state.strip() if state else MISSING

            zip_postal = pa.postcode
            zip_postal = zip_postal.strip() if zip_postal else MISSING

            country_code = "FR"
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
                raw_address=raw_address,
            )


def scrape():
    log.info("Started")
    count = 0
    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.PageUrlId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
