from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import SgRecordID
from sgpostal.sgpostal import parse_address_intl
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "shawarmaroyale_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "https://www.shawarmaroyale.com/"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        r = session.get(DOMAIN, headers=headers)
        city_list = r.text.split("CONTACT US")[0].split("<h3")[1:]
        for temp_city in city_list:
            temp_city = BeautifulSoup(temp_city, "html.parser")
            city = temp_city.find("span").text
            loclist = temp_city.findAll("div", {"data-testid": "richTextElement"})
            for loc in loclist:
                temp = loc.get_text(separator="|", strip=True).split("|")
                if len(temp) < 2:
                    continue
                location_name = MISSING
                phone = temp[-1]
                if temp[0].split()[0] in temp[1]:
                    location_name = temp[0]
                    raw_address = " ".join(temp[1:-1])
                else:
                    raw_address = " ".join(temp[:-1])
                log.info(raw_address)
                latitude, longitude = (
                    loc.find("a")["href"].split("@")[1].split(",15z")[0].split(",")
                )
                pa = parse_address_intl(raw_address.replace("Mountain", ""))

                street_address = pa.street_address_1
                street_address = street_address if street_address else MISSING

                state = pa.state
                state = state.strip() if state else MISSING

                zip_postal = pa.postcode
                zip_postal = zip_postal.strip() if zip_postal else MISSING
                if street_address == "89 Park Pl Blvd":
                    city = "Barrie"
                if "1786 Stone Church Rd E " in raw_address:
                    city = "Hamilton"
                country_code = "CA"
                yield SgRecord(
                    locator_domain=DOMAIN,
                    page_url=DOMAIN,
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
                    hours_of_operation=MISSING,
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
