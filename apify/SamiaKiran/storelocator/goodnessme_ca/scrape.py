from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter

session = SgRequests()
website = "goodnessme_ca"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "Accept-Encoding": "gzip, deflate",
    "Accept-Language": "en-US,en;q=0.9",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36",
}

DOMAIN = "https://goodnessme.ca/"
MISSING = "<MISSING>"


def fetch_data():
    if True:
        url = "https://goodnessme.ca/tools/store-locator"
        r = session.get(url, headers=headers)
        coord_list = r.text.split("markersCoords.push(")[1:-2]
        soup = BeautifulSoup(r.text, "html.parser")
        loclist = soup.find("div", {"id": "addresses_list"}).findAll("li")
        for loc in loclist:
            location_name = loc.find("span", {"class": "name"}).text
            log.info(location_name)
            street_address = loc.find("span", {"class": "address"}).text
            city = loc.find("span", {"class": "city"}).text
            state = loc.find("span", {"class": "prov_state"}).text
            try:
                zip_postal = loc.find("span", {"class": "postal_zip"}).text
            except:
                MISSING
            country_code = loc.find("span", {"class": "country"}).text
            phone = loc.find("span", {"class": "phone"}).text
            hours_of_operation = (
                loc.find("span", {"class": "hours"})
                .get_text(separator="|", strip=True)
                .replace("|", " ")
                .replace("Orders: 24 / 7, 365 Call Centre:", "")
                .replace("*see in-store for eatery hours", "")
                .replace("EST", "")
            )
            for coords in coord_list:
                if location_name in coords:
                    latitude = coords.split("lat: ")[1].split(",")[0]
                    longitude = coords.split("lng: ")[1].split(",")[0]
            yield SgRecord(
                locator_domain=DOMAIN,
                page_url=url,
                location_name=location_name,
                street_address=street_address.strip(),
                city=city.strip(),
                state=state.strip(),
                zip_postal=zip_postal.strip(),
                country_code=country_code.strip(),
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
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
