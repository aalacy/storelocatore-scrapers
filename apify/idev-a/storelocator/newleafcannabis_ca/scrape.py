from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
import json
import re
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

days = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]

states = {
    "A": "NL",
    "B": "NS",
    "C": "PE",
    "E": "NB",
    "G": "QC",
    "H": "QC",
    "J": "QC",
    "K": "ON",
    "L": "ON",
    "M": "ON",
    "N": "ON",
    "P": "ON",
    "R": "MB",
    "S": "SK",
    "T": "AB",
    "V": "BC",
    "X": "NU/NT",
    "Y": "YT",
}
locator_domain = "https://cannacabana.com"
base_url = "https://cannacabana.com/a/stores/"


def _loc(locs, name):
    for loc in locs:
        if name.split("(")[0].strip() == list(loc.h3.stripped_strings)[0]:
            return loc


def fetch_data():
    with SgRequests() as session:
        res = session.get(base_url, headers=_headers).text
        locs = bs(res, "lxml").select("div.wrapper div.grid div.col-4_xs-12")
        locations = json.loads(
            res.split("window['all_stores'] =")[1].split("loadStores()")[0].strip()[:-1]
        )
        for _ in locations:
            if "Online" in _["title"]:
                continue

            addr = _["address"]
            street_address = addr["street1"].replace("–", "-")
            if addr.get("street2"):
                street_address += " " + addr["street2"]

            zip_postal = addr["zip"]
            if zip_postal and zip_postal.split()[0] == "ON":
                zip_postal = " ".join(zip_postal.split()[1:])
            hours = []
            temp = ", ".join(bs(_.get("hours"), "lxml").stripped_strings).split(",")
            for hh in temp:
                if hh.strip() and (
                    hh.strip().startswith("Temporary")
                    or hh.strip().startswith("Special")
                    or "/" in hh.strip().split()[0]
                ):
                    break
                hours.append(hh.split("Temporary")[0].strip())

            loc = _loc(locs, _["title"])
            phone = (
                loc.find("i", {"class", re.compile(r"bi-telephone")})
                .find_next_sibling()
                .text.strip()
            )
            yield SgRecord(
                page_url=locator_domain + loc.select_one("a.btn--solo-orange")["href"],
                location_name=_["title"],
                street_address=street_address,
                city=addr["city"],
                state=addr["province"],
                latitude=addr["latitude"],
                longitude=addr["longitude"],
                zip_postal=zip_postal,
                country_code=addr["country"],
                phone=phone,
                locator_domain=locator_domain,
                hours_of_operation=", ".join(hours).replace("|", ";"),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.GeoSpatialId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
