from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgpostal import parse_address_intl
from bs4 import BeautifulSoup as bs
import re

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def _valid(val):
    return val.replace("–", "-").strip()


def fetch_data():
    locator_domain = "https://houstonresto.com"
    base_url = "https://houstonresto.com/fr/nos-restaurants/"
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        locations = soup.select("div.restaurant-list ul li a")
        for _ in locations:
            page_url = locator_domain + _["href"]
            soup1 = bs(session.get(page_url, headers=_headers).text, "lxml")
            hours = []

            for hh in soup1.select("div.entry-content.our-restaurants p")[1:]:
                if re.search(r"NOS HEURES D’OUVERTURE VARIENT", hh.text, re.IGNORECASE):
                    continue
                if re.search(r"nous avons fermé nos", hh.text, re.IGNORECASE):
                    hours = ["Closed"]
                if re.search(r"LUNDI", hh.text, re.IGNORECASE):
                    hours = list(hh.stripped_strings)

            hours1 = []
            for x in range(0, len(hours), 2):
                hours1.append(f"{hours[x]}: {hours[x+1]}")

            addr = parse_address_intl(
                soup1.select_one("div.entry-content.our-restaurants p").text.replace(
                    "|", ""
                )
            )
            phone_block = list(
                soup1.find("h3", string=re.compile(r"Nos coordonnées", re.IGNORECASE))
                .find_next_sibling("p")
                .stripped_strings
            )
            if (
                phone_block
                and not phone_block[0].replace("TEL:", "").replace("TÉL:", "").strip()
            ):
                del phone_block[0]
            phone = (
                phone_block[0]
                .split(":")[-1]
                .split("#")[0]
                .replace("TEL:", "")
                .replace("TÉL:", "")
                .strip()
            )
            yield SgRecord(
                page_url=page_url,
                location_name=_.text,
                street_address=addr.street_address_1,
                city=addr.city,
                state=addr.state,
                zip_postal=addr.postcode,
                country_code="CA",
                phone=phone,
                locator_domain=locator_domain,
                hours_of_operation=_valid("; ".join(hours1)),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
