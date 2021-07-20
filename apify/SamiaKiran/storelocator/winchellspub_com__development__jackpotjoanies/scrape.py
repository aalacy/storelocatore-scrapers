from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sglogging import sglog
from bs4 import BeautifulSoup

website = "winchellspub_com__development__jackpotjoanies"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}


def fetch_data():
    if True:
        url = "http://winchellspub.com/development/jackpotjoanies/locations.html"
        r = session.get(url, headers=headers, verify=False)
        soup = BeautifulSoup(r.text, "html.parser")
        loclist = soup.findAll("center")[1]
        loclist = str(loclist).split("<h4>")
        for loc in loclist[1:]:
            loc = loc.replace("<br/>", "")
            temp = loc.split("\n")
            street_address = temp[1]
            address = temp[2].split(",")
            city = address[0]
            address = address[1].split()
            state = address[0]
            zip_postal = address[1]
            loc = BeautifulSoup(loc, "html.parser")
            location_name = loc.find("b").text
            log.info(location_name)
            try:
                phone = loc.find("a").text
            except:
                phone = temp[-2]
            yield SgRecord(
                locator_domain="https://winchellspub.com/development/jackpotjoanies",
                page_url="http://winchellspub.com/development/jackpotjoanies/locations.html",
                location_name=location_name.strip(),
                street_address=street_address.strip(),
                city=city.strip(),
                state=state.strip(),
                zip_postal=zip_postal.strip(),
                country_code="US",
                store_number="<MISSING>",
                phone=phone.strip(),
                location_type="<MISSING>",
                latitude="<MISSING>",
                longitude="<MISSING>",
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
