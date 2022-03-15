from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.diptyqueparis.com"
base_url = "https://www.diptyqueparis.com/en_us/stockists/ajax/stores?_=1626364672595"


def fetch_data():
    with SgRequests() as session:
        locations = session.get(base_url, headers=_headers).json()
        for _ in locations:
            street_address = _["address"]
            if _["address2"]:
                street_address += " " + _["address2"]
            page_url = ""
            if _["request_path"]:
                page_url = f"https://www.diptyqueparis.com/en_us/{_['request_path']}"
            state = ""
            if _.get("region"):
                state = _.get("region")
            hours = []
            if _["schedule"]:
                for hh in bs(_["schedule"], "lxml").stripped_strings:
                    if "こちら" in hh:
                        break
                    if "@" in hh or "現在" in hh or "opening" in hh.lower():
                        continue
                    hh = (
                        hh.split("当店")[0]
                        .replace("通常営業時間", "")
                        .replace("\\n", " ")
                        .replace("\n", "")
                        .replace("\r", " ")
                        .replace("※", "")
                        .replace("This boutique is open for services.", "")
                        .strip()
                    )
                    if not hh.strip():
                        continue
                    hours.append(hh)
            if hours and "temporarily not open" in hours[0]:
                hours = ["temporarily closed"]
            yield SgRecord(
                page_url=page_url,
                location_name=_["name"],
                street_address=street_address,
                city=_["city"],
                state=state,
                zip_postal=_["postcode"],
                latitude=_["latitude"],
                longitude=_["longitude"],
                country_code=_["country"],
                phone=_["phone"],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
            )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.LATITUDE,
                    SgRecord.Headers.LONGITUDE,
                    SgRecord.Headers.PAGE_URL,
                }
            )
        )
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
