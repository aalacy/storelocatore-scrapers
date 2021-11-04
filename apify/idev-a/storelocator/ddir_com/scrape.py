from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
import json
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.ddir.com"
base_url = "https://www.ddir.com/locations/"


def _coord(street_address, city, zip_postal, locations):
    coord = ["", ""]
    for _ in locations:
        if " ".join(street_address.split(" ")[:2]) in _["address"] or (
            city in _["address"] and zip_postal in _["address"]
        ):
            coord[0] = _["point"]["lat"]
            coord[1] = _["point"]["lng"]
            break
    return coord


def _p(val):
    if (
        val.replace("(", "")
        .replace(")", "")
        .replace("+", "")
        .replace("-", "")
        .replace(".", " ")
        .replace("to", "")
        .replace(" ", "")
        .strip()
        .isdigit()
    ):
        return val
    else:
        return ""


def fetch_data():
    with SgRequests() as session:
        res = session.get(base_url, headers=_headers).text
        links = bs(res, "lxml").select("div.block-grid div.block")
        locations = json.loads(res.split("mapp.data.push(")[1].split("); if")[0])[
            "pois"
        ]
        for link in links:
            if "Opening" in link.p.text:
                continue
            if link.select_one("div.block-description").select("p")[-1].a:
                addr = list(
                    link.select_one("div.block-description")
                    .select("p")[-2]
                    .stripped_strings
                )
            else:
                addr = list(
                    link.select_one("div.block-description")
                    .select("p")[-1]
                    .stripped_strings
                )

            city = addr[1].split(",")[0].strip()
            zip_postal = (
                addr[1].split(",")[1].replace("\xa0", " ").strip().split(" ")[1].strip()
            )
            street_address = addr[0].strip()
            coord = _coord(street_address, city, zip_postal, locations)
            location_name = link.h2.text.strip()
            location_type = ""
            if "CLOSED UNTIL" in location_name:
                location_type = "temporarily closed"
            hours = [
                " ".join(hh.stripped_strings)
                for hh in link.select("div.block-description p span")
            ]
            phone = ""
            if _p(addr[-1]):
                phone = _p(addr[-1])
                del addr[-1]
            yield SgRecord(
                page_url=base_url,
                location_name=location_name.split("-")[0],
                street_address=street_address,
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
                phone=phone,
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
                raw_address=" ".join(addr).replace("\xa0", " "),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.GeoSpatialId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
