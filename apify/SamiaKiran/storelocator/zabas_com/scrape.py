from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter

session = SgRequests()
website = "zabas_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}

DOMAIN = "https://zabas.com/"
MISSING = "<MISSING>"


def fetch_data():
    if True:
        streetlist = []
        url = "https://zabas.com/restaurant-locations/"
        r = session.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        loclist = soup.findAll("div", {"class": "elementor-widget-wrap"})
        for loc in loclist:
            if "ORDER NOW" in loc.text:
                address = (
                    loc.find("p").get_text(separator="|", strip=True).split("|")[:-1]
                )
                phone = address[-1]
                street_address = address[0]
                if street_address in streetlist:
                    continue
                streetlist.append(street_address)
                location_name = loc.find("h2").text
                log.info(location_name)
                city = "Las Vegas"
                state = "NV"
                country_code = "US"
                zip_postal = "zip_postal"
                coords = loc.find("a")["href"]
                zip_postal = coords.rsplit("+")[-1].split("/")[0]
                if zip_postal.isalpha():
                    zip_postal = MISSING
                latitude, longitude = coords.split("@")[1].split(",13z")[0].split(",")
                yield SgRecord(
                    locator_domain=DOMAIN,
                    page_url=url,
                    location_name=location_name.strip(),
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
                    hours_of_operation=MISSING,
                )


def scrape():
    log.info("Started")
    count = 0
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
