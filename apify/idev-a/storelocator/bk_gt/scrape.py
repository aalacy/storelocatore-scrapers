from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgselenium import SgChrome
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup
import json
from sgscrape.sgpostal import parse_address_intl
from bs4 import BeautifulSoup as bs
import ssl

try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification


logger = SgLogSetup().get_logger("bk")

_headers = {
    "Host": "bk.gt",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "en-US,en;q=0.9,ko;q=0.8",
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://bk.gt"
base_url = "https://bk.gt/mas-cerca-de-ti"


def fetch_data():
    with SgChrome() as driver:
        driver.get(base_url)
        locations = json.loads(
            driver.page_source.split("var markers = JSON.parse(")[1].split(");")[0][
                1:-1
            ]
        )
        logger.info(f"{len(locations)} found")
        for link in locations:
            page_url = link["url"]
            logger.info(page_url)
            driver.get(page_url)
            sp1 = bs(driver.page_source, "lxml")
            raw_address = sp1.select_one(
                "div.container.ubicacion div.col-md-6 p"
            ).text.strip()
            if "Guatemala" not in raw_address:
                raw_address += " Guatemala"
            addr = parse_address_intl(raw_address)
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2
            zip_postal = addr.postcode
            if zip_postal and not zip_postal.isdigit():
                zip_postal = ""
            city = addr.city
            if city:
                city = (
                    city.replace("Guatemala", "")
                    .replace(".", "")
                    .replace("Cuesta Blanca", "")
                )
            yield SgRecord(
                page_url=page_url,
                location_name=link["title"],
                street_address=street_address,
                city=city,
                state=addr.state,
                zip_postal=zip_postal,
                latitude=link["latitud"],
                longitude=link["longitud"],
                country_code="Guatemala",
                locator_domain=locator_domain,
                hours_of_operation="-".join(
                    sp1.select("div.container.ubicacion div.col-md-6 p")[
                        -1
                    ].stripped_strings
                ),
                raw_address=raw_address,
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
