import json
import unicodedata
from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "safestore_com_be"
log = sglog.SgLogSetup().get_logger(logger_name=website)

DOMAIN = "https://www.safestore.com/be"
MISSING = SgRecord.MISSING


api_url = "https://www.safestore.com/be/search.ashx?action=search-in-area"

payload = "northeast%5Blatitude%5D=54.62144551458296&northeast%5Blongitude%5D=7.9528027343749885&southwest%5Blatitude%5D=46.42088772522721&southwest%5Blongitude%5D=1.2071972656249885&latitude=50.7&longitude=4.58&iscitypage=true&culture=fr-BE"
headers = {
    "Connection": "keep-alive",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="99", "Google Chrome";v="99"',
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "X-Requested-With": "XMLHttpRequest",
    "sec-ch-ua-mobile": "?0",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.82 Safari/537.36",
    "sec-ch-ua-platform": '"Windows"',
    "Origin": "https://www.safestore.com",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Dest": "empty",
    "Referer": "https://www.safestore.com/be/fr/trouver-un-centre/",
    "Accept-Language": "en-US,en;q=0.9",
}


def strip_accents(text):

    text = unicodedata.normalize("NFD", text).encode("ascii", "ignore").decode("utf-8")

    return str(text)


def fetch_data():
    if True:
        loclist = session.post(api_url, headers=headers, data=payload).json()["stores"]
        for loc in loclist:
            store_number = loc["Id"]
            location_name = loc["StoreDocumentName"]
            latitude = loc["Latitude"]
            longitude = loc["Longitude"]
            phone = loc["Phone"]
            page_url = "https://www.safestore.com" + loc["DetailsUrl"]
            log.info(page_url)
            r = session.get(page_url)
            address = r.text.split('"address":')[1].split("},", 1)[0] + "}"
            address = json.loads(address)
            street_address = strip_accents(address["streetAddress"])
            city = strip_accents(address["addressLocality"])
            state = MISSING
            zip_postal = address["postalCode"]
            country_code = "NL"
            soup = BeautifulSoup(r.text, "html.parser")
            hours_of_operation = (
                soup.find("div", {"class": "store-info__time opening-time"})
                .get_text(separator="|", strip=True)
                .replace("|", " ")
                .replace("Gesloten", "Zo: Gesloten")
            )
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
