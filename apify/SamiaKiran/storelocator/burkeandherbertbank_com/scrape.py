from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter

session = SgRequests()
website = "burkeandherbertbank_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}

DOMAIN = "https://www.burkeandherbertbank.com/"
MISSING = "<MISSING>"


def fetch_data():
    if True:
        url = "https://www.burkeandherbertbank.com/locations/list/"
        r = session.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        loclist = soup.find("div", {"class": "filtered-posts__posts"}).findAll(
            "div", {"itemtype": "http://schema.org/LocalBusiness"}
        )
        for loc in loclist:
            try:
                street_address = loc.find("span", {"itemprop": "streetAddress"}).text
                city = loc.find("span", {"itemprop": "addressLocality"}).text.replace(
                    ",", ""
                )
                state = loc.find("span", {"itemprop": "addressRegion"}).text
                zip_postal = loc.find("span", {"itemprop": "postalCode"}).text
            except:
                address = loc.find("address").text.split(",")
                street_address = address[0]
                city = address[1]
                address = address[2].split()
                state = address[0]
                zip_postal = address[1]
            location_name = street_address + " " + city + state + zip_postal
            log.info(location_name)
            phone = loc.find("p", {"class": "mb-2"}).text
            country_code = "US"
            hours_of_operation = (
                loc.find("div", {"class": "is__medium"})
                .get_text(separator="|", strip=True)
                .replace("|", " ")
                .replace("Lobby Hours", "")
                .replace("Lobby and Drive Up Hours", "")
                .replace("Lobby Hours", "")
                .replace("Lobby & Drive Up Hours", "")
            )
            if "Now Offering" in hours_of_operation:
                hours_of_operation = hours_of_operation.split("Now Offering")[0]
            location_type = "branch"
            coords = loc.find("div", {"class": "visually-hidden"}).findAll("div")
            latitude = coords[0].text
            longitude = coords[1].text
            store_number = loc["data-filtered-posts-id"]
            yield SgRecord(
                locator_domain=DOMAIN,
                page_url=url,
                location_name=location_name.strip(),
                street_address=street_address.strip(),
                city=city.strip(),
                state=state.strip(),
                zip_postal=zip_postal.strip(),
                country_code=country_code,
                store_number=store_number,
                phone=phone.strip(),
                location_type=location_type,
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
