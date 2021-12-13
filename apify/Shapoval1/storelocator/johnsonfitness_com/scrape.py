from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgzip.dynamic import DynamicZipSearch, SearchableCountries
from concurrent import futures


def get_data(zips, sgw: SgWriter):

    locator_domain = "https://www.johnsonfitness.com"

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "Content-Type": "application/x-www-form-urlencoded",
        "Origin": "https://www.johnsonfitness.com",
        "Connection": "keep-alive",
        "Referer": "https://www.johnsonfitness.com/StoreLocator/",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-User": "?1",
        "TE": "trailers",
    }

    data = {
        "submitted": "1",
        "view_type": "Home",
        "cbFilter": "",
        "searchZip": f"{zips}",
    }
    session = SgRequests()

    r = session.post(
        "https://www.johnsonfitness.com/StoreLocator/Index?lat=&lon=",
        headers=headers,
        data=data,
    )

    tree = html.fromstring(r.text)
    div = tree.xpath('//div[@class="address"]//h3/a')

    for d in div:

        page_url = "".join(d.xpath(".//@href"))
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)

        location_name = (
            "".join(tree.xpath('//span[@itemprop="name"]/text()')) or "<MISSING>"
        )
        street_address = (
            "".join(tree.xpath('//span[@itemprop="streetAddress"]/text()'))
            .replace("\n", "")
            .strip()
            or "<MISSING>"
        )
        city = (
            "".join(tree.xpath('//span[@itemprop="addressLocality"]/text()'))
            .replace("\n", "")
            .strip()
            or "<MISSING>"
        )
        state = (
            "".join(tree.xpath('//span[@itemprop="addressRegion"]/text()'))
            .replace("\n", "")
            .strip()
            or "<MISSING>"
        )
        postal = (
            "".join(tree.xpath('//span[@itemprop="postalCode"]/text()'))
            .replace("\n", "")
            .strip()
            or "".join(tree.xpath('//p[@itemprop="address"]/text()'))
            .replace("\n", "")
            .replace(",", "")
            .strip()
            or "<MISSING>"
        )
        country_code = "US"
        phone = (
            "".join(
                tree.xpath(
                    '//p[@itemprop="address"]//span[@itemprop="telephone"]/text()'
                )
            )
            or "<MISSING>"
        )
        latitude = (
            "".join(tree.xpath('//a[./span[text()="Get Directions"]]/@href'))
            .split("ll=")[1]
            .split(",")[0]
            .strip()
        )
        longitude = (
            "".join(tree.xpath('//a[./span[text()="Get Directions"]]/@href'))
            .split("ll=")[1]
            .split(",")[1]
            .strip()
        )
        hours_of_operation = (
            " ".join(
                tree.xpath(
                    '//div[contains(@class, "hours")]/span//meta[@itemprop="openingHours"]/@content'
                )
            )
            .replace("\n", "")
            .strip()
        )

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
            raw_address=f"{street_address} {city}, {state} {postal}",
        )

        sgw.write_row(row)


def fetch_data(sgw: SgWriter):
    zips = DynamicZipSearch(
        country_codes=[SearchableCountries.USA],
        max_search_distance_miles=30,
        expected_search_radius_miles=30,
        max_search_results=None,
    )

    with futures.ThreadPoolExecutor(max_workers=5) as executor:
        future_to_url = {executor.submit(get_data, url, sgw): url for url in zips}
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
