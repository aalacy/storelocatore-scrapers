from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "https://www.asics.com/"
    base_url = "https://asics.locally.com/stores/conversion_data?has_data=true&company_id=1682&store_mode=&style=&color=&upc=&category=&inline=1&show_links_in_list=&parent_domain=&map_center_lat=33.95973902795987&map_center_lng=-118.39490000000023&map_distance_diag=47.071173551117695&sort_by=proximity&no_variants=0&only_retailer_id=&dealers_company_id=&only_store_id=false&uses_alt_coords=false&q=false&zoom_level="
    with SgRequests() as session:
        locations = session.get(base_url, headers=_headers).json()
        for _ in locations["markers"]:
            page_url = f"https://asics.locally.com/conversion/location/store/{_['id']}?company_id={_['company_id']}&only_retailer_id="
            detail = session.get(page_url, headers=_headers).json()
            location_type = ""
            if "Temporarily Closed" in _["name"]:
                location_type = "Temporarily Closed"
            hours = []
            for hh in bs(detail["tabs_html"], "lxml").select(
                "div.store-hours  .store-hours-days .store-hours-day"
            ):
                hours.append(
                    f"{hh.select('span')[0].text}: {hh.select('span')[1].text}"
                )
            yield SgRecord(
                page_url=page_url,
                store_number=_["id"],
                location_name=_["name"].split("|")[0],
                street_address=_["address"],
                city=_["city"],
                state=_["state"],
                latitude=_["lat"],
                longitude=_["lng"],
                zip_postal=_["zip"],
                country_code=_["country"],
                phone=_["phone"],
                locator_domain=locator_domain,
                location_type=location_type,
                hours_of_operation="; ".join(hours),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
