import usaddress
from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter

session = SgRequests()
website = "officetaverngrill_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}


DOMAIN = "https://www.officetaverngrill.com/"
MISSING = "<MISSING>"


def fetch_data():
    url = "https://www.officetaverngrill.com/locations"
    r = session.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")
    loclist = soup.find("div", {"id": "sortMain"}).findAll(
        "div", {"data-spansize": "6"}
    )
    for loc in loclist:
        temp = loc.findAll("div", {"class": "row js-group-row"})
        location_name = temp[1].find("p", {"class": "fp-el"}).text
        log.info(location_name)
        hours_of_operation = (
            temp[4].get_text(separator="|", strip=True).replace("|", " ")
        )
        phone = temp[2].find("a").text
        address_url = temp[6].find("a")["data-href"]
        r = session.get(address_url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        address = (
            soup.find("div", {"class": "restaurant-info"})
            .get_text(separator="|", strip=True)
            .split("|")[1:-1]
        )
        try:
            coords = (
                temp[3]
                .find("a")["href"]
                .split("place/")[1]
                .split(",17z")[0]
                .split("/@")
            )

            latitude, longitude = coords[-1].split(",")
        except:
            latitude = MISSING
            longitude = MISSING
        address = " ".join(x for x in address)
        address = address.replace(",", " ")
        address = usaddress.parse(address)
        i = 0
        street_address = ""
        city = ""
        state = ""
        zip_postal = ""
        country_code = "US"
        while i < len(address):
            temp = address[i]
            if (
                temp[1].find("Address") != -1
                or temp[1].find("Street") != -1
                or temp[1].find("Recipient") != -1
                or temp[1].find("Occupancy") != -1
                or temp[1].find("BuildingName") != -1
                or temp[1].find("USPSBoxType") != -1
                or temp[1].find("USPSBoxID") != -1
            ):
                street_address = street_address + " " + temp[0]
            if temp[1].find("PlaceName") != -1:
                city = city + " " + temp[0]
            if temp[1].find("StateName") != -1:
                state = state + " " + temp[0]
            if temp[1].find("ZipCode") != -1:
                zip_postal = zip_postal + " " + temp[0]
            i += 1
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
