from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "phycare_net"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}

DOMAIN = "https://www.urgentteam.com/brand/physicians-care/"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        url = "https://www.urgentteam.com/locations/"
        r = session.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        linklist = soup.findAll("a", {"class": "page-numbers"})[-2].text
        linklist = int(linklist) + 1
        for link in range(1, linklist):
            log.info(f"Page No {link}")
            link = "https://www.urgentteam.com/locations/page/" + str(link)
            r = session.get(link, headers=headers, allow_redirects=True)
            soup = BeautifulSoup(r.text, "html.parser")
            loclist = soup.find("ul", {"class": "m-locations__list"}).findAll(
                "li", {"class": "m-locations__item"}
            )
            for loc in loclist:
                page_url = loc.find("a")["href"]
                log.info(page_url)
                r = session.get(page_url, headers=headers)
                if "COMING-SOON" in r.text:
                    continue
                soup = BeautifulSoup(r.text, "html.parser")
                location_name = soup.find(
                    "h2", {"class": "m-location-panel__heading u-h2"}
                ).text
                location_type = soup.find(
                    "h3", {"class": "m-location-panel__subheading"}
                ).text
                hours_of_operation = (
                    soup.find("ul", {"class": "m-location-hours__list"})
                    .get_text(separator="|", strip=True)
                    .replace("|", " ")
                )
                address = (
                    soup.find("a", {"class": "m-location-panel__text"})
                    .get_text(separator="|", strip=True)
                    .split("|")
                )
                phone = soup.find("a", {"class": "m-location-panel__phone"}).text
                street_address = address[0].replace(",", "")
                address = address[1].split(",")
                city = address[0]
                address = address[1].split()
                state = address[0]
                zip_postal = address[1]
                street_address = (
                    street_address.replace(city, "")
                    .replace(state, "")
                    .replace(zip_postal, "")
                )
                latitude = r.text.split('"latitude":')[1].split(",")[0]
                longitude = r.text.split('"longitude":')[1].split("}")[0]
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
                    location_type=location_type,
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
