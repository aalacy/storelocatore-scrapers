import json
from datetime import datetime, timedelta
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgzip.dynamic import SearchableCountries, DynamicZipSearch


def override(js):
    days = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday",
    ]
    j = (
        json.loads(js.get("hours_sets:primary"))
        .get("children", {})
        .get("holiday")
        .get("overrides")
    )
    date_list = [
        (datetime.today() + timedelta(days=x)).date().strftime("%Y-%m-%d")
        for x in range(7)
    ]

    _tmp = []
    for date in date_list:
        day = days[datetime.strptime(date, "%Y-%m-%d").weekday()]
        if type(j.get(date)) == list:
            time = f"{j[date][0].get('open')} - {j[date][0].get('close')}"
            _tmp.append(f"{day}: {time}")
        else:
            _tmp.append(f"{day}: Closed")

    hoo = ";".join(_tmp)
    return hoo


def fetch_data(sgw: SgWriter):
    search = DynamicZipSearch(
        country_codes=[SearchableCountries.BRITAIN], expected_search_radius_miles=500
    )
    for _z in search:
        api = f"https://maps.pandora.net/api/getAsyncLocations?search={_z}&level=domain&template=domain&limit=1000&radius=1000"
        r = session.get(api, headers=headers)
        js_init = r.json()["maplist"]
        try:
            line = (
                "["
                + js_init.split('<div class="tlsmap_list">')[1].split(",</div>")[0]
                + "]"
            )
        except:
            continue
        js = json.loads(line)

        for j in js:
            page_url = j.get("indy_url") or ""
            if page_url.startswith("/"):
                page_url = page_url.replace("//", "https://")
            location_name = j.get("location_name")
            street_address = j.get("address_1") or ""
            city = j.get("city") or ""
            state = j.get("big_region") or ""
            postal = j.get("post_code") or ""
            raw_address = " ".join(f"{street_address} {city} {state} {postal}".split())
            country_code = j.get("country")
            if country_code != "GB":
                continue
            store_number = j.get("fid")
            phone = j.get("local_phone")
            latitude = j.get("lat")
            longitude = j.get("lng")
            location_type = j.get("Store Type_CS")

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

            hours_of_operation = ";".join(_tmp)

            try:
                hours_of_operation = override(j)
            except:
                pass

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
                locator_domain=locator_domain,
                hours_of_operation=hours_of_operation,
                raw_address=raw_address,
            )

            sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:95.0) Gecko/20100101 Firefox/95.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "ru,en-US;q=0.7,en;q=0.3",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
    }
    locator_domain = "https://pandora.net/"
    with SgWriter(
        SgRecordDeduper(
            RecommendedRecordIds.PageUrlId, duplicate_streak_failure_factor=-1
        )
    ) as writer:
        fetch_data(writer)
