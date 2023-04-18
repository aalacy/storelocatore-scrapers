from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgselenium import SgChrome
from bs4 import BeautifulSoup as bs
import ssl
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification


_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.cityoptical.com"
base_url = "https://www.cityoptical.com/locations"


def fetch_data():
    with SgChrome() as driver:
        driver.get(base_url)
        soup = bs(driver.page_source, "lxml")
        links = [
            ll
            for ll in soup.select(
                'main div[data-testid="mesh-container-content"] div[data-testid="richTextElement"]'
            )
            if ll.h2 or ll.p
        ]
        for x in range(0, len(links), 2):
            h2 = links[x].select("h2")
            addr = h2[1].text.replace("\xa0", " ").split(",")
            hours = [hh.text for hh in links[x + 1].select("p")]
            if "Hours" in hours[0]:
                del hours[0]

            hours_of_operation = (
                "; ".join(hours)
                .replace("–", "-")
                .replace("\xa0", "")
                .replace("  ", " ")
            )
            hours_of_operation = " ".join(
                [hh for hh in hours_of_operation.split() if hh.strip()]
            )
            yield SgRecord(
                page_url=base_url,
                location_name=h2[0].text.strip(),
                street_address=" ".join(addr[:-2]),
                city=addr[-2].strip(),
                state=addr[-1].strip().split(" ")[0].strip(),
                zip_postal=" ".join(addr[-1].strip().split(" ")[1:]),
                country_code="US",
                phone=h2[2].text.strip(),
                locator_domain=locator_domain,
                hours_of_operation=hours_of_operation,
                raw_address=" ".join(addr),
            )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
