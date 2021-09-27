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
website = "llbean_co_jp"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "https://llbean.co.jp/"
MISSING = SgRecord.MISSING


def strip_accents(text):

    text = unicodedata.normalize("NFD", text).encode("ascii", "ignore").decode("utf-8")

    return str(text)


def fetch_data():
    if True:
        url = "https://www.llbean.co.jp/store/"
        r = session.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        loclist = soup.find("div", {"class": "shop_list"}).findAll("li")
        for loc in loclist:
            temp = loc.find("p", {"class": "shop_location"}).find("a")
            page_url = "https://www.llbean.co.jp" + temp["name"].replace('"', "")
            store_number = page_url.split("StoreID=")[1]
            log.info(page_url)
            location_name = temp.get_text(separator="|", strip=True).split("|")[0]
            location_name = strip_accents(location_name)
            raw_address = (
                loc.find("p", {"class": "shop_address"})
                .get_text(separator="|", strip=True)
                .replace("|", " ")
            )
            raw_address = strip_accents(raw_address)
            temp = (
                loc.find("p", {"class": "shop_tel"})
                .get_text(separator="|", strip=True)
                .split("|")
            )
            phone = temp[0].split("：")[1]
            hours_of_operation = temp[1].split("：")[1]
            pa = parse_address_intl(raw_address)
            street_address = pa.street_address_1
            street_address = street_address if street_address else MISSING
            city = pa.city
            city = city.strip() if city else MISSING
            state = pa.state
            state = state.strip() if state else MISSING
            zip_postal = pa.postcode
            zip_postal = zip_postal.strip() if zip_postal else MISSING
            country_code = pa.country
            zip_postal = country_code.strip() if country_code else MISSING
            yield SgRecord(
                locator_domain=DOMAIN,
                page_url=page_url,
                location_name=location_name,
                street_address=street_address.strip(),
                city=city.strip(),
                state=state.strip(),
                zip_postal=zip_postal.strip(),
                country_code=country_code,
                store_number=store_number,
                phone=phone.strip(),
                location_type=MISSING,
                latitude=MISSING,
                longitude=MISSING,
                hours_of_operation=hours_of_operation,
                raw_address=raw_address,
            )


def scrape():
    log.info("Started")
    count = 0
    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.PhoneNumberId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
