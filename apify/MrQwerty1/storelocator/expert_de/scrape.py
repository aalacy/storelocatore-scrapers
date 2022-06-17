from sgscrape.sgrecord import SgRecord
from sgselenium import SgChrome
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def get_js():
    with SgChrome(driver_wait_timeout=10) as fox:
        fox.get("https://www.expert.de/storefinder")
        return fox.execute_async_script(
            """
        fetch('https://www.expert.de/_api/storeFinder/searchStoresByGeoLocation', {
    method: 'POST',
    headers: {
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:101.0) Gecko/20100101 Firefox/101.0',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-Language': 'ru,en-US;q=0.7,en;q=0.3',
        'Accept-Encoding': 'gzip, deflate, br',
        'Referer': 'https://www.expert.de/storefinder',
        'Content-Type': 'application/json; charset=utf-8',
        'X-Requested-With': 'XMLHttpRequest',
        'Origin': 'https://www.expert.de',
        'Alt-Used': 'www.expert.de',
        'Connection': 'keep-alive',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'no-cors',
        'Sec-Fetch-Site': 'same-origin',
        'TE': 'trailers',
        'Pragma': 'no-cache',
        'Cache-Control': 'no-cache'
    },
    body: JSON.stringify({
        'lat': 52.52000659999999,
        'lng': 13.404954,
        'maxResults': 500,
        'conditions': {
            'storeFinderResultFilter': 'PRODUCT_VISIBLE'
        }
    })
})
            .then(res => res.json())
            .then(arguments[0])
            .catch(err => arguments[0](JSON.stringify(err.error)))
    """
        )


def fetch_data(sgw: SgWriter):
    js = get_js()

    for j in js:
        s = j.get("store") or {}
        street_address = s.get("street")
        city = s.get("city")
        postal = s.get("zip")
        country_code = "DE"
        store_number = s.get("expId")
        location_name = s.get("name")
        phone = s.get("phone")
        latitude = s.get("latitude")
        longitude = s.get("longitude")

        _tmp = []
        hours = j.get("openingTimes") or {}
        for day, h in hours.items():
            inter = "|".join(h.get("times") or [])
            _tmp.append(f"{day}: {inter}")

        hours_of_operation = ";".join(_tmp)

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            zip_postal=postal,
            country_code=country_code,
            latitude=latitude,
            longitude=longitude,
            phone=phone,
            store_number=store_number,
            hours_of_operation=hours_of_operation,
            locator_domain=locator_domain,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.expert.de/"
    page_url = "https://www.expert.de/storefinder"

    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        fetch_data(writer)
