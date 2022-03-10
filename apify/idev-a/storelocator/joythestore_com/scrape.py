from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgselenium import SgChrome
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
import ssl
from sgpostal.sgpostal import parse_address_intl

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
            if not _.text.strip() or not _.p or len(_.select("p")) < 2:
                break
            p = _.select("p")
            _addr = list(p[1].stripped_strings)
            phone = ""
            _pp = list(p[-2].stripped_strings)[-1]
            if "Phone" in _pp:
                phone = _pp.split(":")[-1]

            raw_address = _addr[0].split(":")[-1].strip()
            addr = parse_address_intl(raw_address + ", United Kingdom")
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2

            hours = list(p[-1].stripped_strings)
            if hours:
                hours = hours[1:]
            try:
                coord = _.a["href"].split("/@")[1].split("/data")[0].split(",")
            except:
                coord = ["", ""]
            city = addr.city
            if not city:
                city = (
                    p[0].text.replace("JOY", "").replace("OUTLET O2 ARENA", "").strip()
                )
            yield SgRecord(
                page_url=base_url,
                location_name=p[0].text.strip(),
                street_address=street_address,
                city=city,
                zip_postal=" ".join(raw_address.split()[-2:]),
                country_code="UK",
                latitude=coord[0],
                longitude=coord[1],
                phone=phone,
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
                raw_address=raw_address,
            )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
