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
    locator_domain = "https://www.burgerking.no/"
    page_url = f"https://www.burgerking.no/locations?field_geofield_distance[origin][lat]={str(lat)}&field_geofield_distance[origin][lon]={str(long)}"

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "Alt-Used": "www.burgerking.fi",
        "Connection": "keep-alive",
        "Referer": f"https://www.burgerking.no/locations?field_geofield_distance[origin][lat]={str(lat)}&field_geofield_distance[origin][lon]={str(long)}",
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

        street_address = (
            "".join(d.xpath('.//div[@class="bk-address1"]/text()'))
            .replace(", TEGUCIGALPA", "")
            .strip()
        )
        state = "".join(d.xpath('.//div[@class="bk-province-name"]/text()'))
        postal = "".join(d.xpath('.//div[@class="bk-zip"]/text()'))
        country_code = "".join(d.xpath('.//div[@class="bk-country"]/text()'))
        city = "".join(d.xpath('.//div[@class="bk-city"]/text()'))
        latitude = "".join(d.xpath('.//div[@class="bk-latitude"]/text()'))
        longitude = "".join(d.xpath('.//div[@class="bk-longitude"]/text()'))
        phone = "".join(d.xpath('.//div[@class="bk-phone"]/text()'))
        if phone == "0" or phone.find("000-000-0000") != -1:
            phone = "<MISSING>"
        sundayOpen = (
            "".join(d.xpath('.//div[@class="bk-location_sun_dining"]/text()'))
            .split(";")[0]
            .split()[1]
            .strip()
        )
        sundayClose = (
            "".join(d.xpath('.//div[@class="bk-location_sun_dining"]/text()'))
            .split(";")[1]
            .split()[1]
            .strip()
        )
        mondayOpen = (
            "".join(d.xpath('.//div[@class="bk-location_mon_dining"]/text()'))
            .split(";")[0]
            .split()[1]
            .strip()
        )
        mondayClose = (
            "".join(d.xpath('.//div[@class="bk-location_mon_dining"]/text()'))
            .split(";")[1]
            .split()[1]
            .strip()
        )
        tuesdayOpen = (
            "".join(d.xpath('.//div[@class="bk-location_tue_dining"]/text()'))
            .split(";")[0]
            .split()[1]
            .strip()
        )
        tuesdayClose = (
            "".join(d.xpath('.//div[@class="bk-location_tue_dining"]/text()'))
            .split(";")[1]
            .split()[1]
            .strip()
        )
        wednesdayOpen = (
            "".join(d.xpath('.//div[@class="bk-location_wed_dining"]/text()'))
            .split(";")[0]
            .split()[1]
            .strip()
        )
        wednesdayClose = (
            "".join(d.xpath('.//div[@class="bk-location_wed_dining"]/text()'))
            .split(";")[1]
            .split()[1]
            .strip()
        )
        thursdayOpen = (
            "".join(d.xpath('.//div[@class="bk-location_thu_dining"]/text()'))
            .split(";")[0]
            .split()[1]
            .strip()
        )
        thursdayClose = (
            "".join(d.xpath('.//div[@class="bk-location_thu_dining"]/text()'))
            .split(";")[1]
            .split()[1]
            .strip()
        )
        fridayOpen = (
            "".join(d.xpath('.//div[@class="bk-location_fri_dining"]/text()'))
            .split(";")[0]
            .split()[1]
            .strip()
        )
        fridayClose = (
            "".join(d.xpath('.//div[@class="bk-location_fri_dining"]/text()'))
            .split(";")[1]
            .split()[1]
            .strip()
        )
        saturdayOpen = (
            "".join(d.xpath('.//div[@class="bk-location_sat_dining"]/text()'))
            .split(";")[0]
            .split()[1]
            .strip()
        )
        saturdayClose = (
            "".join(d.xpath('.//div[@class="bk-location_sat_dining"]/text()'))
            .split(";")[1]
            .split()[1]
            .strip()
        )
        hours_of_operation = f"Sunday {sundayOpen} - {sundayClose} Monday {mondayOpen} - {mondayClose} Tuesday {tuesdayOpen} - {tuesdayClose} Wednesday {wednesdayOpen} - {wednesdayClose} Thursday {thursdayOpen} - {thursdayClose} Friday {fridayOpen} - {fridayClose} Saturday {saturdayOpen} - {saturdayClose}"
        row = SgRecord(
            locator_domain=locator_domain,
            page_url=page_url,
            location_name=SgRecord.MISSING,
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
        country_codes=[SearchableCountries.NORWAY],
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
