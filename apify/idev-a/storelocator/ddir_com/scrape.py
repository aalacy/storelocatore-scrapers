from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
import json
from bs4 import BeautifulSoup as bs

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.ddir.com"
base_url = "https://www.ddir.com/locations/"


def _coord(city, zip_postal, locations):
    coord = ["", ""]
    for _ in locations:
        if city in _["address"] and zip_postal in _["address"]:
            coord[0] = _["point"]["lat"]
            coord[1] = _["point"]["lng"]
            break
    return coord


def fetch_data():
    with SgRequests() as session:
        res = session.get(base_url, headers=_headers).text
        links = bs(res, "lxml").select("div.block-grid div.block")
        locations = json.loads(res.split("mapp.data.push(")[1].split("); if")[0])[
            "pois"
        ]
        for link in links:
            addr = list(link.select_one("div.block-description p").stripped_strings)
            if len(addr) == 1:
                continue
            city = addr[1].split(",")[0].strip()
            zip_postal = (
                addr[1].split(",")[1].replace("\xa0", " ").strip().split(" ")[1].strip()
            )
            coord = _coord(city, zip_postal, locations)
            location_name = link.h2.text.strip()
            location_type = ""
            if "CLOSED UNTIL" in location_name:
                location_type = "temporarily closed"
            yield SgRecord(
                page_url=base_url,
                location_name=location_name.split("-")[-1],
                street_address=addr[0].strip(),
                state=addr[1]
                .split(",")[1]
                .replace("\xa0", " ")
                .strip()
                .split(" ")[0]
                .strip(),
                city=city,
                zip_postal=zip_postal,
                latitude=coord[0],
                longitude=coord[1],
                country_code="US",
                location_type=location_type,
                phone=addr[-1],
                locator_domain=locator_domain,
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
