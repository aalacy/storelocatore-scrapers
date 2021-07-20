from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.buy-low.com"
base_url = "https://storeportal.buy-low.com/wp-admin/admin-ajax.php/admin-ajax.php?action=buylow_get_store_list&banner=buy-low&timezone=America/Los_Angeles"
page_url = "https://www.buy-low.com/stores/"


def fetch_data():
    with SgRequests() as session:
        locations = session.get(base_url, headers=_headers).json()
        for _ in locations:
            phone = ""
            if _["store_details"]["phone_numbers"]:
                phone = _["store_details"]["phone_numbers"][0]["phone_number"]
            hours = []
            for day, hh in _["store_hours"].items():
                hours.append(f"{day}: {hh['start']}-{hh['Close']}")
            yield SgRecord(
                page_url=page_url,
                store_number=_["storeNumber"],
                location_name=_["storeName"],
                street_address=_["store_details"]["address"],
                city=_["store_details"]["city"],
                state=_["store_details"]["province"],
                zip_postal=_["store_details"]["postal_code"],
                latitude=_["map_data"]["latitude"],
                longitude=_["map_data"]["longitude"],
                country_code="CA",
                phone=phone,
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
