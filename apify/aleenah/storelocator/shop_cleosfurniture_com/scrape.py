from bs4 import BeautifulSoup
from sglogging import sglog
from sgselenium import SgChrome
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
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
website = " shop.cleosfurniture_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "https://shop.cleosfurniture.com/"
MISSING = "<MISSING>"


session = SgRequests()


def fetch_data(sgw: SgWriter):
    with SgChrome() as driver:
        driver.get("https://shop.cleosfurniture.com/stores/store-info")
        soup = BeautifulSoup(driver.page_source, "html.parser")
        loclist = soup.findAll("div", {"class": "vc_btn3-container vc_btn3-inline"})
        for loc in loclist:
            if "cleosfurniture.com" in loc.find("a")["href"]:
                page_url = loc.find("a")["href"]
            else:
                page_url = "https://shop.cleosfurniture.com" + loc.find("a")["href"]
            log.info(page_url)
            r = session.get(page_url, headers=headers)
            soup = BeautifulSoup(r.text, "html.parser")
            temp_list = soup.find(
                "div", {"class": "wpb_text_column wpb_content_element"}
            ).findAll("p")
            longitude, latitude = (
                soup.select_one("iframe[src*=maps]")["src"]
                .split("!2d", 1)[1]
                .split("!2m", 1)[0]
                .split("!3d")
            )
            location_name = soup.find("h1").text
            phone = temp_list[0].get_text(separator="|", strip=True).split("|")[1]
            address = temp_list[1].get_text(separator="|", strip=True).split("|")
            street_address = address[1]
            address = address[2].split(",")
            city = address[0]
            address = address[1].split()
            state = address[0]
            try:
                zip_postal = address[1]
            except:
                zip_postal = MISSING
            country_code = "US"
            hours_of_operation = (
                temp_list[2]
                .get_text(separator="|", strip=True)
                .replace("|", " ")
                .replace("STORE HOURS:", "")
            )
            sgw.write_row(
                SgRecord(
                    locator_domain=DOMAIN,
                    page_url=page_url,
                    location_name=location_name,
                    street_address=street_address.strip(),
                    city=city.strip(),
                    state=state.strip(),
                    zip_postal=zip_postal.strip(),
                    country_code=country_code,
                    store_number=MISSING,
                    phone=phone,
                    location_type=MISSING,
                    latitude=latitude,
                    longitude=longitude,
                    hours_of_operation=hours_of_operation,
                )
            )


with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
    fetch_data(writer)
