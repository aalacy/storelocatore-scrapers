from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgselenium import SgChrome
from bs4 import BeautifulSoup as bs
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

locator_domain = "https://www.patsmarketplace.com"
base_url = "https://www.patsmarketplace.com/"


def _url(phone, locs):
    url = ""
    for loc in locs:
        if phone == loc.select("p")[3].text.strip():
            url = locator_domain + loc.a["href"]
            break

    return url


def fetch_data():
    with SgChrome() as driver:
        driver.get(base_url)
        soup = bs(driver.page_source, "lxml")
        locations = soup.select("div#dmFirstContainer  div.dmRespRow.fullBleedChanged")[
            -2:
        ]
        locs = soup.select("div.mini-header-hide-row div.dmNewParagraph")
        for _ in locations:
            block = _.select("div.dmNewParagraph")
            addr = list(block[1].stripped_strings)
            loc = _.select_one("div.inlineMap")
            yield SgRecord(
                page_url=_url(addr[-1], locs),
                store_number=loc["id"],
                location_name=block[0].text.strip(),
                street_address=addr[0],
                city=addr[1].split(",")[0].strip(),
                state=addr[1].split(",")[1].strip().split(" ")[0].strip(),
                zip_postal=addr[1].split(",")[1].strip().split(" ")[-1].strip(),
                country_code="US",
                locator_domain=locator_domain,
                raw_address=loc["data-address"],
                latitude=loc["data-lat"],
                longitude=loc["data-lng"],
                phone=addr[-1],
                hours_of_operation=list(block[-1].stripped_strings)[-1].replace(
                    "–", "-"
                ),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
