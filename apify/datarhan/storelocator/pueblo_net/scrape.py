import re
import ssl
import json
from lxml import etree
from urllib.parse import unquote

from sgselenium import SgChrome
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgscrape.sgpostal import parse_address_intl

try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification


def fetch_data():
    start_url = "https://puebloweb.com/wp-json/wp/v2/pages/121"
    domain = re.findall(r"://(.+?)/", start_url)[0].replace("www.", "")

    with SgChrome() as driver:
        driver.get(start_url)
        unquoted = unquote(driver.page_source)
        unquoted = (
            unquoted.replace("\\n", "")
            .replace("\\t", "")
            .replace("\\", "")
            .replace("&gt;", ">")
            .replace("&lt;", "<")
            .replace("  ", " ")
        )
    data = re.findall(
        "google-maps-options=(.+)  data-elfsight-google-maps-version", unquoted
    )[0].strip()[1:-1]
    data = json.loads(data)

    for poi in data["markers"]:
        addr = parse_address_intl(poi["infoAddress"])
        street_address = addr.street_address_1
        if addr.street_address_2:
            street_address += " " + addr.street_address_2
        zip_code = poi["infoAddress"].split()[-1]
        if not zip_code.isdigit():
            zip_code = SgRecord.MISSING
        hoo = etree.HTML(poi["infoDescription"]).xpath("//text()")
        hoo = [e.strip() for e in hoo if e.strip() and "Tel" not in e]
        hoo = (
            " ".join(hoo).split("Horario:")[-1].split(poi["infoPhone"])[0].strip()
            if hoo
            else SgRecord.MISSING
        )

        item = SgRecord(
            locator_domain=domain,
            page_url="https://puebloweb.com/tiendas/",
            location_name=poi["infoTitle"],
            street_address=street_address,
            city=addr.city,
            state=SgRecord.MISSING,
            zip_postal=zip_code,
            country_code="PR",
            store_number=SgRecord.MISSING,
            phone=poi["infoPhone"],
            location_type=SgRecord.MISSING,
            latitude=poi["coordinates"].split(", ")[0],
            longitude=poi["coordinates"].split(", ")[-1],
            hours_of_operation=hoo,
            raw_address=poi["infoAddress"],
        )

        yield item


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
