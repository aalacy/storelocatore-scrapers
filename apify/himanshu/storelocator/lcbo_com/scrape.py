from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from f.dynamic import DynamicGeoSearch, SearchableCountries
from sgpostal.sgpostal import International_Parser, parse_address
from concurrent import futures


def get_data(coords, sgw: SgWriter):
    lat, long = coords
    locator_domain = "https://www.lcbo.com/"

    session = SgRequests()

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
        "Accept": "*/*",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "X-NewRelic-ID": "VwQHU1dQCRAJU1NUAgMEUFQ=",
        "newrelic": "eyJ2IjpbMCwxXSwiZCI6eyJ0eSI6IkJyb3dzZXIiLCJhYyI6IjMyMDIxMzEiLCJhcCI6IjEwMjgwMDg2OTIiLCJpZCI6ImE0NmRjNDg4NTQ1Y2Q1MjAiLCJ0ciI6IjNjOWNhNWQzY2U1MWE2Y2NhOWY1ZWIwMWFmYjU2MGMwIiwidGkiOjE2NDk4NDU3NjM0OTAsInRrIjoiMTMyMjg0MCJ9fQ==",
        "traceparent": "00-3c9ca5d3ce51a6cca9f5eb01afb560c0-a46dc488545cd520-01",
        "tracestate": "1322840@nr=0-1-3202131-1028008692-a46dc488545cd520----1649845763490",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "X-Requested-With": "XMLHttpRequest",
        "Origin": "https://www.lcbo.com",
        "Connection": "keep-alive",
        "Referer": "https://www.lcbo.com/en/stores/",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
    }

    data = {
        "lat": f"{lat}",
        "lng": f"{long}",
    }

    r = session.post(
        "https://www.lcbo.com/en/amlocator/index/ajax/", headers=headers, data=data
    )

    js = r.json()["items"]

    for j in js:

        info = j.get("popup_html")
        a = html.fromstring(info)
        page_url = "".join(a.xpath('//h3[@class="amlocator-name"]/a/@href'))
        location_name = (
            "".join(a.xpath('//h3[@class="amlocator-name"]//text()'))
            .replace("\n", "")
            .strip()
        )
        ad = (
            " ".join(a.xpath('//div[@class="amlocator-info-popup"]//text()'))
            .replace("Address 2", "")
            .replace("address 2", "")
            .replace(":", "")
            .replace("\n", "")
            .strip()
        )
        ad = " ".join(ad.split())
        b = parse_address(International_Parser(), ad)
        street_address = (
            f"{b.street_address_1} {b.street_address_2}".replace("None", "").strip()
            or "<MISSING>"
        )
        state = b.state or "<MISSING>"
        postal = b.postcode or "<MISSING>"
        country_code = "CA"
        city = b.city or "<MISSING>"
        phone = (
            "".join(a.xpath('//div[@class="amlocator-phone-number"]//text()'))
            or "<MISSING>"
        )
        latitude = j.get("lat")
        longitude = j.get("lng")
        store_number = j.get("stloc")
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)
        hours_of_operation = (
            " ".join(tree.xpath('//div[@class="amlocator-week"]//div//div//text()'))
            .replace("\n", "")
            .strip()
        )
        hours_of_operation = " ".join(hours_of_operation.split()) or "<MISSING>"

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
            raw_address=ad,
        )

        sgw.write_row(row)


def fetch_data(sgw: SgWriter):
    coords = DynamicGeoSearch(
        country_codes=[SearchableCountries.CANADA],
        max_search_distance_miles=10,
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
