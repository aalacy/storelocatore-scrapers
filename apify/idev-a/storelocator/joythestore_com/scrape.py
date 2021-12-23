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


locator_domain = "https://www.joythestore.com"
base_url = "https://www.joythestore.com/store-finder"


def fetch_data():
    with SgChrome() as driver:
        driver.get(base_url)
        soup = bs(driver.page_source, "lxml")
        locations = soup.select(
            "section.vtex-store-components-3-x-container > div > div  div.items-stretch.pr0"
        )
        for _ in locations:
            if not _.text.strip():
                break
            p = _.select("p")
            addr = list(p[1].stripped_strings)
            phone = ""
            if "Phone" in addr[-1]:
                phone = addr[-1].split(":")[-1]
            raw_address = addr[0].split(":")[-1].strip()
            street_address = " ".join(raw_address.split()[:-2]).strip()
            if street_address.endswith(","):
                street_address = street_address[:-1]
            yield SgRecord(
                page_url=base_url,
                location_name=p[0].text.strip(),
                street_address=street_address,
                city=p[0]
                .text.replace("JOY", "")
                .replace("OUTLET O2 ARENA", "")
                .strip(),
                zip_postal=" ".join(raw_address.split()[-2:]),
                country_code="UK",
                phone=phone,
                locator_domain=locator_domain,
                raw_address=raw_address,
            )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
