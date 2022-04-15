import html
from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import SgRecordID
from sgpostal.sgpostal import parse_address_intl
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "captsub_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "https://captsub.com/"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        url = "http://captsub.com/locations/"
        r = session.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        loclist = str(soup.find("div", {"class": "entry-content"})).split(
            '<h4 style="text-align: left;">'
        )[1:]
        for loc in loclist:
            temp = BeautifulSoup(loc, "html.parser")
            loc = temp.get_text(separator="|", strip=True).split("|")
            if "Get Directions" in loc[-1]:
                del loc[-1]
            location_name = loc[0]
            log.info(location_name)
            raw_address = html.unescape(" ".join(loc[1:]))
            try:
                latitude, longitude = (
                    temp.find("a")["href"].split("!3d")[1].split("!4d")
                )
            except:
                try:
                    coords = temp.find("a")["href"].split("@")[1].split(",")
                    latitude = coords[0]
                    longitude = coords[1]
                except:
                    latitude = MISSING
                    longitude = MISSING
            pa = parse_address_intl(raw_address)

            street_address = pa.street_address_1
            street_address = street_address if street_address else MISSING

            city = pa.city
            city = city.strip() if city else MISSING

            state = pa.state
            state = state.strip() if state else MISSING

            zip_postal = pa.postcode
            zip_postal = zip_postal.strip() if zip_postal else MISSING

            country_code = "CA"
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
                phone=MISSING,
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
