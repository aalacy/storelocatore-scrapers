import json
import time
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgzip.dynamic import DynamicZipSearch, SearchableCountries
from concurrent import futures


def get_data(zipps, sgw: SgWriter):

    locator_domain = "https://www.babyone.de/"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
        "Accept": "*/*",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "Referer": "https://www.babyone.de/",
        "X-Requested-With": "XMLHttpRequest",
        "Content-type": "application/json",
        "Connection": "keep-alive",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
    }

    params = {
        "search": f"{str(zipps)}",
    }

    r = session.get(
        "https://www.babyone.de/place/suggest", params=params, headers=headers
    )
    tree = html.fromstring(r.text)
    div = tree.xpath("//div[@data-place-id]")
    for d in div:
        search = "".join(d.xpath("./@data-text-search"))
        place_id = "".join(d.xpath("./@data-place-id"))
        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
            "Accept": "*/*",
            "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
            "Referer": "https://www.babyone.de/",
            "X-Requested-With": "XMLHttpRequest",
            "Content-type": "application/json",
            "Connection": "keep-alive",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
        }

        params = {
            "search": f"{search}",
            "placeId": f"{place_id}",
        }
        r = session.get(
            "https://www.babyone.de/store-finder/search", params=params, headers=headers
        )
        try:
            js = r.json()["html"]
        except:
            continue
        tree = html.fromstring(js)
        div = tree.xpath('//a[@class="retail-market-result-item-link "]')
        for d in div:
            slug = "".join(d.xpath("./@href"))
            page_url = f"https://www.babyone.de{slug}"
            headers = {
                "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
                "Referer": "https://www.babyone.de/",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "same-origin",
                "Sec-Fetch-User": "?1",
                "Cache-Control": "max-age=0",
            }
            try:
                r = session.get(page_url, headers=headers)
                tree = html.fromstring(r.text)
            except:
                try:
                    time.sleep(40)
                    r = session.get(page_url, headers=headers)
                    tree = html.fromstring(r.text)
                except:
                    continue

            js_block = "".join(tree.xpath("//div/@data-google-map-options"))
            js = json.loads(js_block)
            a = js.get("storeData")
            location_name = (
                "".join(tree.xpath("//h1//text()")).replace("\n", "").strip()
                or "<MISSING>"
            )
            street_address = a.get("address1") or "<MISSING>"
            city = a.get("city") or "<MISSING>"
            state = "<MISSING>"
            postal = a.get("postalCode") or "<MISSING>"
            country_code = a.get("countryCode")
            phone = a.get("phone") or "<MISSING>"
            latitude = a.get("latitude") or "<MISSING>"
            longitude = a.get("longitude") or "<MISSING>"
            hours = a.get("storeHours")
            hours_of_operation = "<MISSING>"
            if hours:
                hours_of_operation = "".join(hours).replace("\n", " ").strip()
            store_number = a.get("storeId") or "<MISSING>"

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
    coords = DynamicZipSearch(
        country_codes=[
            SearchableCountries.GERMANY,
            SearchableCountries.AUSTRIA,
            SearchableCountries.SWITZERLAND,
        ],
        max_search_distance_miles=100,
        expected_search_radius_miles=50,
        max_search_results=None,
    )

    with futures.ThreadPoolExecutor(max_workers=5) as executor:
        future_to_url = {executor.submit(get_data, url, sgw): url for url in coords}
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        fetch_data(writer)
