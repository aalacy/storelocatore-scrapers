import json
from datetime import datetime, timedelta
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


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
    api_url = (
        "https://maps.pandora.net/api/getAsyncLocations?search=75022&level=domain"
        "&template=domain&limit=5000&radius=5000"
    )

    r = session.get(api_url)
    js_init = r.json()["maplist"]
    line = "[" + js_init.split('<div class="tlsmap_list">')[1].split(",</div>")[0] + "]"
    js = json.loads(line)

    for j in js:
        page_url = j.get("indy_url").replace("//", "https://")
        location_name = j.get("location_name")
        street_address = f"{j.get('address_1')} {j.get('address_2')}".strip()
        city = j.get("city")
        state = j.get("big_region")
        postal = j.get("post_code")
        country_code = j.get("country")
        store_number = j.get("fid")
        phone = j.get("local_phone")
        latitude = j.get("lat")
        longitude = j.get("lng")
        location_type = j.get("Store Type_CS")
        if country_code != "US":
            continue

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
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    locator_domain = "https://us.pandora.net/"
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
