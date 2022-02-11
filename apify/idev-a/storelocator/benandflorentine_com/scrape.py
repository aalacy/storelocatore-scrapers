from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
import json
from bs4 import BeautifulSoup as bs
from sgpostal.sgpostal import parse_address_intl
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://benetflorentine.com"
base_url = "https://benetflorentine.com/en/restaurants/"


def _p(val):
    return (
        val.replace("(", "")
        .replace(")", "")
        .replace("+", "")
        .replace("-", "")
        .replace(".", " ")
        .replace("to", "")
        .replace(" ", "")
        .strip()
        .isdigit()
    )


def fetch_data():
    with SgRequests() as session:
        locations = json.loads(
            session.get(base_url, headers=_headers)
            .text.split("var maplistScriptParamsKo =")[1]
            .split("/* ]]> */")[0]
            .strip()[:-1]
        )["KOObject"][0]["locations"]
        for x, _ in enumerate(locations):
            blocks = [
                list(p.stripped_strings)
                for p in bs(_["description"], "lxml").select("p")
                if p.text.strip()
            ]
            if "View location detail" in blocks[-1]:
                del blocks[-1]
            phone = ""
            if _p(" ".join(blocks[-1])):
                phone = " ".join(blocks[-1])
                del blocks[-1]
            hours = []
            for hh in blocks[-1]:
                if "temporarily closed" in hh.lower():
                    hours = ["Temporarily closed"]
                    break
                if "reopening" in hh.lower():
                    break
                if "take-out" in hh.lower() or "open" in hh.lower():
                    continue
                hours.append(hh)
            raw_address = " ".join(blocks[0]).replace(".", ". ")
            addr = parse_address_intl(raw_address)
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2
            state = addr.state
            zip_postal = addr.postcode
            _addr = " ".join(blocks[0])
            if not state:
                state = _addr.split(",")[1].strip().split(" ")[0]
            if not zip_postal:
                if len(_addr.split(",")) == 3:
                    zip_postal = _addr.split(",")[-1].strip()
                else:
                    zip_postal = " ".join(_addr.split(",")[1].strip().split(" ")[1:])
            yield SgRecord(
                page_url=base_url,
                store_number=x,
                location_name=_["title"],
                street_address=street_address,
                city=addr.city or _["title"],
                state=state.replace("Local", ""),
                zip_postal=zip_postal,
                latitude=_["latitude"],
                longitude=_["longitude"],
                country_code="CA",
                phone=phone,
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
                raw_address=raw_address,
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
