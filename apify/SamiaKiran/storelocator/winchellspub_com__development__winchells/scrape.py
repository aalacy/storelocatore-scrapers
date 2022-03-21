from sglogging import SgLogSetup
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgpostal import parse_address_intl

website = "winchellspub_com__development__winchells"
logger = SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}
DOMAIN = "http://winchellspub.com"
MISSING = "<MISSING>"


def fetch_data():
    if True:
        url = "https://winchellspub.com/development/winchells/"
        r = session.get(url, headers=headers, verify=False)
        soup = BeautifulSoup(r.text, "html.parser")
        loclist = soup.find(
            "div", {"class": "w3-dropdown-content w3-card-4 w3-bar-block"}
        ).findAll("a")
        for loc in loclist:
            page_url = loc["href"]
            logger.info(page_url)
            location_name = loc.text
            location_name = " ".join(location_name.split())
            location_name = location_name if location_name else MISSING

            r = session.get(page_url, headers=headers)
            soup = BeautifulSoup(r.text, "html.parser")

            address_raw = soup.find("div", {"class": "w3-col m5"})

            # Find the raw address
            address_raw = address_raw.find("h3").text
            address_raw = " ".join(address_raw.split())

            # Parse the address
            pa = parse_address_intl(address_raw)

            street_address = pa.street_address_1
            street_address = street_address if street_address else MISSING

            city = pa.city
            city = city.strip() if city else MISSING

            state = pa.state
            state = state.strip() if state else MISSING

            zip_postal = pa.postcode
            zip_postal = zip_postal.strip() if zip_postal else MISSING

            country_code = "US"
            store_number = MISSING

            # Phone
            phone_data = soup.find("div", {"class": "w3-col m5"})
            ph = phone_data.find("p").getText()
            ph = "".join(ph.split()).strip()
            ph = ph.encode("ascii", "ignore")
            ph = ph.decode("utf-8")
            phone = ph if ph else MISSING

            # location
            location_type = MISSING
            latitude, longitude = r.text.split("LatLng(")[1].split(")")[0].split(",")
            hours_of_operation = MISSING
            raw_address = address_raw if address_raw else MISSING
            logger.info(f"Raw Address: {raw_address}")
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
                location_type=location_type,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hours_of_operation,
                raw_address=raw_address,
            )


def scrape():
    logger.info("Scraper Started")
    count = 0
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    logger.info(f"No of records being processed: {count}")
    logger.info("Finished")


if __name__ == "__main__":
    scrape()
