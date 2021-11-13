from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries
from concurrent import futures


def get_data(coords, sgw: SgWriter):
    lat, long = coords
    locator_domain = "https://www.burgerking.co.nz/"
    page_url = f"https://www.burgerking.co.nz/locations?field_geofield_distance[origin][lat]={str(lat)}&field_geofield_distance[origin][lon]={str(long)}"

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "Alt-Used": "www.burgerking.fi",
        "Connection": "keep-alive",
        "Referer": f"https://www.burgerking.co.nz/locations?field_geofield_distance[origin][lat]={str(lat)}&field_geofield_distance[origin][lon]={str(long)}",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-User": "?1",
    }

    session = SgRequests()

    r = session.get(page_url, headers=headers)

    tree = html.fromstring(r.text)
    div = tree.xpath('//div[@class="bk-restaurants"]/ul/li')
    for d in div:
        location_name = "".join(
            d.xpath('.//div[@class="bk-location-title"]/text()')
        ).strip()
        street_address = "".join(d.xpath('.//div[@class="bk-address1"]/text()')).strip()
        state = "".join(d.xpath('.//div[@class="bk-province-name"]/text()'))
        postal = "".join(d.xpath('.//div[@class="bk-zip"]/text()'))
        if postal == "-":
            postal = "<MISSING>"
        country_code = "".join(d.xpath('.//div[@class="bk-country"]/text()'))
        city = "".join(d.xpath('.//div[@class="bk-city"]/text()'))
        latitude = "".join(d.xpath('.//div[@class="bk-latitude"]/text()'))
        longitude = "".join(d.xpath('.//div[@class="bk-longitude"]/text()'))
        phone = "".join(d.xpath('.//div[@class="bk-phone"]/text()'))
        if phone == "0":
            phone = "<MISSING>"
        if phone.find("Restaurant") != -1:
            phone = phone.split("Restaurant: ")[1].split(",")[0].strip()
        if phone.find(",") != -1:
            phone = phone.split(",")[0].strip()
        days = [
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
            "Sunday",
        ]
        weekday = d.xpath('.//div[contains(@class, "hours")]/text()')
        i = 0
        tmp = []
        for d in days:
            day = d
            times = "".join(weekday[i])
            if times.find("(") != -1:
                times = times.split("(")[0].strip()
            i += 1
            line = f"{day} {times}"
            tmp.append(line)

        hours_of_operation = "; ".join(tmp) or "<MISSING>"

        row = SgRecord(
            locator_domain=locator_domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code=country_code,
            store_number=SgRecord.MISSING,
            phone=phone,
            location_type=SgRecord.MISSING,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


def fetch_data(sgw: SgWriter):
    coords = DynamicGeoSearch(
        country_codes=[SearchableCountries.NEW_ZEALAND],
        max_search_distance_miles=500,
        expected_search_radius_miles=10,
        max_search_results=None,
    )

    with futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(get_data, url, sgw): url for url in coords}
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.GeoSpatialId)) as writer:
        fetch_data(writer)
