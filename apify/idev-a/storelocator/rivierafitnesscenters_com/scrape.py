from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
import re
from sgscrape.sgpostal import parse_address_intl
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("rivierafitnesscenters")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "https://rivierafitnesscenters.com/"
    base_url = "https://rivierafitnesscenters.com/"
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        links = soup.select("div.rr-module-hover h4 a")
        for link in links:
            logger.info(link["href"])
            sp1 = bs(session.get(link["href"], headers=_headers).text, "lxml")
            locs = sp1.select(
                "div.et_pb_row_7 div.et_pb_css_mix_blend_mode_passthrough"
            )
            for _ in locs:
                addr = list(_.select_one("div.et_pb_text_inner").stripped_strings)[:2]
                _hr = _.find("h4", string=re.compile(r"Hours", re.IGNORECASE))
                hours = []
                if _hr:
                    hours = [
                        hh.text.strip().replace("\n", "; ")
                        for hh in _hr.find_next_siblings()
                        if hh.text.strip()
                    ]

                yield SgRecord(
                    page_url=link["href"],
                    location_name=link.text.strip(),
                    street_address=addr[0],
                    city=addr[1].split(",")[0].strip(),
                    state=addr[1].split(",")[1].strip().split(" ")[0].strip(),
                    zip_postal=addr[1].split(",")[1].strip().split(" ")[-1].strip(),
                    country_code="US",
                    locator_domain=locator_domain,
                    hours_of_operation="; ".join(hours),
                )

        links = soup.select("div.popmake-content a")
        for link in links:
            logger.info(link["href"])
            sp1 = bs(session.get(link["href"], headers=_headers).text, "lxml")
            _addr = sp1.find("h4", string=re.compile(r"Address", re.IGNORECASE))
            addr = parse_address_intl(_addr.find_next_sibling().text.strip())
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2
            _phone = sp1.find("strong", string=re.compile(r"Phone", re.IGNORECASE))
            phone = _phone.next.next.strip()
            _hr = sp1.find("h4", string=re.compile(r"Hours", re.IGNORECASE))
            hours = []
            if _hr:
                hours = list(_hr.find_next_sibling().stripped_strings)
            coord = sp1.iframe["src"].split("!2d")[1].split("!2m")[0].split("!3d")

            yield SgRecord(
                page_url=link["href"],
                location_name=link.text.strip(),
                street_address=street_address,
                city=addr.city,
                state=addr.state,
                zip_postal=addr.postcode,
                latitude=coord[1],
                longitude=coord[0],
                country_code="US",
                phone=phone,
                hours_of_operation="; ".join(hours),
                locator_domain=locator_domain,
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
