import unicodedata
from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import SgRecordID
from sgpostal.sgpostal import parse_address_intl
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "thinkkitchen_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "https://thinkkitchen.ir/"
MISSING = SgRecord.MISSING


def strip_accents(text):

    text = unicodedata.normalize("NFD", text).encode("ascii", "ignore").decode("utf-8")

    return str(text)


def fetch_data():
    if True:
        url = "https://thinkkitchen.ir/en/storelocator.html"
        r = session.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        country_list = soup.find("div", {"class": "layer1"})
        country_list = str(country_list).split("<ul")[1:]
        for country in country_list:
            loclist = country.split("<strong>")[1:]
            country_code = country.split("</ul>")[0].split("\n")[1]
            for loc in loclist:
                if "comming soon" in loc:
                    continue
                loc = (
                    BeautifulSoup(loc, "html.parser")
                    .get_text(separator="|", strip=True)
                    .split("|")
                )
                location_name = loc[0]
                if "International" in loc[-1]:
                    del loc[-1]
                if "0919-8923105" in loc[-1]:
                    del loc[-1]
                phone = loc[-1].replace("Phone", "")
                if "," in phone:
                    phone = MISSING
                if "Opening in August" in phone:
                    phone = MISSING
                raw_address = strip_accents(" ".join(loc[1:-1]))
                log.info(raw_address)
                pa = parse_address_intl(raw_address)

                street_address = pa.street_address_1
                street_address = street_address if street_address else MISSING

                city = pa.city
                city = city.strip() if city else MISSING

                state = pa.state
                state = state.strip() if state else MISSING

                zip_postal = pa.postcode
                zip_postal = zip_postal.strip() if zip_postal else MISSING

                if zip_postal != MISSING:
                    country_code = "CANADA"
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
                    latitude=MISSING,
                    longitude=MISSING,
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
