from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgrequests import SgRequests

url = "https://crocs.locally.com/stores/conversion_data?has_data=true&company_id=1762&store_mode=&style=&color=&upc=&category=&inline=1&show_links_in_list=&parent_domain=&map_center_lat=40.87058088827031&map_center_lng=-74.54615122000206&map_distance_diag=3000&sort_by=proximity&no_variants=0&only_retailer_id=&dealers_company_id=&only_store_id=false&uses_alt_coords=false&q=false&zoom_level=6.727111799313498&lang=en-us"


def fetch_data():
    with SgRequests() as http:
        response = http.get(url)
        stores = response.json()["markers"]
        for store in stores:
            record = SgRecord(
                locator_domain="https://www.crocs.com/",
                page_url="fill me in",
                location_name=store["name"],
                street_address=store["address"],
                city=store["city"],
                state=store["state"],
                zip_postal=store["zip"],
                country_code=store["country"],
                store_number=store["id"],
                phone=store["phone"],
                location_type="fill me in",
                latitude=store["lat"],
                longitude=store["lng"],
                hours_of_operation="fill me in",
            )
            yield record


def scrape():
    with SgWriter(
        deduper=SgRecordDeduper(
            RecommendedRecordIds.StoreNumberId, duplicate_streak_failure_factor=-1
        )
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)


scrape()
