from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "sutherlands_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36"
}

DOMAIN = "https://sutherlands.com"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        state_list = [
            "AL",
            "AK",
            "AZ",
            "AR",
            "CA",
            "CO",
            "CT",
            "DC",
            "DE",
            "FL",
            "GA",
            "HI",
            "ID",
            "IL",
            "IN",
            "IA",
            "KS",
            "KY",
            "LA",
            "ME",
            "MD",
            "MA",
            "MI",
            "MN",
            "MS",
            "MO",
            "MT",
            "NE",
            "NV",
            "NH",
            "NJ",
            "NM",
            "NY",
            "NC",
            "ND",
            "OH",
            "OK",
            "OR",
            "PA",
            "RI",
            "SC",
            "SD",
            "TN",
            "TX",
            "UT",
            "VT",
            "VA",
            "WA",
            "WV",
            "WI",
            "WY",
        ]
        for state_url in state_list:
            log.info(f"Fetching locations from state {state_url}...")
            state_url = "https://sutherlands.com/locations/" + state_url
            r = session.get(state_url, headers=headers)
            if "No Stores Match Your Search" in r.text:
                continue
            soup = BeautifulSoup(r.text, "html.parser")
            loclist = soup.findAll("div", {"class": "card-block"})
            for loc in loclist:
                if "NEW LOCATION!" in loc.text:
                    continue
                try:
                    page_url = loc.findAll("a")[2]["href"]
                except:
                    page_url = state_url
                location_name = loc.find("h3", {"itemprop": "name"}).text
                log.info(page_url)
                phone = loc.find("p", {"class": "phone"}).text
                street_address = loc.find("span", {"itemprop": "streetAddress"}).text
                city = loc.find("span", {"itemprop": "addressLocality"}).text
                latitude = MISSING
                longitude = MISSING
                state = loc.find("span", {"itemprop": "addressRegion"}).text
                zip_postal = loc.find("span", {"itemprop": "postalCode"}).text
                country_code = "US"
                hours_of_operation = loc.findAll("span", {"itemprop": "openingHours"})
                hours_of_operation = " ".join(
                    x.get_text(separator="|", strip=True).replace("|", " ")
                    for x in hours_of_operation
                )
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
                    phone=phone.strip(),
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
