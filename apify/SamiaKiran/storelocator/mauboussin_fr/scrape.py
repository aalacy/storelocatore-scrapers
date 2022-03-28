import unicodedata
from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "mauboussin_fr"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36"
}

DOMAIN = "https://www.mauboussin.fr/"
MISSING = SgRecord.MISSING

url = "https://www.mauboussin.fr/amlocator/index/ajax/"

payload = "lat=0&lng=0&radius=0&product=0&category=0&attributes%5B0%5D%5Bname%5D=2&attributes%5B0%5D%5Bvalue%5D=1"
headers = {
    "authority": "www.mauboussin.fr",
    "accept": "*/*",
    "x-requested-with": "XMLHttpRequest",
    "user-agent": "Mozilla/5.0 (iPad; CPU OS 11_0 like Mac OS X) AppleWebKit/604.1.34 (KHTML, like Gecko) Version/11.0 Mobile/15A5341f Safari/604.1",
    "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
    "origin": "https://www.mauboussin.fr",
}


def strip_accents(text):

    text = unicodedata.normalize("NFD", text).encode("ascii", "ignore").decode("utf-8")

    return str(text)


def fetch_data():
    if True:

        r = session.post(url, headers=headers, data=payload).json()
        hour_list = r["block"]
        coord_list = r["items"]
        soup = BeautifulSoup(hour_list, "html.parser")
        loclist = soup.find("div", {"class": "amlocator-stores-wrapper"}).findAll(
            "div", {"class": "amlocator-store-desc"}
        )
        for loc, coord in zip(loclist, coord_list):
            latitude = coord["lat"]
            longitude = coord["lng"]
            store_number = coord["id"]
            temp = loc.find("a", {"class": "amlocator-link"})
            location_name = strip_accents(temp.text)
            page_url = temp["href"]
            log.info(page_url)
            phone = loc.find("span", {"class": "telephone"}).text
            raw_address = (
                strip_accents(loc.find("address").text)
                .replace(phone, "")
                .split(",")[:-1]
            )
            street_address = raw_address[0]
            address = raw_address[1].split()
            zip_postal = address[0]
            city = " ".join(address[1:])
            state = MISSING
            hours_of_operation = (
                soup.find("div", {"class": "amlocator-schedule-table"})
                .get_text(separator="|", strip=True)
                .replace("|", " ")
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
                store_number=store_number,
                phone=phone.strip(),
                location_type=MISSING,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hours_of_operation,
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
