from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import json
from bs4 import BeautifulSoup as bs

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.kfcjamaica.com"
base_url = "https://www.kfcjamaica.com/locations"


def _city(val):
    city = val
    cc = val.lower().strip()
    if (
        "street" in cc
        or "avenue" in cc
        or "boulevard" in cc
        or "ironshore" in cc
        or "hall" in cc
        or cc.endswith("rd")
        or cc.endswith("st")
        or "blvd" in cc
        or "center" in cc
        or "centre" in cc
        or "drive" in cc
        or "road" in cc
        or "parish" in cc
        or "mar" in cc
        or "catherine" in cc
        or "james" in cc
        or "pen" in cc
        or "elizabeth" in cc
        or "plaza" in cc
    ):
        city = ""
    return city


def fetch_data():
    with SgRequests() as session:
        locations = json.loads(
            bs(session.get(base_url, headers=_headers).text, "lxml")
            .find("script", type="application/json")
            .string
        )["dexp_gmap_locations"]
        for _ in locations:
            _addr = _["address"]
            if "Jamaica" in _addr:
                _addr = _addr.replace("Jamaica", "").strip()
            if _addr.endswith(","):
                _addr = _addr[:-1].strip()
            city = ""
            if len(_addr.split(",")) > 1:
                city = _city(_addr.split(",")[-1].strip())
            if "Constant Spring" in _addr:
                city = "Constant Spring"
            if not city:
                city = _city(_addr.split(" ")[-1])
            if not city:
                street_address = _addr
            else:
                street_address = _addr.split(city)[0].strip()

            if street_address.endswith(","):
                street_address = street_address[:-1]
            page_url = f"https://www.kfcjamaica.com/locations/location/{_['id']}"
            sp1 = bs(session.get(page_url, headers=_headers).text, "lxml")
            hours = [
                ": ".join(hh.stripped_strings)
                for hh in sp1.select("div.dexp-lm-open-hours div.open-hour-item")
            ]
            if "center" in city.lower():
                import pdb

                pdb.set_trace()
            yield SgRecord(
                page_url=page_url,
                store_number=_["id"],
                location_name=_["title"],
                street_address=street_address,
                city=city,
                latitude=_["latitude"],
                longitude=_["longitude"],
                country_code="Jamaica",
                phone=_["phone"],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
                raw_address=_addr + ", Jamaica",
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
