from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
import re
from sgscrape.sgpostal import parse_address_intl

logger = SgLogSetup().get_logger("cleanslatecenters")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def _h(temp):
    hours = []
    for hh in temp:
        if "call" in hh.lower() or "hour" in hh.lower():
            break
        hours.append(
            hh.split("(")[0]
            .strip()
            .replace("–", "-")
            .replace("\xa0", "")
            .replace("    ", " ")
        )

    return hours


def fetch_data():
    locator_domain = "https://www.cleanslatecenters.com/"
    base_url = "https://www.cleanslatecenters.com/our-location"
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        links = soup.select("div.hs_cos_wrapper_type_custom_widget")
        logger.info(f"{len(links)} found")
        for link in links:
            page_url = link.a["href"]
            logger.info(page_url)
            sp1 = bs(session.get(page_url, headers=_headers).text, "lxml")
            addr = list(link.select_one("div.address-div").stripped_strings)[:-1]
            _addr = []
            for aa in addr:
                if "phone" in aa.lower():
                    break
                _addr.append(aa)
            addr = parse_address_intl(" ".join(_addr))
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2
            _hr = sp1.find("strong", string=re.compile(r"HOURS OF OPERATION"))
            hours = []
            if _hr:
                hours = [
                    "; ".join(hh.stripped_strings)
                    for hh in _hr.find_parent().find_next_siblings("p")
                ]
            else:
                _hr = sp1.find_all("strong", string=re.compile(r"ADDRESS"))
                if len(_hr) > 1:
                    hours = [
                        "; ".join(hh.stripped_strings)
                        for hh in _hr[1].find_parent().find_next_siblings("p")
                    ]
            try:
                coord = (
                    sp1.select_one("div.locations-map-responsive iframe")["src"]
                    .split("!2d")[1]
                    .split("!3m")[0]
                    .split("!2m")[0]
                    .split("!3d")
                )
            except:
                coord = ["", ""]
            yield SgRecord(
                page_url=page_url,
                location_name=link.select_one(".map-name-sec").text.strip(),
                street_address=street_address,
                city=addr.city,
                state=addr.state,
                zip_postal=addr.postcode,
                country_code="US",
                phone=link.select_one(".telephone-link").text.strip(),
                locator_domain=locator_domain,
                latitude=coord[1],
                longitude=coord[0],
                hours_of_operation="; ".join(_h(hours)),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
