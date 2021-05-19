from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
from sgscrape.sgpostal import parse_address_intl

logger = SgLogSetup().get_logger("syb")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def _v(val):
    val = val.strip()
    if val.endswith(":"):
        val = val[:-1]
    return val


def fetch_data():
    locator_domain = "https://syb.com"
    base_url = "https://syb.com/locations/?ext=."
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        links = soup.select("div.container .col-sm-9 a.button")
        logger.info(f"{len(links)} found")
        for link in links:
            page_url = locator_domain + link["href"]
            logger.info(page_url)
            sp1 = bs(session.get(page_url, headers=_headers).text, "lxml")
            locations = sp1.select("div.location")
            for _ in locations:
                if _.img:
                    _name = _.img.find_next_sibling().text
                    coord = _.img["src"].split("ll=")[1].split("&")[0].split(",")
                else:
                    _name = _.select_one(".location_name").text
                    coord = _.a["href"].split("ll=")[1].split("&")[0].split(",")
                _addr = list(_.select_one("p.address").stripped_strings)
                del _addr[-1]
                if "Direction" in _addr[-1]:
                    del _addr[-1]
                addr = parse_address_intl(" ".join(_addr[:-2]))
                street_address = addr.street_address_1
                if addr.street_address_2:
                    street_address += " " + addr.street_address_2
                try:
                    yield SgRecord(
                        page_url=page_url,
                        location_name=_v(_name),
                        street_address=street_address,
                        city=addr.city,
                        state=addr.state,
                        zip_postal=addr.postcode,
                        country_code="US",
                        phone=_addr[-2].replace("(Louisville)", ""),
                        latitude=coord[0],
                        longitude=coord[1],
                        locator_domain=locator_domain,
                        hours_of_operation=_addr[-1]
                        .replace("–", "-")
                        .replace(",", ";"),
                    )
                except:
                    import pdb

                    pdb.set_trace()


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
