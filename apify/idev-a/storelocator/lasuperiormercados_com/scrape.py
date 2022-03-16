from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgpostal import parse_address_intl
import re


locator_domain = "http://www.lasuperiormercados.com/"
base_url = "https://www.lasuperiormercados.com/locations#"


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url).text, "lxml")
        stores = soup.select("div.store-info-box")
        for _ in stores:
            try:
                coord = _.iframe["src"].split("!2d")[1].split("!2m")[0].split("!3d")
            except:
                coord = ["", ""]

            addr = parse_address_intl(_.a.text.strip())
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2
            phone = ""
            if _.find("a", href=re.compile(r"tel:")):
                phone = _.find("a", href=re.compile(r"tel:")).text.strip()
            yield SgRecord(
                page_url=base_url,
                location_name=_.h2.text.strip(),
                street_address=street_address,
                city=addr.city,
                state=addr.state,
                zip_postal=addr.postcode,
                phone=phone,
                country_code="US",
                locator_domain=locator_domain,
                latitude=coord[1],
                longitude=coord[0],
                hours_of_operation="; ".join(_.p.stripped_strings),
                raw_address=_.a.text.strip(),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
