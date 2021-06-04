from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests

_headers = {
    "accept": "application/json, text/javascript, */*; q=0.01",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "en-US,en;q=0.9,ko;q=0.8",
    "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
    "origin": "https://dagnyc.com",
    "referer": "https://dagnyc.com/",
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

data = {
    "app_key": "dagostino",
    "referrer": "https://dagnyc.com/my-store/store-locator",
    "utc": "1621124044662",
}


def fetch_data():
    locator_domain = "https://dagnyc.com/"
    base_url = "https://api.freshop.com/2/sessions/create"
    json_url = "https://api.freshop.com/1/stores?app_key=dagostino&has_address=true&limit=-1&token={}"
    with SgRequests() as session:
        token = session.post(base_url, headers=_headers, data=data).json()["token"]
        locations = session.get(json_url.format(token)).json()
        for _ in locations["items"]:
            yield SgRecord(
                page_url=_["url"],
                location_name=_["name"],
                store_number=_["store_number"],
                street_address=_["address_1"],
                city=_["city"],
                state=_["state"],
                zip_postal=_["postal_code"],
                latitude=_["latitude"],
                longitude=_["longitude"],
                country_code=_["country"],
                phone=_["phone"].split("\n")[1],
                locator_domain=locator_domain,
                hours_of_operation=_["hours_md"].split("\n")[0],
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
