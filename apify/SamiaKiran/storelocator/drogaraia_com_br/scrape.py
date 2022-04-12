import unicodedata
from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import SgRecordID
from sgpostal.sgpostal import parse_address_intl
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "drogaraia_com_br"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "https://www.drogaraia.com.br/"
MISSING = SgRecord.MISSING


def strip_accents(text):

    text = unicodedata.normalize("NFD", text).encode("ascii", "ignore").decode("utf-8")

    return str(text)


def fetch_data():
    if True:
        url = "https://www.drogaraia.com.br/storelocator/search/result/?limit=60"
        r = session.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        page_list = int(
            soup.find("div", {"class": "pages inline"}).findAll("li")[-2].text
        )
        page_list = page_list + 1
        for page in range(1, page_list):
            log.info(f"Fetching Locations from Page {page}...")
            url = (
                "https://www.drogaraia.com.br/storelocator/search/result/?limit=60&p="
                + str(page)
            )
            r = session.get(url, headers=headers)
            soup = BeautifulSoup(r.text, "html.parser")
            loclist = soup.find("div", {"id": "our_store_list"}).findAll(
                "li", {"class": "item"}
            )
            for loc in loclist:
                location_name = strip_accents(loc.find("p", {"class": "name"}).text)
                log.info(location_name)
                raw_address = strip_accents(
                    loc.find("p", {"class": "street"})
                    .get_text(separator="|", strip=True)
                    .replace("|", " ")
                )
                hours_of_operation = strip_accents(
                    loc.find("p", {"class": "hour"})
                    .get_text(separator="|", strip=True)
                    .replace("|", " ")
                )
                phone = (
                    loc.find("p", {"class": "phone"})
                    .get_text(separator="|", strip=True)
                    .replace("|", " ")
                    .split("/")[0]
                )
                pa = parse_address_intl(raw_address)

                street_address = pa.street_address_1
                street_address = street_address if street_address else MISSING

                city = pa.city
                city = city.strip() if city else MISSING

                state = pa.state
                state = state.strip() if state else MISSING

                zip_postal = pa.postcode
                zip_postal = zip_postal.strip() if zip_postal else MISSING

                zip_postal = zip_postal.replace("CEP", "")

                if zip_postal == MISSING:
                    zip_postal = raw_address.split("CEP:")[1].split("-")[0]
                country_code = "BR"
                yield SgRecord(
                    locator_domain=DOMAIN,
                    page_url="https://www.drogaraia.com.br/nossas-lojas",
                    location_name=location_name,
                    street_address=street_address,
                    city=city,
                    state=state,
                    zip_postal=zip_postal,
                    country_code=country_code,
                    store_number=MISSING,
                    phone=phone,
                    location_type=MISSING,
                    latitude=MISSING,
                    longitude=MISSING,
                    hours_of_operation=hours_of_operation,
                    raw_address=raw_address,
                )


def scrape():
    with SgWriter(
        SgRecordDeduper(
            SgRecordID({SgRecord.Headers.LOCATION_NAME, SgRecord.Headers.RAW_ADDRESS})
        )
    ) as writer:
        for item in fetch_data():
            writer.write_row(item)


if __name__ == "__main__":
    scrape()
