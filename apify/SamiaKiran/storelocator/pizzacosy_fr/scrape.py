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
website = "pizzacosy_fr"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36"
}

DOMAIN = "https://pizzacosy.fr"
MISSING = SgRecord.MISSING


def strip_accents(text):

    text = unicodedata.normalize("NFD", text).encode("ascii", "ignore").decode("utf-8")

    return str(text)


def fetch_data():
    if True:
        r = session.get(DOMAIN, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        loclist = soup.find("ul", {"class": "dropdown-menu listeRestauHeader"}).findAll(
            "li"
        )
        for loc in loclist:
            temp = loc.find("a")
            location_name = strip_accents(temp.text)
            if "pizzacosy" in temp["href"]:
                page_url = temp["href"]
            else:
                page_url = DOMAIN + temp["href"]
            log.info(page_url)
            r = session.get(page_url, headers=headers)
            soup = BeautifulSoup(r.text, "html.parser")
            phone = soup.select_one("a[href*=tel]").text
            temp = soup.findAll("div", {"class": "blockCoordonneesRestau"})
            address = (
                temp[0]
                .get_text(separator="|", strip=True)
                .replace("|", " ")
                .split("T.")
            )
            raw_address = strip_accents(address[0])
            pa = parse_address_intl(raw_address)

            street_address = pa.street_address_1
            street_address = street_address if street_address else MISSING

            city = pa.city
            city = city.strip() if city else MISSING

            state = pa.state
            state = state.strip() if state else MISSING

            zip_postal = pa.postcode
            zip_postal = zip_postal.strip() if zip_postal else MISSING

            temp_zip = raw_address.split()
            if zip_postal == MISSING:
                zip_postal = temp_zip[-3] + " " + temp_zip[-2]
            elif len(zip_postal) < 5:
                zip_postal = temp_zip[-3] + " " + temp_zip[-2]
            if "Le" in zip_postal:
                zip_postal = temp_zip[-4] + " " + temp_zip[-3]

            hours_of_operation = (
                temp[1]
                .get_text(separator="|", strip=True)
                .replace("|", " ")
                .replace("Schedule", "")
            )
            country_code = "FR"
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
                latitude=MISSING,
                longitude=MISSING,
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
