import re
from sglogging import sglog
from sgrequests import SgRequests
from bs4 import BeautifulSoup
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord

website = "midorisushi.net"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}


def parse_geo(url):
    a = re.findall(r"\&sll=(-?[\d\.]*,(--?[\d\.]*))", url)[0]
    lat = a[0].split(",")[0]
    lon = a[0].split(",")[1]
    return lat, lon


def fetch_data():
    if True:
        url = "http://midorisushi.net/locations_text.html?20210216"
        link = "http://midorisushi.net/locations.html?20210216"
        hours = session.get(link, headers=headers)
        hours = BeautifulSoup(hours.text, "html.parser")
        hours = hours.find("ul").findAll("li")
        hours_of_operation = " ".join(hour.text for hour in hours)
        r = session.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        loclist = soup.find("table").findAll("td")[1]
        coords = loclist.findAll("a")
        loclist = loclist.text.strip().split("click here for map")

        for (loc, coord) in zip(loclist, coords):
            coord = coord["href"]
            try:
                latitude, longitude = parse_geo(coord)
            except:
                latitude, longitude = "<MISSING>", "<MISSING>"
            loc = loc.splitlines()
            if not loc[0]:
                location_name = loc[1].strip()
                street_address = loc[2].strip()
                phone = loc[5].replace("T:", "").strip()
                address = loc[3].strip().split(",")
                city = address[0]
                address = address[1].split()
                state = address[0]
                zip_postal = address[1]
            else:
                location_name = loc[0].strip()
                street_address = loc[1].strip()
                phone = loc[4].replace("T:", "").strip()
                address = loc[2].strip().split(",")
                city = address[0]
                address = address[1].split()
                state = address[0]
                zip_postal = address[1]
            hours_of_operation

            yield SgRecord(
                locator_domain="http://midorisushi.net/",
                page_url="http://midorisushi.net/locations.html?20210216",
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zip_postal,
                country_code="US",
                store_number="<MISSING>",
                phone=phone,
                location_type="<MISSING>",
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hours_of_operation,
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
