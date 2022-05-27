from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


session = SgRequests()
website = "americasmattress_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)

DOMAIN = "https://www.americasmattress.com"
MISSING = SgRecord.MISSING

token_url = "https://www.americasmattress.com/springfield-il/locations"
r = session.get(token_url)
soup = BeautifulSoup(r.text, "html.parser")
token = soup.find("meta", {"name": "csrf-token"})["content"]


headers = {
    "Connection": "keep-alive",
    "Content-Length": "0",
    "sec-ch-ua": '"Google Chrome";v="95", "Chromium";v="95", ";Not A Brand";v="99"',
    "Accept": "*/*",
    "X-CSRF-Token": token,
    "sec-ch-ua-mobile": "?0",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36",
    "X-Requested-With": "XMLHttpRequest",
    "sec-ch-ua-platform": '"Windows"',
    "Origin": "https://www.americasmattress.com",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Dest": "empty",
    "Referer": "https://www.americasmattress.com/springfield-il/locations",
    "Accept-Language": "en-US,en;q=0.9",
}


def fetch_data():
    if True:
        url = "https://www.americasmattress.com/springfield-il/locations/finderajax"
        loclist = session.post(url, headers=headers).json()
        for loc in loclist:
            location_name = loc["name"]
            if "Test Location" in location_name:
                continue
            elif "Coming Soon" in location_name:
                continue
            latitude = loc["latitude"]
            longitude = loc["longtitude"]
            store_number = loc["id"]
            page_url = DOMAIN + loc["url"]
            log.info(page_url)
            try:
                r = session.get(page_url, headers=headers)
                soup = BeautifulSoup(r.text, "html.parser")
            except:
                hours_of_operation = MISSING
            try:
                hours_of_operation = (
                    soup.find("div", {"class": "locations--store-hours"})
                    .get_text(separator="|", strip=True)
                    .replace("|", " ")
                )
            except:
                hours_of_operation = MISSING
            street_address = loc["address"]
            city = loc["city"]
            state = loc["state"]
            zip_postal = loc["zipcode"]
            street_address = loc["address"]
            if "North Georgia Premium Outlet Mall" in street_address:
                street_address = soup.find(
                    "span", {"class": "locations--store-address-line2"}
                ).text
            phone = loc["phone"]
            if "@" in street_address:
                street_address = street_address.split("@")[0]
            elif "Next" in street_address:
                street_address = street_address.split("Next")[0]
            elif "Near" in street_address:
                street_address = street_address.split("Near")[0]
            country_code = "US"
            yield SgRecord(
                locator_domain=DOMAIN,
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zip_postal,
                country_code=country_code,
                store_number=store_number,
                phone=phone,
                location_type=MISSING,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hours_of_operation,
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
