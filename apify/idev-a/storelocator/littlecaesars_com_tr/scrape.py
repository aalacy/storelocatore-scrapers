from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import json
from sgscrape.sgpostal import parse_address_intl

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.littlecaesars.com.tr"
base_url = "https://www.littlecaesars.com.tr/musteri-destegi/harita"
days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


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
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        locations = json.loads(soup.find("script", type="application/json").string)[
            "props"
        ]["initialProps"]["ssrProps"]["addressData"]["restaurants"]
        for _ in locations:
            page_url = f"https://www.littlecaesars.com.tr/sube/adana/{_['name'].replace(' ', '-')}/{_['id']}"
            hours = []
            for hh in _.get("storeWorkingTimes", []):
                hours.append(
                    f"{days[hh['dayOfWeek']]}: {hh['startTime'].split()[-1]} - {hh['endTime'].split()[-1]}"
                )
            raw_address = (
                _["address"].replace("\n", " ").replace("\r", "").replace("\t", "")
            )
            addr = parse_address_intl(raw_address + ", Turkey")
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2
            yield SgRecord(
                page_url=page_url,
                store_number=_["id"],
                location_name=_["name"],
                street_address=street_address,
                city=_["townName"],
                state=addr.state,
                zip_postal=addr.postcode,
                country_code="Turkey",
                phone=_p(_["phone"]),
                latitude=_["latitude"],
                longitude=_["longitude"],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
                raw_address=raw_address,
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
