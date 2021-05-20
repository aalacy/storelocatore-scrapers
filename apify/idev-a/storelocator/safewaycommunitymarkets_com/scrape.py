from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
import json
from sgscrape.sgpostal import parse_address_intl
import ssl

try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "https://www.andronicos.com/"
    base_url = "https://www.andronicos.com/locations"
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        map_block = soup.select("section.Main-content div.map-block")
        html_block = soup.select("section.Main-content div.html-block")[1:]
        button_block = soup.select("section.Main-content div.button-block")
        locations = zip(map_block, html_block, button_block)
        for _ in locations:
            map_data = json.loads(_[0]["data-block-json"])
            block = list(_[1].stripped_strings)[1:]
            addr = parse_address_intl(" ".join(block[:2]))
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2
            location_name = _[1].h3.text.strip().split("Now Open")[0].strip()
            if location_name.endswith("-"):
                location_name = location_name[:-1]
            yield SgRecord(
                page_url=_[2].a["href"],
                location_name=location_name,
                street_address=street_address,
                city=addr.city,
                state=addr.state,
                zip_postal=addr.postcode,
                country_code=map_data["location"]["addressCountry"],
                phone=block[-1],
                locator_domain=locator_domain,
                latitude=map_data["location"]["mapLat"],
                longitude=map_data["location"]["mapLng"],
                hours_of_operation=block[-3].replace("–", "-"),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
