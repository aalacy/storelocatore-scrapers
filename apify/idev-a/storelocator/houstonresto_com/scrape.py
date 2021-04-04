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
            hours = [
                hh.text
                for hh in soup1.select("div.entry-content.our-restaurants p")[1:]
            ]
            if "COMING SOON" in hours:
                continue
            if not re.search(r"tel:", hours[-1], re.IGNORECASE):
                del hours[-1]
            for x, hh in enumerate(hours):
                if not re.search(r"Monday", hh, re.IGNORECASE):
                    del hours[x]
            hours_of_operation = ""
            if hours:
                if "we have closed" not in " ".join(hours):
                    hours_of_operation = hours[0].replace("\n", "; ")
            addr = parse_address_intl(
                soup1.select_one("div.entry-content.our-restaurants p").text.replace(
                    "|", ""
                )
            )
            phone = (
                (
                    soup1.find(
                        "h3", string=re.compile(r"Nos coordonnées", re.IGNORECASE)
                    )
                    .find_next_sibling("p")
                    .stripped_strings
                )[0]
                .replace("TEL:", "")
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
                hours_of_operation=_valid(hours_of_operation),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
