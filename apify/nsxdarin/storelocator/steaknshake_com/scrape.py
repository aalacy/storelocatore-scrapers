from sgrequests import SgRequests
import json
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def fetch_data():
    url = "https://www.steaknshake.com/wp-admin/admin-ajax.php?action=get_location_data_from_plugin"
    r = session.get(url, headers=headers)
    for item in json.loads(r.content):
        store = item["brandChainId"]
        name = item["name"]
        if "phone1" in item:
            phone = item["phone1"]
        else:
            phone = "<MISSING>"
        purl = "https://www.steaknshake.com/locations/" + item["slug"]
        try:
            hours = (
                str(item)
                .split("]}, 'hours': {'")[1]
                .split("}}]}")[0]
                .replace("', '", "; ")
                .replace("'", "")
            )
        except:
            hours = "<MISSING>"
        add = item["address"]["address1"]
        if "address2" in item["address"]:
            add = add + " " + item["address"]["address2"]
        city = item["address"]["city"]
        zc = item["address"]["zip"]
        state = item["address"]["region"]
        country = item["address"]["country"]
        website = "steaknshake.com"
        typ = "Restaurant"
        if "loc" in item["address"]:
            lat = item["address"]["loc"][1]
            lng = item["address"]["loc"][0]
        else:
            lat = "<MISSING>"
            lng = "<MISSING>"
        if phone == "":
            phone = "<MISSING>"
        if lat == "":
            lat = "<MISSING>"
            lng = "<MISSING>"
        yield SgRecord(
            locator_domain=website,
            page_url=purl,
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
    with SgWriter(deduper=SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        for rec in results:
            writer.write_row(rec)


scrape()
