from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
import re
from bs4 import BeautifulSoup as bs
import dirtyjson as json
from sgscrape.sgpostal import parse_address_intl

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "https://www.bankmw.com/"
    base_url = "https://www.bankmw.com/locations/"
    with SgRequests() as session:
        res = session.get(base_url, headers=_headers).text
        locations = json.loads(
            bs(res, "lxml")
            .find("script", string=re.compile(r"window.config.indexes.locations ="))
            .string.split("window.config.indexes.locations =")[1]
            .strip()[1:-2]
            .replace("\\/", "/")
            .replace('\\"', '"')
        )
        for _ in locations:
            addr = parse_address_intl(
                " ".join(bs(_["address"], "lxml").stripped_strings)
            )
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2
            page_url = f"https://www.bankmw.com/location/{_['name']}"
            location_type = ""
            hours_of_operation = ""
            if _["atm_only"]:
                location_type = "atm"
                hours_of_operation = _["atm_services_str"].split(",")[0]
                if hours_of_operation == "Limited Hours":
                    hours_of_operation = ""
            else:
                location_type = "branch"
                hours_of_operation = "; ".join(
                    bs(_["drivethru_hours_str"], "lxml").stripped_strings
                )
                if _["atm_services"]:
                    location_type += ",atm"
            yield SgRecord(
                page_url=page_url,
                location_name=_["title"],
                street_address=street_address,
                city=addr.city,
                state=addr.state,
                zip_postal=addr.postcode,
                latitude=_["lat"],
                longitude=_["lng"],
                country_code="US",
                phone=_["phone"],
                location_type=location_type,
                locator_domain=locator_domain,
                hours_of_operation=hours_of_operation,
                raw_address=_["address_clean"],
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
