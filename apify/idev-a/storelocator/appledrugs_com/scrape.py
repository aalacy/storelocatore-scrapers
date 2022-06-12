from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
import json
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.appledrugs.com"
base_url = "https://www.appledrugs.com/locate-us/"
map_url = "https://www.google.com/maps/d/u/0/embed?mid=1uHFqqo43RxtP-cUn7_oDVJP8WiIL4Z3w&hl=en&ll=38.277436637736734%2C-75.49934384999999&z=11"


def _p(val):
    return (
        val.split(":")[-1]
        .replace("(", "")
        .replace(")", "")
        .replace("+", "")
        .replace("-", "")
        .replace(".", " ")
        .replace("to", "")
        .replace(" ", "")
        .strip()
        .isdigit()
    )


def _coord(map_locations, addr):
    coord = ["", ""]
    for _ in map_locations[1][6][0][12][0][13][0]:
        if _[5][0][1][0].split(" ")[0].lower() in addr[0].lower():
            coord = _[1][0][0]
            break
    return coord


def fetch_data():
    with SgRequests() as session:
        res = session.get(map_url, headers=_headers)
        cleaned = (
            res.text.replace("\\t", " ")
            .replace("\t", " ")
            .replace("\\n]", "]")
            .replace("\n]", "]")
            .replace("\\n,", ",")
            .replace("\\n", "#")
            .replace('\\"', '"')
            .replace("\\u003d", "=")
            .replace("\\u0026", "&")
            .replace("\\", "")
            .replace("\xa0", " ")
        )
        map_locations = json.loads(
            cleaned.split('var _pageData = "')[1].split('";</script>')[0]
        )
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        locations = soup.select("div.entry table table tr")
        for _ in locations:
            if not _.strong:
                continue
            temp = list(_.select("td")[1].stripped_strings)
            hours = []
            for x in range(0, len(temp), 2):
                hours.append(f"{temp[x]} {temp[x+1]}")
            block = list(_.select("td")[0].stripped_strings)
            phone = ""
            addr = []
            for x, bb in enumerate(block):
                if _p(bb):
                    phone = bb.split(":")[-1].strip()
                    addr = block[1:x]
                    break
            coord = _coord(map_locations, addr)
            yield SgRecord(
                page_url=base_url,
                location_name=block[0],
                street_address=" ".join(addr[:-1]),
                city=addr[-1].split(",")[0].strip(),
                state=addr[-1].split(",")[1].strip().split(" ")[0],
                zip_postal=addr[-1].split(",")[1].strip().split(" ")[1],
                country_code="US",
                phone=phone,
                latitude=coord[0],
                longitude=coord[1],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours).replace("–", "-"),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.GeoSpatialId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
