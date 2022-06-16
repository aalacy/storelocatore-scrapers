from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://nealtire.com"
base_url = "https://nealtire.com/App_Services/Retailers.ashx?method=retailers&zip=47807&city=&state=&radius=9999999&measurement=0"
days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def fetch_data():
    with SgRequests() as session:
        locations = session.get(base_url, headers=_headers).json()
        for loc in locations:
            _ = loc["retailer"]
            addr = _["Location"]
            street_address = addr["Address1"]
            if addr["Address2"]:
                street_address += " " + addr["Address2"]
            hours = []
            if _["OpeningTimes"]:
                for day in days:
                    for key, hh in _["OpeningTimes"].items():
                        if key == day:
                            times = "closed"
                            if hh["IsOpen"]:
                                times = f"{hh['OpenHours']}:{hh['OpenMinutes']} - {hh['CloseHours']}:{hh['CloseMinutes']}"
                            hours.append(f"{key}: {times}")

            yield SgRecord(
                page_url=_["WebSiteUrl"],
                store_number=_["ID"],
                location_name=_["Name"],
                street_address=street_address,
                city=addr["City"],
                state=addr["State"],
                zip_postal=addr["PostCode"],
                latitude=addr["Latitude"],
                longitude=addr["Longitude"],
                country_code=addr["Country"],
                phone=_["Phone"],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
