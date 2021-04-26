from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter

session = SgRequests()
website = "sunsetfoods_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}


def fetch_data():
    if True:
        url = "https://www.sunsetfoods.com/map"
        r = session.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        loclist = soup.find("section", {"id": "g-sidebar"})
        hours_of_operation = (
            soup.find("section", {"id": "g-sidebar"})
            .find("p")
            .text.replace("Store hours: ", "")
        )
        coords_list = {}
        coords = r.text.split("var marker")[1:]
        for coord in coords:
            name = coord.split(':bold;">')[1].split("</div>", 1)[0].strip()
            coords_list[name] = coord.split("L.marker([")[1].split("])", 1)[0].strip()
        loclist = loclist.findAll("div", {"class": "g-infolist-item"})
        for loc in loclist:
            location_name = (
                loc.find("div", {"class": "g-infolist-item-title"})
                .text.replace("\n", "")
                .strip()
            )
            latitude, longitude = coords_list[location_name].split(",")

            log.info(location_name)
            address = (
                loc.find("div", {"class": "g-infolist-item-desc"})
                .get_text(separator="|", strip=True)
                .split("|")
            )
            phone = address[-1].replace("\n", "")
            street_address = address[0]
            address = address[1].split(",")
            city = address[0]
            address = address[1].split()
            state = address[0]
            zip_postal = address[1]
            yield SgRecord(
                locator_domain="https://www.sunsetfoods.com/",
                page_url="https://www.sunsetfoods.com/map",
                location_name=location_name,
                street_address=street_address.strip(),
                city=city.strip(),
                state=state.strip(),
                zip_postal=zip_postal.strip(),
                country_code="US",
                store_number="<MISSING>",
                phone=phone.strip(),
                location_type="<MISSING>",
                latitude=latitude.strip(),
                longitude=longitude.strip(),
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
