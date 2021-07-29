from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
from sgscrape.sgpostal import parse_address_intl
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

logger = SgLogSetup().get_logger("groupeadonis")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def _coord(locs, phone):
    coord = ["", ""]
    _addr = ""
    for _ in locs:
        if phone in _:
            coord = _[4].split(",")
            _addr = _[2]
            break
    return coord, _addr


def fetch_data():
    locator_domain = "https://www.groupeadonis.ca"
    base_url = "https://www.groupeadonis.ca/find-us"
    json_url = "https://www.groupeadonis.ca/geometry"
    with SgRequests() as session:
        locs = session.get(json_url, headers=_headers).json()
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        links = soup.select("div#stores table")[1].select("tbody tr")
        logger.info(f"{len(links)} found")
        for link in links:
            td = link.select("td")
            page_url = locator_domain + td[-1].a["href"]
            logger.info(page_url)
            phone = td[2].text.strip()
            coord, _addr = _coord(locs, phone)
            sp1 = bs(session.get(page_url, headers=_headers).text, "lxml")
            addr = parse_address_intl(_addr)
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2
            hours = []
            for hh in sp1.select("main table tr"):
                if hh.select("td")[1].text.strip():
                    hours.append(":".join(hh.stripped_strings))
            location_name = td[0].text.strip()
            yield SgRecord(
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=addr.city,
                state=addr.state,
                zip_postal=addr.postcode,
                country_code="CA",
                phone=phone,
                locator_domain=locator_domain,
                latitude=coord[0],
                longitude=coord[1],
                hours_of_operation="; ".join(hours).replace("–", "-"),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
