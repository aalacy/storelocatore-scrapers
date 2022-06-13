from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgzip.dynamic import SearchableCountries, DynamicGeoSearch


def get_hoo(page_url):
    _tmp = []
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    lines = tree.xpath("//div[@id='regStores']//h2/text()")
    for line in lines:
        if not line.strip():
            continue
        _tmp.append(line.strip())
        if "Sun" in line:
            break

    return ";".join(_tmp)


def fetch_data(coords, sgw: SgWriter):
    lat, lng = coords
    api = f"https://www.athome.com/on/demandware.store/Sites-athome-sfra-Site/default/Stores-FindStores?radius=50&lat={lat}&long={lng}"
    r = session.get(api, headers=headers)
    js = r.json()["stores"]

    for j in js:
        page_url = f'https://www.athome.com/store-detail/?StoreID={j.get("ID")}'
        location_name = j.get("name").strip()
        street_address = f"{j.get('address1')} {j.get('address2') or ''}".strip()
        city = j.get("city")
        state = j.get("stateCode")
        postal = j.get("postalCode")
        country_code = j.get("countryCode")
        phone = j.get("phone") or ""
        if "Coming" in phone:
            continue
        latitude = j.get("latitude")
        longitude = j.get("longitude")

        _tmp = []
        hours = j.get("actualHours") or []
        for h in hours:
            day = h.get("day")
            if h.get("isClosed"):
                _tmp.append(f"{day}: Closed")
                continue
            start = h.get("start")
            end = h.get("end")
            _tmp.append(f"{day}: {start}-{end}")

        hours_of_operation = ";".join(_tmp)
        if not hours_of_operation:
            try:
                hours_of_operation = get_hoo(page_url)
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
            phone=phone,
            latitude=latitude,
            longitude=longitude,
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:86.0) Gecko/20100101 Firefox/86.0"
    }

    locator_domain = "https://www.athome.com/"
    search = DynamicGeoSearch(
        country_codes=[SearchableCountries.USA],
        expected_search_radius_miles=50,
    )
    with SgWriter(
        SgRecordDeduper(
            RecommendedRecordIds.PageUrlId, duplicate_streak_failure_factor=-1
        )
    ) as writer:
        for p in search:
            fetch_data(p, writer)
