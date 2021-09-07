from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.soletrader.co.uk"
base_url = "https://www.soletrader.co.uk/modules/staff/ajax.aspx?Longitude=-0.137502&Latitude=51.497662&RangeInMiles=9999&F=GetClosestLocations"


def fetch_data():
    with SgRequests() as session:
        data = ""
        locations = session.get(base_url, headers=_headers).json()
        for _ in locations:
            phone = _["Phone"]
            if phone == "N/A":
                phone = ""
            hours = []
            for hh in _.get("OpenHours", []):
                hours.append(f"{hh['DayName']}: {hh['From']} - {hh['To']}")
            page_url = locator_domain + _["CustomUrl"]
            yield SgRecord(
                page_url=page_url,
                store_number=_["DealerId"],
                location_name=_["Address1"],
                street_address=_["Address2"],
                city=_["City"],
                state=_.get("State"),
                zip_postal=_["Zip"],
                latitude=_["Latitude"],
                longitude=_["Longitude"],
                country_code="UK",
                phone=phone,
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
