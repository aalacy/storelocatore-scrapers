from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
import json

locator_domain = "https://oreck.com/"
base_url = "https://oreck.com/pages/find-your-local-store"
days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


def fetch_data():
    with SgRequests() as http:
        groups = json.loads(
            bs(http.get(base_url), "lxml")
            .select_one('main script[type="application/json"]')
            .text
        )["storeGroups"]
        for key, group in groups.items():
            for _ in group:
                hours = []
                for day in days:
                    day = day.lower()
                    if _.get(day):
                        hours.append(f"{day}: {_[day]}")

                location_type = "Authorized Dealers & Distributors"
                if _.get("t") == "F":
                    location_type = "Exclusive Oreck Dealers"
                elif _.get("t") == "S":
                    location_type = "Authorized Dealers & Distributors"
                yield SgRecord(
                    page_url=base_url,
                    location_name=_["n"] if _.get("n") else _["a1"],
                    street_address=_["a1"],
                    city=_["c"],
                    state=_["s"],
                    zip_postal=_["z"],
                    country_code="us",
                    phone=_["p"],
                    location_type=location_type,
                    latitude=_["lat"],
                    longitude=_["lng"],
                    locator_domain=locator_domain,
                    hours_of_operation="; ".join(hours),
                )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.STREET_ADDRESS,
                    SgRecord.Headers.CITY,
                    SgRecord.Headers.PHONE,
                }
            )
        )
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
