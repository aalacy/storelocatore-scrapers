from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.pandaexpress.com.gt"
base_url = "https://www.pandaexpress.com.gt/en/userlocation/searchbycoordinates?lat=34.0667&lng=-118.0833&desiredDistance=25&maxDistance=50&page=0&limit=25&hours=true&filters=%7B%22driveThru%22:false,%22orderOnline%22:false%7D"


def fetch_data():
    with SgRequests() as session:
        locations = session.get(base_url, headers=_headers).json()["List"]
        for _ in locations:
            hours = []
            for day, hh in (
                _.get("OperationalHours", {}).get("Normal", {}).get("Hours", {}).items()
            ):
                if not hh["StartTime"]:
                    break
                hours.append(f"{day}: {hh['StartTime']} - {hh['EndTime']}")
            location_type = ""
            if _["TemporarilyClosed"]:
                location_type = "Temporarily Closed"
            page_url = f"{locator_domain}/userlocation/{_['Id']}/{_['City']}/{_['Address'].replace(' ', '-')}"
            yield SgRecord(
                page_url=page_url.replace(",", ""),
                store_number=_["Id"],
                location_name=_["Name"],
                street_address=_["Address"],
                city=_["City"],
                state=_["State"],
                zip_postal=_["Zip"],
                latitude=_["Latitude"],
                longitude=_["Longitude"],
                country_code=_["Country"],
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
