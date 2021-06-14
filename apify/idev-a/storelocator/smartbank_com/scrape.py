from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
import re
from bs4 import BeautifulSoup as bs
from sgscrape.sgpostal import parse_address_intl

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def _i(locations, street_address):
    loc = {}
    for _loc in locations:
        if re.search(
            street_address, _loc["streetaddress"].replace(",", ""), re.IGNORECASE
        ):
            loc = _loc
            break
    return loc


def fetch_data():
    locator_domain = "https://www.smartbank.com/"
    base_url = "https://www.smartbank.com/contact-us/"
    json_url = "https://api-cdn.storepoint.co/v1/15a83293917490/locations?rq"
    with SgRequests() as session:
        locations = session.get(json_url, headers=_headers).json()["results"][
            "locations"
        ]
        locs = bs(session.get(base_url, headers=_headers).text, "lxml").select(
            "div.sb-location-states div.vc_column_container"
        )
        for _ in locs:
            if not _.text.strip():
                continue
            addr = parse_address_intl(
                " ".join(_.select_one("div.vc_toggle_content h4").stripped_strings)
            )
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2
            _phone = _.find("a", href=re.compile(r"tel:"))
            temp = [
                ":".join(hh.stripped_strings)
                for hh in _phone.find_parent().find_next_siblings("p")
            ]
            hours = []
            for hh in temp:
                if "drive" in hh.lower() or "Mortgage" in hh:
                    break
                hours.append(hh)
            location_name = _.h4.text.strip()
            loc = _i(locations, addr.street_address_1)
            yield SgRecord(
                page_url=base_url,
                location_name=location_name,
                store_number=loc.get("id"),
                street_address=street_address,
                city=addr.city,
                state=addr.state,
                zip_postal=addr.postcode,
                latitude=loc.get("loc_lat"),
                longitude=loc.get("loc_long"),
                country_code="US",
                phone=_phone.text.strip(),
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours).replace("–", "-"),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
