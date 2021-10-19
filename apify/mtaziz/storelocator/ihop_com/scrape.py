import json
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup


API_ENDPOINT_URL = (
    "https://maps.restaurants.ihop.com/api/getAsyncLocations?search=75022&level=domain"
    "&template=domain&limit=5000&radius=5000"
)
DOMAIN = "ihop.com"
logger = SgLogSetup().get_logger("ihop_com")
MISSING = SgRecord.MISSING
headers = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36",
}


def fetch_data(sgw: SgWriter, http: SgRequests):
    r = http.get(API_ENDPOINT_URL, headers=headers)
    js_init = r.json()["maplist"]
    line = "[" + js_init.split('<div class="tlsmap_list">')[1].split(",</div>")[0] + "]"
    js = json.loads(line)
    js_markers = r.json()["markers"]
    for idx, j in enumerate(js):
        page_url = j.get("url")
        location_name = j.get("location_name") or MISSING
        logger.info(f"[{idx}] Location Name: {location_name}")
        street_address = f"{j.get('address_1')} {j.get('address_2')}".strip() or MISSING
        city = j.get("city") or MISSING
        state = j.get("big_region") or MISSING
        postal = j.get("post_code") or MISSING
        country_code = j.get("country") or MISSING
        store_number = j.get("fid") or MISSING
        phone = j.get("local_phone") or MISSING
        latitude = js_markers[idx].get("lat") or MISSING
        longitude = js_markers[idx].get("lng") or MISSING
        location_type = j.get("location_type") or MISSING
        _tmp = []
        tmp_js = json.loads(j.get("hours_sets:primary")).get("days", {})
        for day in tmp_js.keys():
            line = tmp_js[day]
            if len(line) == 1:
                start = line[0]["open"]
                close = line[0]["close"]
                _tmp.append(f"{day} {start} - {close}")
            else:
                _tmp.append(f"{day} Closed")
        if _tmp:
            hours_of_operation = "; ".join(_tmp)
        else:
            hours_of_operation = MISSING

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code=country_code,
            store_number=store_number,
            phone=phone,
            location_type=location_type,
            latitude=latitude,
            longitude=longitude,
            locator_domain=DOMAIN,
            hours_of_operation=hours_of_operation,
            raw_address=MISSING,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    with SgRequests(proxy_country="us") as http:
        with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
            fetch_data(writer, http)
