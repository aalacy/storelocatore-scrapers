from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgpostal import parse_address_intl
from bs4 import BeautifulSoup as bs
import re

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "https://www.loscucos.com/"
    base_url = "https://www.loscucos.com/locations.html"
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        locations = soup.select(
            "div#bp_infinity div.Location-Buttons---Background a.nonblock"
        )
        for link in locations:
            location_name = link.text.split("@")[0].strip()
            page_url = locator_domain + link["href"]
            soup1 = bs(session.get(page_url, headers=_headers).text, "lxml")
            title_tag = soup1.find_all(
                "img", alt=re.compile(f"^{location_name}", re.IGNORECASE)
            )[-2]
            hours_of_operation = (
                soup1.find("img", alt=re.compile(r"Business Hours", re.IGNORECASE))[
                    "alt"
                ]
                .replace("Business Hours", "")
                .strip()
            )
            siblings = title_tag.find_next_siblings("img")
            address = ""
            if siblings and len(siblings) > 2:
                address = title_tag.find_next_siblings("img")[0]["alt"]
            else:
                address = " ".join(
                    [_.text for _ in soup1.select("div.colelem.shared_content p")[:2]]
                )

            phone = ""
            try:
                phone = (
                    soup1.find("img", alt=re.compile(r"Telephone:", re.IGNORECASE))[
                        "alt"
                    ]
                    .split("Telephone:")[1]
                    .strip()
                    .split("Fax")[0]
                    .strip()
                )
            except:
                phone = (
                    soup1.find("p", string=re.compile(r"Telephone:"))
                    .text.split("Telephone:")[1]
                    .strip()
                    .split("Fax")[0]
                    .strip()
                )

            addr = parse_address_intl(address)
            yield SgRecord(
                page_url=page_url,
                location_name=location_name,
                street_address=addr.street_address_1,
                city=addr.city,
                state=addr.state,
                zip_postal=addr.postcode,
                country_code="US",
                phone=phone,
                locator_domain=locator_domain,
                hours_of_operation=hours_of_operation,
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
