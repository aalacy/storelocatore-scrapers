from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgselenium import SgChrome
from bs4 import BeautifulSoup as bs
import re
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


locator_domain = "https://eattopround.com"
base_url = "https://eattopround.com/locations-menus"


def fetch_data():
    with SgChrome() as driver:
        driver.get(base_url)
        soup = bs(driver.page_source, "lxml")
        links = soup.select("div.et_pb_gutters1.et_pb_row_4col")
        for link in links:
            if not link.p:
                continue
            coord = link.h3.a["href"].split("/@")[1].split("/data")[0].split(",")
            addr = list(link.p.stripped_strings)
            _hr = link.find("strong", string=re.compile(r"^Hours", re.IGNORECASE))
            hours = []
            if _hr:
                hours.append(list(_hr.find_parent().stripped_strings)[1])
                if "Phone" not in _hr.find_parent().find_next_sibling().text:
                    hours.append(_hr.find_parent().find_next_sibling().text.strip())

            _pp = link.find("a", href=re.compile(r"tel:", re.IGNORECASE))
            phone = ""
            if _pp:
                phone = _pp.text.strip()

            city = addr[-1].split(",")[0].strip()
            yield SgRecord(
                page_url=base_url,
                location_name=city,
                street_address=" ".join(addr[:-1]).replace(
                    "Irvine Spectrum Center", ""
                ),
                city=city,
                state=addr[-1].split(",")[1].strip().split()[0].strip(),
                zip_postal=addr[-1].split(",")[1].strip().split()[-1].strip(),
                country_code="US",
                phone=phone,
                locator_domain=locator_domain,
                latitude=coord[0],
                longitude=coord[1],
                hours_of_operation="; ".join(hours).replace("–", "-"),
                raw_address=" ".join(addr),
            )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
