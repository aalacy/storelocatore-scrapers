import usaddress
from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter

session = SgRequests()
website = "pizzacharlottenc_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}

DOMAIN = "https://pizzacharlottenc.com/"
MISSING = "<MISSING>"


def fetch_data():
    if True:
        url = "https://pizzacharlottenc.com/locations/"
        r = session.get(url, headers=headers)
        loclist = r.text.split('<div class="et_pb_blurb_container">')[1:-1]
        for loc in loclist:
            loc = BeautifulSoup(loc, "html.parser")
            location_name = loc.find("strong").text.replace("FIND", "")
            log.info(location_name)
            phone = loc.find("div", {"et_pb_blurb_description"}).text.split("FIND")[0]
            address = loc.find("a")
            coords = address["href"]
            try:
                coords = coords.split("!1d", 1)[1].split("!2d")
            except:
                coords = coords.split("!3d", 1)[1].split("!4d")
            longitude = coords[0]
            latitude = coords[1]
            if "!3m" in latitude:
                latitude = latitude.split("!3m")[0]
            if "-" in latitude:
                temp = latitude
                latitude = longitude
                longitude = temp
            address = address.get_text(separator="|", strip=True).replace("|", " ")
            address = address.replace(",", " ")
            address = usaddress.parse(address)
            i = 0
            street_address = ""
            city = ""
            state = ""
            zip_postal = ""
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
            country_code = "US"
            hours_of_operation = (
                loc.findAll("p")[-1]
                .get_text(separator="|", strip=True)
                .replace("|", " ")
            )
            if hours_of_operation == "Subscribe":
                hours_of_operation = (
                    loc.findAll("p")[2]
                    .get_text(separator="|", strip=True)
                    .replace("|", " ")
                )
            hours_of_operation = hours_of_operation.replace("HOURS:", "")

            yield SgRecord(
                locator_domain=DOMAIN,
                page_url=url,
                location_name=location_name,
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
