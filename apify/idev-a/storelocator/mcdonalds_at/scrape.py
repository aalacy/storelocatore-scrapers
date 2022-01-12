from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgselenium import SgChrome
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import SgRecordID
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

locator_domain = "https://www.mcdonalds.at"
base_url = "https://www.mcdonalds.at/restaurants"


def fetch_data():
    with SgChrome() as driver:
        driver.get(base_url)
        soup = bs(driver.page_source, "lxml")
        locations = soup.select("article.wpgb-card")
        for _ in locations:
            addr = list(_.p.stripped_strings)
            coord = (
                _.select_one("a.wso-route-button")["href"]
                .split("/@")[1]
                .split("/data")[0]
                .split(",")
            )
            yield SgRecord(
                page_url=base_url,
                street_address=addr[0].replace("\n", " "),
                city=addr[1].split()[0],
                zip_postal=addr[1].split()[-1],
                country_code="Austria",
                locator_domain=locator_domain,
                latitude=coord[0],
                longitude=coord[1],
                hours_of_operation=_.select("p")[1].text.strip(),
                raw_address=" ".join(addr).replace("\n", " "),
            )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
