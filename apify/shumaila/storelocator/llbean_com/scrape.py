from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "llbean_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "https://llbean.com/"
MISSING = "<MISSING>"


def fetch_data():
    pattern = re.compile(r"\s\s+")
    url = "https://www.llbean.com/llb/shop/1000001703?pla1=1"
    r = session.get(url, headers=headers, verify=False)
    soup = BeautifulSoup(r.text, "html.parser")
    loclist = soup.find("div", {"id": "storeLocatorZone"}).findAll("a")
    for loc in loclist[1:]:
        page_url = "https://www.llbean.com" + loc["href"]
        log.info(page_url)
        r = session.get(page_url, headers=headers, verify=False)
        soup = BeautifulSoup(r.text, "html.parser")
        address = soup.find("address")
        location_name = soup.find("strong", {"class": "title"}).text
        store_number = page_url.rsplit("/")[-1]
        street_address = address.find("span", {"class": "street-address"}).text
        city = address.find("em", {"class": "locality"}).text
        state = address.find("abbr", {"class": "region"}).text
        zip_postal = address.find("em", {"class": "postal-code"}).text
        phone = address.find("strong", {"class": "tel"}).text
        country_code = "US"
        hours_of_operation = (
            soup.find("ul", {"class": "schedule hoursActive"})
            .get_text(separator="|", strip=True)
            .replace("|", " ")
        )
        latitude = r.text.split("var latitude =  ")[1].split(";")[0]
        longitude = r.text.split("var longitude =  ")[1].split(";")[0]
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
