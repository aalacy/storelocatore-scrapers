from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import dirtyjson as json
from bs4 import BeautifulSoup as bs
import re
from sgscrape.sgpostal import parse_address_intl

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.spar.ie"
base_url = "https://www.spar.ie/find-your-nearest-spar/"


def fetch_data():
    with SgRequests() as http:
        locations = (
            bs(http.get(base_url, headers=_headers).text, "lxml")
            .find("script", string=re.compile(r"var storeDetailArr"))
            .string.split("var storeDetailArr =")[1]
            .split("new Array(")[1]
            .split(");")[0]
            .strip()
            .split("},")
        )
        for x in range(len(locations)):
            loc = locations[x]
            _ = json.loads(re.sub("", "", loc) + "}")
            coord = _["geocode"].split(",")
            if len(coord) == 1:
                coord = coord[0].split("-")
                coord[1] = "-" + coord[1]
            raw_address = (
                " ".join(bs(_["address"], "lxml").stripped_strings)
                .replace("&nbsp;", " ")
                .strip()
            )
            street_address = zip_postal = city = ""
            if raw_address:
                addr = parse_address_intl(raw_address)
                street_address = addr.street_address_1 or ""
                if addr.street_address_2:
                    street_address += " " + addr.street_address_2
                if raw_address.split(_["county"])[-1].strip():
                    zip_postal = raw_address.split(_["county"])[-1].strip().split()[-1]
                city = addr.city
            if not city:
                city = _["town"]
            if street_address:
                street_address = (
                    street_address.replace("Spar Express", "")
                    .replace("Spar", "")
                    .strip()
                )
            if zip_postal and zip_postal.isdigit():
                zip_postal = ""
            if city and city == zip_postal:
                city = ""
            yield SgRecord(
                page_url=base_url,
                location_name=_["name"].replace("&#8217;", "'"),
                street_address=street_address,
                city=city,
                state=_["county"],
                zip_postal=zip_postal.replace(",", "").strip(),
                latitude=coord[0].replace(",", ".").strip(),
                longitude=coord[1].replace(",", ".").strip(),
                country_code="Ireland",
                phone=_["phone"],
                locator_domain=locator_domain,
                raw_address=raw_address.replace("Spar Express", "")
                .replace("Spar", "")
                .strip(),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.GeoSpatialId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
