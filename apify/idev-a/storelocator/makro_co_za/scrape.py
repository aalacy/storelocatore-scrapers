from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.makro.co.za"
base_url = "https://www.makro.co.za/store-finder?q=&page={}&latitude=-25.9678718&longitude=28.0208121&posType="


def fetch_data():
    with SgRequests() as session:
        page = 0
        while True:
            try:
                res = session.get(base_url.format(page), headers=_headers)
                if res.status_code == 500:
                    continue
                locations = session.get(base_url.format(page), headers=_headers).json()[
                    "data"
                ]
            except:
                break
            page += 1
            for _ in locations:
                if _["type"] in ["Makro Online Store", "Makro General Enquiries"]:
                    continue
                street_address = _["line1"]
                if _["line2"]:
                    street_address += " " + _["line2"]
                page_url = locator_domain + _["url"]
                hours = []
                for day, hh in _.get("openings", {}).items():
                    hours.append(f"{day}: {hh}")

                if (
                    "Online Store" in _["displayName"]
                    or "General Enquiries" in _["displayName"]
                ):
                    continue

                yield SgRecord(
                    page_url=page_url,
                    location_name=_["displayName"],
                    street_address=street_address.replace("&amp;", "&"),
                    city=_["town"],
                    state=_["province"],
                    zip_postal=_["postalCode"],
                    latitude=_["latitude"],
                    longitude=_["longitude"],
                    country_code="South Africa",
                    phone=_["phone"].replace("&nbsp;", " "),
                    location_type=_["type"],
                    locator_domain=locator_domain,
                    hours_of_operation="; ".join(hours),
                )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
