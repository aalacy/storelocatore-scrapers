import json
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def get_dict():
    out = dict()
    params = (
        (
            "url",
            "https://cms.vizergy.com/yext/index.aspx?Fields=address,mainPhone,hours,meta&PageWidgetId=805821&CacheMinutes=5&callback=YextDataAllLocationsMap",
        ),
    )

    r = session.get(
        "https://www.hardrockcafe.com/cdn-cache.aspx", headers=headers, params=params
    )
    text = (
        r.text.replace(";", "")
        .replace("(", "")
        .replace(")", "")
        .replace("YextDataAllLocationsMap", "")
    )
    js = json.loads(text)["response"]["entities"]
    for j in js:
        _id = j["meta"]["id"]
        out[_id] = j

    return out


def fetch_data(sgw: SgWriter):
    additional = get_dict()
    api = "https://www.hardrockcafe.com/files/5282/widget805821.js"
    r = session.get(api, headers=headers)
    text = (
        r.content.decode("utf-8-sig")
        .replace(");", "")
        .replace("widget805821DataCallback(", "")
    )
    js = json.loads(text)["PropertyorInterestPoint"]

    for j in js:
        location_name = j.get("interestpointpropertyname")
        page_url = j.get("interestpointMoreInfoLink")
        store_number = j.get("interestpointYextEntityId")
        latitude = j.get("interestpointinterestlatitude")
        longitude = j.get("interestpointinterestlongitude")
        if not store_number:
            continue

        add = additional.get(store_number)
        a = add.get("address") or {}
        street_address = f'{a.get("line1")} {a.get("line2") or ""}'.strip()
        city = a.get("city")
        state = a.get("region")
        postal = a.get("postalCode")
        country = a.get("countryCode")
        phone = add.get("mainPhone")

        _tmp = []
        hours = add.get("hours") or {}
        for day, v in hours.items():
            if not v or isinstance(v, list):
                continue
            inters = []
            inter = v.get("openIntervals") or []
            for i in inter:
                start = i.get("startIn12HourFormat")
                end = i.get("endIn12HourFormat")
                inters.append(f"{start}-{end}")
            _tmp.append(f'{day}: {"&".join(inters)}')

        hours_of_operation = ";".join(_tmp)

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code=country,
            store_number=store_number,
            phone=phone,
            latitude=latitude,
            longitude=longitude,
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.hardrockcafe.com/"

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:96.0) Gecko/20100101 Firefox/96.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "ru,en-US;q=0.7,en;q=0.3",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "cross-site",
        "Cache-Control": "max-age=0",
        "TE": "trailers",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
