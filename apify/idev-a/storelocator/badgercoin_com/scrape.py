from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from bs4 import BeautifulSoup as bs

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.badgercoin.com"
base_url = "https://www.badgercoin.com/locations"
json_url = "https://api.storepoint.co/v1/{}/locations?lat=40.8&long=-73.97&radius=20000"


def fetch_data():
    with SgRequests() as session:
        key = bs(session.get(base_url, headers=_headers).text, "lxml").select_one(
            "div#storepoint-container"
        )["data-map-id"]
        locations = session.get(json_url.format(key), headers=_headers).json()[
            "results"
        ]["locations"]
        for _ in locations:
            addr = _["streetaddress"].split(",")
            state = zip_postal = ""
            s_z = addr[-2].strip().split(" ")
            if len(s_z) > 2:
                state = " ".join(addr[-2].strip().split(" ")[:-2])
                zip_postal = " ".join(addr[-2].strip().split(" ")[-2:])
            else:
                state = s_z[0]
                zip_postal = s_z[-1]
            hours = []
            hours.append(f"Mon: {_['monday']}")
            hours.append(f"Tue: {_['tuesday']}")
            hours.append(f"Wed: {_['wednesday']}")
            hours.append(f"Thu: {_['tuesday']}")
            hours.append(f"Fri: {_['friday']}")
            hours.append(f"Sat: {_['saturday']}")
            hours.append(f"Sun: {_['sunday']}")
            yield SgRecord(
                page_url="https://www.badgercoin.com/locations",
                store_number=_["id"],
                location_name=_["name"],
                street_address=" ".join(addr[:-3]),
                city=addr[-3].strip(),
                state=state,
                zip_postal=zip_postal,
                latitude=_["loc_lat"],
                longitude=_["loc_long"],
                country_code="CA",
                phone=_["phone"],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
                raw_address=_["streetaddress"],
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
