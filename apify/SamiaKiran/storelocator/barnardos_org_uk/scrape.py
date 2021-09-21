from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import SgRecordID
from sgpostal.sgpostal import parse_address_intl
from sgscrape.sgrecord_deduper import SgRecordDeduper


session = SgRequests()
website = "barnardos_org_uk"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "https://www.barnardos.org.uk/"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        url = "https://www.barnardos.org.uk/shops/our-shops"
        r = session.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        page_limit = (
            soup.find("a", {"title": "Go to last page"}).findAll("span")[-1].text
        )
        for link in range(int(page_limit)):
            url = "https://www.barnardos.org.uk/shops/our-shops?page=" + str(link)
            log.info(f"Fetching locations from Page No {link}")
            main_r = session.get(url, headers=headers, timeout=180)
            soup = BeautifulSoup(main_r.text, "html.parser")
            loclist = soup.find("ul", {"class": "teaser-list__teasers"}).findAll("li")
            for loc in loclist:
                location_type = loc.find("span", {"class": "teaser__type"}).text
                page_url = "https://www.barnardos.org.uk" + loc.find("a")["href"]
                log.info(page_url)
                r = session.get(page_url, headers=headers)
                soup = BeautifulSoup(r.text, "html.parser")
                temp = soup.findAll("div", {"class": "shop-entity__content"})
                latitude, longitude = (
                    temp[0].find("a")["href"].split("query=")[1].split(",")
                )
                raw_address = (
                    temp[0]
                    .get_text(separator="|", strip=True)
                    .replace("|", " ")
                    .replace("View on Google Maps", " ")
                )
                phone = temp[1].get_text(separator="|", strip=True).replace("|", " ")
                try:
                    hours_of_operation = (
                        temp[2].get_text(separator="|", strip=True).replace("|", " ")
                    )
                except:
                    hours_of_operation = MISSING
                location_name = soup.find("h1", {"class": "title"}).text
                pa = parse_address_intl(raw_address)
                street_address = pa.street_address_1
                street_address = street_address if street_address else MISSING
                city = pa.city
                city = city.strip() if city else MISSING
                state = pa.state
                state = state.strip() if state else MISSING
                zip_postal = pa.postcode
                zip_postal = zip_postal.strip() if zip_postal else MISSING
                country_code = "UK"
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
                    hours_of_operation=hours_of_operation,
                    raw_address=raw_address,
                )


def scrape():
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {SgRecord.Headers.LOCATION_NAME, SgRecord.Headers.STREET_ADDRESS}
            )
        )
    ) as writer:
        for item in fetch_data():
            writer.write_row(item)


if __name__ == "__main__":
    scrape()
