from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import parse_address_intl

logger = SgLogSetup().get_logger("verstlogistics")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.verstlogistics.com"
base_url = "https://www.verstlogistics.com/cincinnati-ohio-and-kentucky-fulfillment-warehouse-and-transportation-management-locations"


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        links = soup.select("div.servicesGroupItem ul li a")
        logger.info(f"{len(links)} found")
        for link in links:
            page_url = locator_domain + link["href"]
            logger.info(page_url)
            sp1 = bs(session.get(page_url, headers=_headers).text, "lxml")
            locations = sp1.select("div.desktopAccordions div.accordContent__Area")
            for _ in locations:
                raw_address = _.span.text.strip()
                addr = parse_address_intl(raw_address)
                street_address = addr.street_address_1
                if addr.street_address_2:
                    street_address += " " + addr.street_address_2
                yield SgRecord(
                    page_url=page_url,
                    location_name=sp1.h1.text.strip(),
                    street_address=street_address,
                    city=addr.city,
                    state=addr.state,
                    zip_postal=addr.postcode,
                    country_code="US",
                    locator_domain=locator_domain,
                    raw_address=raw_address,
                )

            blocks = []
            for block in sp1.select(
                'div.body-container-wrapper span.hs_cos_wrapper.hs_cos_wrapper_widget.hs_cos_wrapper_type_rich_text p[style="text-align: center;"]'
            ):
                tt = block.text.strip().lower()
                if not tt:
                    continue
                if "check" in tt or "location" in tt or "started" in tt or "view" in tt:
                    continue
                blocks.append(block)

            if blocks:
                addr = list(blocks[0].stripped_strings)
                if "verst" in addr[0].lower():
                    del addr[0]
                phone = ""
                if _p(addr[-1]):
                    phone = addr[-1]
                try:
                    coord = (
                        blocks[0].a["href"].split("/@")[1].split("/data")[0].split(",")
                    )
                except:
                    coord = ["", ""]
                yield SgRecord(
                    page_url=page_url,
                    location_name=sp1.h1.text.strip(),
                    street_address=addr[0],
                    city=addr[1].split(",")[0].strip(),
                    state=addr[1].split(",")[1].strip().split(" ")[0].strip(),
                    zip_postal=addr[1].split(",")[1].strip().split(" ")[-1].strip(),
                    country_code="US",
                    phone=phone,
                    locator_domain=locator_domain,
                    latitude=coord[0],
                    longitude=coord[1],
                )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
