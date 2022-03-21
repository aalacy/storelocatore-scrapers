from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "https://www.qehomelinens.com"
    base_url = "https://lambda.ribon.ca/api/v1/x79kxz20uq/services/tokens"
    with SgRequests() as session:
        token = ""
        for dd in session.get(base_url, headers=_headers).json():
            if dd["name"] == "data":
                token = dd["token"]

        if token:
            url = (
                f"https://data.ribon.ca/api/v1/data/store_info?token={token}&debug=bapo"
            )
            locations = session.get(url, headers=_headers).json()
            for _ in locations:
                if not _["url_name"]:
                    continue
                page_url = f"https://www.qehomelinens.com/store/{_['url_name']}/"
                location_type = ""
                if "Due to lockdown, we'll be closed starting" in _["store_note"]:
                    location_type = "closed"
                hours = []
                if "Temporarily Closed" in _["monday_hours"]:
                    location_type = "Temporarily Closed"
                else:
                    hours.append(f"Mon: {_['monday_hours']}")
                    hours.append(f"Tue: {_['tuesday_hours']}")
                    hours.append(f"Wed: {_['wednesday_hours']}")
                    hours.append(f"Thu: {_['thursday_hours']}")
                    hours.append(f"Fri: {_['friday_hours']}")
                    hours.append(f"Sat: {_['saturday_hours']}")
                    hours.append(f"Sun: {_['sunday_hours']}")
                yield SgRecord(
                    page_url=page_url,
                    store_number=_["store_id"],
                    location_name=_["name"],
                    street_address=_["address"],
                    city=_["city"],
                    state=_["province"],
                    zip_postal=_["zip"],
                    latitude=_["lat"],
                    longitude=_["lng"],
                    country_code=_["country"],
                    phone=_["phone"],
                    location_type=location_type,
                    locator_domain=locator_domain,
                    hours_of_operation="; ".join(hours),
                )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
