import json
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgzip.dynamic import SearchableCountries, DynamicGeoSearch


def fetch_data(sgw: SgWriter):
    search = DynamicGeoSearch(
        expected_search_radius_miles=1000, country_codes=SearchableCountries.ALL
    )
    for lat, lng in search:
        api = f"https://maps.stores.claires.com/api/getAsyncLocations?template=searchicing&level=search&limit=*&radius=*&lat={lat}&lng={lng}"
        r = session.get(api, headers=headers)
        js_init = r.json()["maplist"]
        js = json.loads("[" + js_init.split(">")[1].split("<")[0][:-1] + "]")

        for j in js:
            page_url = j.get("url")
            location_name = j.get("location_name")
            street_address = f"{j.get('address_1')} {j.get('address_2') or ''}".strip()
            city = j.get("city")
            state = j.get("region")
            postal = j.get("post_code")
            country_code = j.get("country")
            store_number = str(j.get("fid")).replace("na", "")
            phone = j.get("local_phone")
            latitude = j.get("lat")
            longitude = j.get("lng")

            _tmp = []
            tmp_js = json.loads(j.get("hours_sets:primary")).get("days") or {}
            for day in tmp_js.keys():
                line = tmp_js[day]
                if len(line) == 1:
                    start = line[0]["open"]
                    close = line[0]["close"]
                    _tmp.append(f"{day} {start} - {close}")
                else:
                    _tmp.append(f"{day} Closed")

            hours_of_operation = ";".join(_tmp)

            row = SgRecord(
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=postal,
                country_code=country_code,
                latitude=latitude,
                longitude=longitude,
                phone=phone,
                store_number=store_number,
                locator_domain=locator_domain,
                hours_of_operation=hours_of_operation,
            )

            sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.icing.com/"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:97.0) Gecko/20100101 Firefox/97.0",
    }
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(
            RecommendedRecordIds.PageUrlId, duplicate_streak_failure_factor=-1
        )
    ) as writer:
        fetch_data(writer)
