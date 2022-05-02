from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries
from concurrent import futures


def get_data(coords, sgw: SgWriter):
    lat, long = coords
    locator_domain = "https://donnakaran.com/"

    cookies = {
        "form_key": "Em72IvTDRlpDrBGl",
    }

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
        "Accept": "*/*",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "X-NewRelic-ID": "VwYHWVJTDhAIVlRVAQgBVVM=",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "X-Requested-With": "XMLHttpRequest",
        "Origin": "https://www.dkny.com",
        "Connection": "keep-alive",
        "Referer": "https://www.dkny.com/donnakaran/store-locator/",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
    }

    data = {
        "latitude": f"{str(lat)}",
        "longitude": f"{str(long)}",
        "form_key": "Em72IvTDRlpDrBGl",
    }

    r = session.post(
        "https://www.dkny.com/donnakaran/odlocator/index/ajax/",
        headers=headers,
        data=data,
        cookies=cookies,
    )
    js = r.json()["sources"]
    for j in js:

        page_url = j.get("url") or "<MISSING>"
        location_name = j.get("name") or "<MISSING>"
        street_address = "<MISSING>"
        city = j.get("city") or "<MISSING>"
        state = j.get("region") or "<MISSING>"
        postal = j.get("postcode") or "<MISSING>"
        country_code = "<MISSING>"
        phone = j.get("phone") or "<MISSING>"
        latitude = j.get("latitude") or "<MISSING>"
        longitude = j.get("longitude") or "<MISSING>"
        hours = j.get("schedule")
        hours_of_operation = "<MISSING>"
        if hours:
            a = html.fromstring(hours)
            hours_of_operation = " ".join(
                a.xpath('//div[@class="schedule-list"]//text()')
            )
            hours_of_operation = " ".join(hours_of_operation.split())
        if (
            hours_of_operation
            == "Monday - Tuesday - Wednesday - Thursday - Friday - Saturday - Sunday -"
        ):
            hours_of_operation = "<MISSING>"
        store_number = j.get("source_code")

        row = SgRecord(
            locator_domain=locator_domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code=country_code,
            store_number=store_number,
            phone=phone,
            location_type=SgRecord.MISSING,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


def fetch_data(sgw: SgWriter):
    for country in SearchableCountries.ALL:
        coords = DynamicGeoSearch(
            country_codes=[f"{country}"],
            max_search_distance_miles=20,
            expected_search_radius_miles=20,
            max_search_results=None,
        )

        with futures.ThreadPoolExecutor(max_workers=1) as executor:
            future_to_url = {executor.submit(get_data, url, sgw): url for url in coords}
            for future in futures.as_completed(future_to_url):
                future.result()


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(
            SgRecordID({SgRecord.Headers.STORE_NUMBER}),
            duplicate_streak_failure_factor=-1,
        )
    ) as writer:
        fetch_data(writer)
