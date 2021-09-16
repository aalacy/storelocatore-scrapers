from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "donatos_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}

DOMAIN = "https://donatos.com/"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        url = "https://www.donatos.com/locations/all"
        r = session.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        loclist = soup.find("div", {"id": "locationresults"}).findAll("li")
        for loc in loclist:
            latitude = loc["data-lat"]
            longitude = loc["data-lng"]
            page_url = loc.findAll("a")[-1]["href"]
            log.info(page_url)
            r = session.get(page_url, headers=headers)
            soup = BeautifulSoup(r.text, "html.parser")
            if "TBD , TBD, TB TBD" in loc.text:
                continue
            try:
                location_name = soup.find("h1").text
                temp = soup.find("div", {"class": "box-content"})
                street_address = temp.find("span", {"itemprop": "streetAddress"}).text
                city = temp.find("span", {"itemprop": "addressLocality"}).text
                state = temp.find("span", {"itemprop": "addressRegion"}).text
                zip_postal = temp.find("span", {"itemprop": "postalCode"}).text
                phone = temp.find("dd", {"itemprop": "phone"}).text
                hours_of_operation = (
                    temp.findAll("dd")[-1]
                    .get_text(separator="|", strip=True)
                    .replace("|", " ")
                )
            except:
                location_name = loc.find("h2").text
                temp = loc.findAll("p")
                address = temp[0].text.replace(", ,", ",").split(",")
                street_address = address[0]
                city = address[1]
                address = address[2].split()
                state = address[0]
                zip_postal = address[1]
                phone = temp[1].find("a").text
                hours_of_operation = MISSING
            if "Warning :  Invalid argument" in hours_of_operation:
                hours_of_operation = MISSING
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
                store_number=MISSING,
                phone=phone.strip(),
                location_type=MISSING,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hours_of_operation.strip(),
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
