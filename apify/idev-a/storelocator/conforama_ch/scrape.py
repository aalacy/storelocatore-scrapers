from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.conforama.ch/"
base_url = "https://api.conforama.ch/occ/v2/conforama/stores?fields=stores(name%2CdisplayName%2CformattedDistance%2CopeningHours(weekDayOpeningList(FULL)%2CspecialDayOpeningList(FULL))%2CgeoPoint(latitude%2Clongitude)%2Caddress(line1%2Cline2%2Ctown%2Cregion(FULL)%2CpostalCode%2Cphone%2Ccountry%2Cemail)%2C%20features)%2Cpagination(DEFAULT)%2Csorts(DEFAULT)&query=&pageSize=-1&lang=de&curr=CHF"


def fetch_data():
    with SgRequests() as session:
        locations = session.get(base_url, headers=_headers).json()["stores"]
        for _ in locations:
            addr = _["address"]
            street_address = addr["line1"]
            if addr.get("line2"):
                street_address += " " + addr.get("line2")
            if "Mock" in street_address:
                continue
            hours = []
            for hh in _["openingHours"]["weekDayOpeningList"]:
                if hh["closed"]:
                    times = "closed"
                else:
                    times = f"{hh['openingTime']['formattedHour']} - {hh['closingTime']['formattedHour']}"
                hours.append(f"{hh['weekDay']} {times}")
            page_url = (
                f"https://www.conforama.ch/de/store-finder/country/CH/{_['name']}"
            )
            zip_postal = addr["postalCode"]
            if zip_postal == "0000":
                zip_postal = ""
            latitude = _["geoPoint"]["latitude"]
            longitude = _["geoPoint"]["longitude"]
            if latitude == 0.0:
                latitude = ""
            if longitude == 0.0:
                longitude = ""
            yield SgRecord(
                page_url=page_url,
                location_name=_["name"],
                street_address=street_address,
                city=addr["town"],
                zip_postal=zip_postal,
                latitude=latitude,
                longitude=longitude,
                country_code="CH",
                phone=addr.get("phone"),
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
