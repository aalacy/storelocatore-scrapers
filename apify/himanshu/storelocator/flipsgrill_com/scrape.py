from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import SgRecordID
from sgpostal.sgpostal import parse_address_intl
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "flipsgrill_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "https://flipsgrill.com/"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        url = "https://flipsgrill.com/locations/"
        r = session.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        loclist = soup.find("div", {"class": "et_pb_row et_pb_row_1"}).findAll(
            "div", {"class": "et_pb_css_mix_blend_mode_passthrough"}
        )
        for loc in loclist:
            location_name = loc.find("h5").text
            log.info(location_name)
            temp_var = loc.findAll("p")
            raw_address = (
                temp_var[0].get_text(separator="|", strip=True).replace("|", " ")
            )
            pa = parse_address_intl(raw_address)

            street_address = pa.street_address_1
            street_address = street_address if street_address else MISSING

            city = pa.city
            city = city.strip() if city else MISSING

            state = pa.state
            state = state.strip() if state else MISSING

            zip_postal = pa.postcode
            zip_postal = zip_postal.strip() if zip_postal else MISSING

            country_code = "US"
            phone = loc.select_one("a[href*=tel]").text
            hours_of_operation = (
                temp_var[1].get_text(separator="|", strip=True).split("|")[0]
            )
            longitude, latitude = (
                loc.select_one("iframe[src*=maps]")["src"]
                .split("!2d", 1)[1]
                .split("!2m", 1)[0]
                .split("!3d")
            )
            if "!3m" in latitude:
                latitude = latitude.split("!3m")[0]
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
