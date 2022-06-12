from sgrequests import SgRequests
import json
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def fetch_data():
    url = "https://wafflehouse.locally.com/stores/conversion_data?has_data=true&company_id=117995&store_mode=&style=&color=&upc=&category=&inline=1&show_links_in_list=&parent_domain=&map_center_lat=32.77073337068231&map_center_lng=-96.79963000000077&map_distance_diag=2500&sort_by=proximity&no_variants=0&only_retailer_id=&dealers_company_id=&only_store_id=false&uses_alt_coords=false&q=false&zoom_level="
    r = session.get(url, headers=headers)
    for item in json.loads(r.content)["markers"]:
        name = item["name"]
        store = item["id"]
        add = item["address"]
        city = item["city"]
        state = item["state"]
        zc = item["zip"]
        phone = item["phone"]
        lat = item["lat"]
        lng = item["lng"]
        country = "US"
        website = "wafflehouse.com"
        typ = "Restaurant"
        hours = "Mon-Sun: 24 Hours"
        loc = "https://locations.wafflehouse.com/shop/" + str(store)
        if add[-1:] == "/" or add[-1:] == ",":
            add = add[:-1]
        yield SgRecord(
            locator_domain=website,
            page_url=loc,
            location_name=name,
            street_address=add,
            city=city,
            state=state,
            zip_postal=zc,
            country_code=country,
            phone=phone,
            location_type=typ,
            store_number=store,
            latitude=lat,
            longitude=lng,
            hours_of_operation=hours,
        )


def scrape():
    results = fetch_data()
    with SgWriter(deduper=SgRecordDeduper(RecommendedRecordIds.GeoSpatialId)) as writer:
        for rec in results:
            writer.write_row(rec)


scrape()
