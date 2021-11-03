from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter

session = SgRequests()
website = "omegasports_net"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36",
}


def fetch_data():
    if True:
        url = "https://www.omegasports.com/store_locations.cfm"
        r = session.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        loclist = soup.findAll("div", {"class": "storeContainer"})
        for loc in loclist:
            store_number = loc.find("div", {"class": "mapAddress"})["id"]
            latitude, longitude = (
                loc.find("h4")["onclick"]
                .replace("changeMap(", "")
                .replace(");", "")
                .split(",")[1:]
            )
            city, state = (
                loc.find("h4")
                .text.replace("\n", "")
                .replace("\t", "")
                .strip()
                .split(",")
            )
            zip_postal = loc.find("p").text.split(" ")[-1]
            street_address = (
                loc.find("p").text.replace(zip_postal, "").strip()
                + " "
                + loc.find_all("p")[1].text
            ).strip()
            location_name = loc.find("h5").text
            log.info(location_name)
            street_address = street_address
            phone = loc.find("a").text
            yield SgRecord(
                locator_domain="https://www.omegasports.com/",
                page_url="https://www.omegasports.com/store_locations.cfm",
                location_name=location_name.strip(),
                street_address=street_address.strip(),
                city=city.strip(),
                state=state.strip(),
                zip_postal=zip_postal.strip(),
                country_code="US",
                store_number=store_number,
                phone=phone.strip(),
                location_type="<MISSING>",
                latitude=latitude,
                longitude=longitude,
                hours_of_operation="<MISSING>",
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
