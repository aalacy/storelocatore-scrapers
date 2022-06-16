from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import parse_address_intl

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.pandaexpress.ae"
base_url = "https://www.pandaexpress.ae/en/userlocation/searchbycoordinates?lat=34.0667&lng=-118.0833&desiredDistance=25&maxDistance=50&page=0&limit=25&hours=true&filters=%7B%7D"

days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


def fetch_data():
    with SgRequests() as session:
        locations = session.get(base_url, headers=_headers).json()["List"]
        for _ in locations:
            hours = []
            for day, hh in (
                _.get("OperationalHours", {}).get("Normal", {}).get("Hours", {}).items()
            ):
                if not hh["StartTime"]:
                    times = "Closed"
                else:
                    times = f"{hh['StartTime']} - {hh['EndTime']}"
                hours.append(f"{day}: {times}")
            if not hours and _.get("OperationalHours", {}).get("Normal", {}).get(
                "HasHours"
            ):
                for day in days:
                    hours.append(f"{day}: closed")
            location_type = ""
            if _["TemporarilyClosed"]:
                location_type = "Temporarily Closed"
            page_url = f"https://www.pandaexpress.ae/userlocation/{_['Id']}/{_['City']}/{_['Address'].replace(' ', '-')}"
            addr = parse_address_intl(_["Address"])
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2
            if not street_address:
                street_address = _["Address"]
            state = _["State"]
            city = _["City"]
            if addr.city:
                city = addr.city
            if addr.state:
                state = addr.state
            country_code = _["Country"]
            if addr.country:
                country_code = addr.country
            if city == "Riyadh":
                country_code = "SA"
            yield SgRecord(
                page_url=page_url,
                store_number=_["Id"],
                location_name=_["Name"],
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=_["Zip"],
                latitude=_["Latitude"],
                longitude=_["Longitude"],
                country_code=country_code,
                phone=_["Phone"],
                locator_domain=locator_domain,
                location_type=location_type,
                hours_of_operation="; ".join(hours),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
