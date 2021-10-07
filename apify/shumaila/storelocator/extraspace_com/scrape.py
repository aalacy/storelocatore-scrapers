from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgpostal.sgpostal import parse_address_intl
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "extraspace_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}

DOMAIN = "https://www.extraspace.com/"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        url = "https://www.extraspace.com/storage/facilities/"
        r = session.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        statelist = soup.find("div", {"class": "light-gray"}).findAll("a")
        for state in statelist:
            stiteMap_url = "https://www.extraspace.com" + state["href"]
            r = session.get(stiteMap_url, headers=headers, timeout=180)
            soup = BeautifulSoup(r.text, "html.parser")
            loclist = soup.findAll("a", {"class": "electric-gray"})
            for loc in loclist:
                page_url = "https://www.extraspace.com" + loc["href"]
                log.info(page_url)
                try:
                    store_number = page_url.split("/")[-2]
                except:
                    store_number = MISSING
                r = session.get(page_url, headers=headers, timeout=15)
                soup = BeautifulSoup(r.text, "html.parser")
                try:
                    raw_address = (
                        soup.find("div", {"class": "address-info"})
                        .get_text(separator="|", strip=True)
                        .replace("|", " ")
                    )
                except:
                    continue
                address_raw = raw_address.replace(",", " ")
                pa = parse_address_intl(address_raw)

                street_address = pa.street_address_1
                street_address = street_address if street_address else MISSING

                city = pa.city
                city = city.strip() if city else MISSING

                state = pa.state
                state = state.strip() if state else MISSING

                zip_postal = pa.postcode
                zip_postal = zip_postal.strip() if zip_postal else MISSING
                location_name = soup.find("h1").text
                phone = (
                    soup.find("div", {"class": "current-customer-container"})
                    .find("a")
                    .text
                )
                hours_of_operation = (
                    soup.find("div", {"class": "office-hours"})
                    .get_text(separator="|", strip=True)
                    .replace("|", " ")
                    .replace("Office Hours", "")
                )
                try:
                    latitude = r.text.split('"latitude": "')[1].split('"')[0]
                    longitude = r.text.split('"longitude": "')[1].split('"')[0]
                except:
                    latitude = r.text.split('"latitude":')[1].split('"')[0]
                    longitude = r.text.split('"longitude":')[1].split('"')[0]
                longitude = longitude.replace('"', "").replace("},", "")
                latitude = latitude.replace('"', "").replace(",", "")
                hours_of_operation = hours_of_operation.replace("Storage", "")
                country_code = "US"
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
                    hours_of_operation=hours_of_operation.strip(),
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
