from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

_headers = {
    "accept": "*/*",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "en-US,en;q=0.9",
    "authorization": "Bearer undefined",
    "content-type": "application/json;charset=UTF-8",
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.aceuae.com"
json_url = "https://webapi.aceuae.com/api/v1/stores/store-locator"
days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
token_url = "https://cas.aceuae.com/auth/v1/token"


def fetch_data():
    with SgRequests() as http:
        data = {
            "serviceUrl": "webapi.aceuae.com",
            "grantType": "Anonymous",
            "appId": "MozCom",
        }
        _headers["authorization"] = (
            "Bearer "
            + http.post(token_url, headers=_headers, json=data).json()["data"]["token"]
        )
        locations = http.get(json_url, headers=_headers).json()["data"]
        for _ in locations:
            addr = _["contactInfo"]
            street_address = addr["addressLine1"]
            if addr["addressLine2"]:
                street_address += " " + addr["addressLine2"]
            temp = {}
            hours = []
            for day, hh in _["workingHours"].items():
                temp[day] = hh
            for day in days:
                hours.append(f"{day}: {temp.get(day)}")
            page_url = locator_domain + "/en-ae/" + _["name"].lower().replace(" ", "-")
            yield SgRecord(
                page_url=page_url,
                store_number=_["storeId"],
                location_name=_["name"],
                street_address=street_address,
                city=addr["city"],
                state=addr.get("state"),
                zip_postal=addr.get("postCode"),
                latitude=addr["location"]["lat"],
                longitude=addr["location"]["lng"],
                country_code=addr["country"],
                phone=addr["telephone1"],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
