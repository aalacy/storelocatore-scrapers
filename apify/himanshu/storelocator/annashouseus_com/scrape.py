from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import ssl

try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification


session = SgRequests()
website = "annashouseus_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}

DOMAIN = "https://annashouseus.com/"
MISSING = "<MISSING>"


def fetch_data():
    if True:
        url = "https://annashouseus.com/locations/"
        r = session.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        loclist = soup.find("ul", {"id": "vc-locationsList"}).findAll("li")
        coord_list = soup.findAll("div", {"class": "vc-location-content"})
        for loc in loclist:
            loc = loc.get_text(separator="|", strip=True).split("|")
            location_name = loc[0]
            log.info(location_name)
            address = (
                loc[-1]
                .encode("ascii", "replace")
                .decode("utf-8")
                .replace("\n", " ")
                .replace("?", "")
            )
            for coord in coord_list:
                if location_name in coord.find("h2").text:
                    phone = coord.select_one("a[href*=tel]").text
                    coords = coord.findAll("iframe")[-1]["src"]
                    r = session.get(coords, headers=headers)
                    coords = (
                        r.text.split("],0],")[0].rsplit("[null,null,", 1)[1].split(",")
                    )
                    latitude = coords[0]
                    longitude = coords[1]
                    break

            address = address.split(",")
            try:
                street_address = address[0]
                city = address[1]
                address = address[2].split()
                state = address[0]
                zip_postal = address[1]
            except:
                street_address = address[0]
                address = address[1].split()

                city = address[0] + " " + address[1]
                state = MISSING
                zip_postal = address[2]
            country_code = "US"
            hours_of_operation = ""
            hour_list = soup.findAll("div", {"class": "et_pb_text_inner"})[1].find_all(
                "p"
            )
            for hour in hour_list:
                if location_name in hour.text:
                    hours_of_operation = hour.text.split("open")[1].split(".")[0]
                    break
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
