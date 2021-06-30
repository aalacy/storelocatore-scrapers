from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests

_headers = {
    "accept": "application/json, text/javascript, */*; q=0.01",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "en-US,en;q=0.9,ko;q=0.8",
    "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
    "origin": "https://www.huntington.com",
    "referer": "https://www.huntington.com/branchlocator",
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

data = {
    "longitude": "-83.0008326",
    "latitude": "39.9610692",
    "typeFilter": "1,2",
    "envelopeFreeDepositsFilter": "false",
    "timeZoneOffset": "420",
    "scController": "GetLocations",
    "scAction": "GetLocationsList",
}

types = {"1": "branch", "2": "ATM"}


def fetch_data():
    locator_domain = "https://www.huntington.com/"
    base_url = "https://www.huntington.com/post/GetLocations/GetLocationsList"
    with SgRequests() as session:
        locations = session.post(base_url, headers=_headers, data=data).json()
        for _ in locations["features"]:
            store_number = _["properties"]["LocID"].replace("bko", "")
            page_url = base_url
            if _["properties"]["LocType"] == "1":
                page_url = f"https://www.huntington.com/Community/branch-info?locationId={store_number}"
            hours = []
            hours.append(f"Monday: {_['properties']['MondayLobbyHours']}")
            hours.append(f"Tuesday: {_['properties']['TuesdayLobbyHours']}")
            hours.append(f"Wednesday: {_['properties']['WednesdayLobbyHours']}")
            hours.append(f"Thursday: {_['properties']['ThursdayLobbyHours']}")
            hours.append(f"Friday: {_['properties']['FridayLobbyHours']}")
            hours.append(f"Saturday: {_['properties']['SaturdayLobbyHours']}")
            hours.append(f"Sunday: {_['properties']['SundayLobbyHours']}")
            yield SgRecord(
                page_url=page_url,
                store_number=store_number,
                location_name=_["properties"]["LocName"],
                street_address=_["properties"]["LocStreet"],
                city=_["properties"]["LocCity"],
                state=_["properties"]["LocState"],
                zip_postal=_["properties"]["LocZip"],
                latitude=_["geometry"]["coordinates"][1],
                longitude=_["geometry"]["coordinates"][0],
                country_code="US",
                location_type=types[_["properties"]["LocType"]],
                phone=_["properties"]["LocPhone"],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
