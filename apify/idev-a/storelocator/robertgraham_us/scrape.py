from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

urls = [
    "https://stores.boldapps.net/front-end/get_surrounding_stores.php?shop=robertgraham.myshopify.com&latitude=36.09201990079786&longitude=-94.76647050000001&max_distance=0&limit=100&search_filter_12617=1&calc_distance=0",
    "https://stores.boldapps.net/front-end/get_surrounding_stores.php?shop=robertgraham.myshopify.com&latitude=34.07870927683378&longitude=-95.27935049999999&max_distance=0&limit=100&search_filter_12863=1&calc_distance=0",
]
base_url = "https://www.robertgraham.us/apps/storelocator/"
locator_domain = "https://www.robertgraham.us"


def fetch_data():
    with SgRequests() as session:
        for url in urls:
            locations = session.get(url, headers=_headers).json()["stores"]
            for _ in locations:
                yield SgRecord(
                    page_url=base_url,
                    store_number=_["store_id"],
                    location_name=_["name"],
                    street_address=_["address"],
                    city=_["city"],
                    state=_["prov_state"],
                    zip_postal=_["postal_zip"],
                    country_code=_["country"],
                    latitude=_["lat"],
                    longitude=_["lng"],
                    phone=_["phone"],
                    location_type=_["group_name"],
                    locator_domain=locator_domain,
                    hours_of_operation=_["hours"],
                )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
