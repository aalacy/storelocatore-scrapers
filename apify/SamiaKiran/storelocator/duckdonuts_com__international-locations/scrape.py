from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgpostal.sgpostal import parse_address_intl
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "duckdonuts_com__international-locations"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "https://www.duckdonuts.com"
MISSING = SgRecord.MISSING

headers_2 = {
    "Connection": "keep-alive",
    "Accept": "*/*",
    "X-Requested-With": "XMLHttpRequest",
    "User-Agent": "Mozilla/5.0 (iPad; CPU OS 11_0 like Mac OS X) AppleWebKit/604.1.34 (KHTML, like Gecko) Version/11.0 Mobile/15A5341f Safari/604.1",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "Origin": "https://www.duckdonuts.com",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Dest": "empty",
    "Accept-Language": "en-US,en;q=0.9",
}


def fetch_data():
    if True:
        url = "https://www.duckdonuts.com/international-locations/"
        r = session.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        loclist = soup.find("div", {"id": "LocationsCont"}).findAll("li")
        for loc in loclist:
            hours_of_operation = MISSING
            location_name = loc.find("h2").text
            if "COMING SOON" in location_name:
                continue
            raw_address = (
                loc.find("address")
                .get_text(separator="|", strip=True)
                .replace("|", " ")
            )
            log.info(location_name)
            page_url = loc.find("a")["href"]
            page_url = "https://www.duckdonuts.com" + page_url
            r = session.get(page_url, headers=headers)
            soup = BeautifulSoup(r.text, "html.parser")
            if "View All Hours" in r.text:
                payload = (
                    "_m_=HoursPopup&HoursPopup%24_edit_=16580&HoursPopup%24_command_="
                )
                r2 = session.post(page_url, headers=headers_2, data=payload)
                hours_of_operation = (
                    BeautifulSoup(r2.text, "html.parser")
                    .find("table")
                    .get_text(separator="|", strip=True)
                    .replace("|", " ")
                )
            try:
                longitude, latitude = (
                    soup.select_one("iframe[src*=maps]")["src"]
                    .split("!2d", 1)[1]
                    .split("!2m", 1)[0]
                    .split("!3d")
                )
            except:
                longitude = MISSING
                latitude = MISSING
            try:
                phone = loc.find("div", {"class": "phone"}).text
            except:
                phone = MISSING

            pa = parse_address_intl(raw_address)

            street_address = pa.street_address_1
            street_address = street_address if street_address else MISSING

            city = pa.city
            city = city.strip() if city else MISSING

            state = pa.state
            state = state.strip() if state else MISSING

            zip_postal = pa.postcode
            zip_postal = zip_postal.strip() if zip_postal else MISSING

            if "Dubai" in location_name:
                country_code = "Dubai"
            elif "Saudi Arabia" in location_name:
                country_code = "Saudi Arabia"
            elif "Bayamon" in location_name:
                country_code = "Bayamon"
            else:
                country_code = MISSING
            yield SgRecord(
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
                raw_address=raw_address,
            )


def scrape():
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {SgRecord.Headers.LOCATION_NAME, SgRecord.Headers.STREET_ADDRESS}
            )
        )
    ) as writer:
        for item in fetch_data():
            writer.write_row(item)


if __name__ == "__main__":
    scrape()
