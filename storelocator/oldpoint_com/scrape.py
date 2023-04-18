from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
import re
from sgscrape.sgpostal import parse_address_intl
import demjson

logger = SgLogSetup().get_logger("oldpoint")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "https://oldpoint.com"
    base_url = "https://oldpoint.com/locations"
    with SgRequests() as session:
        res = session.get(base_url, headers=_headers).text
        coords = demjson.decode(
            res.split("var locations =")[1]
            .split("for (")[0]
            .replace("\t", "")
            .replace("\n", "")
            .strip()[:-1]
        )
        soup = bs(res, "lxml")
        links = soup.select_one("div#map_search").findChildren(recursive=False)
        logger.info(f"{len(links)} found")
        name = phone = hours_of_operation = location_type = ""
        idx = 0
        for link in links:
            if link.name in ["h3", "form"]:
                continue
            if link.name != "hr" and not link.text.strip():
                continue
            if "Appointment" in link.text.strip():
                continue
            if link.img:
                continue
            if link.a:
                page_url = locator_domain + link.a["href"]
                _addr = list(link.stripped_strings)
                name = " ".join(_addr[:-1])
                if "branch" in name.lower():
                    location_type = "branch"
                if "atm" in name.lower():
                    location_type = "atm"
                addr = parse_address_intl(_addr[-1])
                street_address = addr.street_address_1
                if addr.street_address_2:
                    street_address += " " + addr.street_address_2
            if link.find("strong", string=re.compile(r"Phone:")):
                _phone = list(
                    link.find("strong", string=re.compile(r"Phone:"))
                    .find_parent("p")
                    .stripped_strings
                )
                if len(_phone) > 1:
                    phone = _phone[1]
                else:
                    phone = (
                        link.find("strong", string=re.compile(r"Phone:"))
                        .find_parent("p")
                        .find_next_sibling()
                        .text.strip()
                    )
            if link.find("strong", string=re.compile(r"Lobby Hours:")):
                hours_of_operation = list(
                    link.find("strong", string=re.compile(r"Lobby Hours:"))
                    .find_parent("p")
                    .stripped_strings
                )[1]
            if name and link.name == "hr":
                coord = coords[idx]
                raw_address = _addr[-1].strip()
                if raw_address == ",":
                    raw_address = ""
                yield SgRecord(
                    page_url=page_url,
                    location_name=name,
                    raw_address=raw_address,
                    street_address=street_address,
                    city=addr.city,
                    state=addr.state,
                    zip_postal=addr.postcode,
                    country_code="US",
                    phone=phone,
                    latitude=coord[1],
                    longitude=coord[2],
                    location_type=location_type,
                    locator_domain=locator_domain,
                    hours_of_operation=hours_of_operation,
                )
                name = phone = hours_of_operation = location_type = ""
                idx += 1


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
