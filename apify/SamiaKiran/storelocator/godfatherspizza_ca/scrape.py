from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter

session = SgRequests()
website = "godfatherspizza_ca"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}


def fetch_data():
    if True:
        url = "http://godfatherspizza.ca/godfathers-locations.htm"
        r = session.get(url, headers=headers)
        loclist = BeautifulSoup(r.text, "html.parser")
        loclist = loclist.find("table", {"id": "stores"}).findAll("tr")
        for loc in loclist:
            temp = loc.findAll("td")
            location_name = temp[0].text
            if "closed" in temp[1].text:
                continue
            log.info(location_name)
            try:
                coords = temp[1].find("a")["href"].split("@")[1].split(",", 2)
                latitude = coords[0]
                longitude = coords[1]

            except:
                latitude = "<MISSING>"
                longitude = "<MISSING>"
            street_address = temp[1].text
            phone = temp[2].text
            yield SgRecord(
                locator_domain="http://godfatherspizza.ca/",
                page_url="http://godfatherspizza.ca/godfathers-locations.htm",
                location_name=location_name.strip(),
                street_address=street_address.strip(),
                city=location_name,
                state="<MISSING>",
                zip_postal="<MISSING>",
                country_code="CA",
                store_number="<MISSING>",
                phone=phone,
                location_type="<MISSING>",
                latitude=latitude.strip(),
                longitude=longitude.strip(),
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
