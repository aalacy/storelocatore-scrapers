from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "https://www.naturiste.ca/"
    page_url = "https://www.naturiste.ca/apps/store-locator"
    base_url = "https://stores.boldapps.net/front-end/get_surrounding_stores.php?shop=lenaturiste.myshopify.com&latitude=46.8138783&longitude=-71.2079809&max_distance=0&limit=100&calc_distance=1"
    with SgRequests() as session:
        locations = session.get(base_url, headers=_headers).json()["stores"]
        for _ in locations:
            street_address = _["address"]
            if _["address2"]:
                street_address += f", {_['address2']}"
            yield SgRecord(
                page_url=page_url,
                store_number=_["store_id"],
                location_name=_["name"],
                street_address=street_address,
                city=_["city"],
                state=_["prov_state"],
                latitude=_["lat"],
                longitude=_["lng"],
                zip_postal=_["postal_zip"],
                country_code=_["country"],
                phone=_["phone"],
                locator_domain=locator_domain,
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
