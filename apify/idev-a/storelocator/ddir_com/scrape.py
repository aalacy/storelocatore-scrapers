from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.ddir.com"
base_url = "https://www.ddir.com/locations/"
json_url = "https://www.ddir.com/wp-json/wpgmza/v1/features/base64eJyrVkrLzClJLVKyUqqOUcpNLIjPTIlRsopRMoxR0gEJFGeUFni6FAPFomOBAsmlxSX5uW6ZqTkpELFapVoABU0Wug"


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


def _coord(name, locs):
    for loc in locs:
        if name.lower() in loc["title"].lower():
            return loc

    return {}


def fetch_data():
    with SgRequests() as session:
        res = session.get(base_url, headers=_headers).text
        links = bs(res, "lxml").select("div.block-grid div.block")
        locations = session.get(json_url, headers=_headers).json()["markers"]
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
            phone = ""
            if _p(addr[-1]):
                phone = _p(addr[-1])
                del addr[-1]

            z_s = addr[-1].split(",")[1].replace("\xa0", " ").strip().split()
            street_address = (
                " ".join(addr[:-1])
                .split("Drive-in")[-1]
                .replace("Crossroads Mall", "")
                .strip()
            )
            location_name = link.h2.text.strip()
            coord = _coord(location_name, locations)
            location_type = ""
            if "CLOSED UNTIL" in location_name:
                location_type = "temporarily closed"
            hours = [
                " ".join(hh.stripped_strings)
                for hh in link.select("div.block-description p span")
            ]

            if hours and "Temporarily closed" in hours[0]:
                hours = ["temporarily closed"]

            yield SgRecord(
                page_url=base_url,
                store_number=coord["id"],
                location_name=location_name.split("-")[0],
                street_address=street_address,
                state=z_s[0],
                city=addr[-1].split(",")[0].strip(),
                zip_postal=z_s[1],
                latitude=coord["lat"],
                longitude=coord["lng"],
                country_code="US",
                location_type=location_type,
                phone=phone,
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours).replace("NOW", "").strip(),
                raw_address=" ".join(addr)
                .replace("\xa0", " ")
                .split("Drive-in")[-1]
                .strip(),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.GeoSpatialId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
