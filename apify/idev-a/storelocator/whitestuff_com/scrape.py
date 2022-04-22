from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.whitestuff.com"
base_url = "https://www.whitestuff.com/INTERSHOP/rest/WFS/WhiteStuff-UK-Site/-;loc=en_GB/stores"
days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]


def _p(val):
    if (
        val
        and val.split("Ex")[0]
        .replace("(", "")
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
        locations = session.get(base_url, headers=_headers).json()["elements"]
        for _ in locations:
            hours = ""
            for day, times in _["customAttributes"].items():
                _day = day.strip().lower()
                if _day in days and _day not in hours:
                    hours += f"{_day}: {times};"
            if hours:
                hours = hours[:-1]
            street_address = _["address"]
            if _.get("address2"):
                street_address += " " + _["address2"]
            yield SgRecord(
                page_url="https://www.whitestuff.com/action/ViewStoreFinder-Start",
                location_name=_["name"],
                street_address=street_address,
                city=_["city"],
                zip_postal=_["postalCode"],
                latitude=_["customAttributes"]["latitude"],
                longitude=_["customAttributes"]["longitude"],
                country_code=_["country"],
                phone=_p(_.get("phoneBusiness")),
                locator_domain=locator_domain,
                hours_of_operation=hours,
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.GeoSpatialId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
