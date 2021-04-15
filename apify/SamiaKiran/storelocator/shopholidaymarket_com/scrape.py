from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter

session = SgRequests()
website = "shopholidaymarket_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}


def fetch_data():
    if True:
        url = "https://www.shopholidaymarket.com/locations.html"
        r = session.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        loclist = soup.find("div", {"class": "scroll center"}).findAll(
            "div", {"class": "location_wrapper"}
        )
        for loc in loclist:
            location_name = loc.find("div", {"class": "location_header"}).text
            log.info(location_name)
            store_number = loc.find("div", {"class": "location_number"}).text.replace(
                "Store ", ""
            )
            temp = (
                loc.find("div", {"class": "location_text"})
                .get_text(separator="|", strip=True)
                .split("|")
            )
            hours_of_operation = " ".join(x for x in temp[3:])
            phone = temp[2]
            street_address = temp[0]
            address = temp[1].split(",")
            city = address[0]
            address = address[1].split()
            state = address[0]
            zip_postal = address[1]
            try:
                coords = loc.findAll("a")[1]["href"].split("@")[1].split(",", 2)
                latitude = coords[0]
                longitude = coords[1]
            except:
                latitude, longitude = (
                    loc.findAll("a")[1]["href"]
                    .split("ll=")[1]
                    .split("&", 1)[0]
                    .split(",")
                )
            yield SgRecord(
                locator_domain="https://www.shopholidaymarket.com/",
                page_url="https://www.shopholidaymarket.com/locations.html",
                location_name=location_name.strip(),
                street_address=street_address.strip(),
                city=city.strip(),
                state=state.strip(),
                zip_postal=zip_postal.strip(),
                country_code="US",
                store_number=store_number,
                phone=phone,
                location_type="<MISSING>",
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
