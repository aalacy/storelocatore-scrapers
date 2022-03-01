from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgzip.dynamic import DynamicZipSearch, SearchableCountries
from concurrent import futures


def get_data(zips, sgw: SgWriter):

    locator_domain = "https://www.opsm.com.au"

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "Content-Type": "application/json; charset=utf-8",
        "X-Requested-With": "XMLHttpRequest",
        "Origin": "https://www.opsm.com.au",
        "Connection": "keep-alive",
        "Referer": "https://www.opsm.com.au/find-store",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
    }

    r = session.post(
        f"https://www.opsm.com.au/AddressValidationResultsView?catalogId=12601&langId=-1&storeId=10151&term={zips}",
        headers=headers,
    )
    try:
        js = r.json()
    except:
        return

    for j in js:

        term = j.get("term")
        value = j.get("value")
        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
            "Content-Type": "application/x-www-form-urlencoded",
            "Origin": "https://www.opsm.com.au",
            "Connection": "keep-alive",
            "Referer": "https://www.opsm.com.au/find-store",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-User": "?1",
        }

        data = {
            "addressValidationResults": "/AddressValidationResultsView?catalogId=12601&langId=-1&storeId=10151",
            "storeId": "10151",
            "catalogId": "12601",
            "langId": "-1",
            "eyetest": "Classic",
            "url": "AppointmentChooseStore",
            "searchCountryLimit": "Australia",
            "searchCountryCode": "AU",
            "zipCode": f"{term}",
            "townSuburb": "",
            "suburbSuggest-bet": f"{value}",
        }

        r = session.post(
            "https://www.opsm.com.au/StoreLocatorView", headers=headers, data=data
        )
        try:
            tree = html.fromstring(r.text)
        except:
            continue
        div = tree.xpath('//div[@class="select-store--item store-location"]')
        for d in div:
            slug = "".join(
                d.xpath('.//a[./span[contains(text(), "Store Details ")]]/@href')
            )
            page_url = f"https://www.opsm.com.au{slug}"
            location_name = (
                "".join(d.xpath('.//h6[@itemprop="name"]/text()'))
                .replace("\n", "")
                .strip()
                or "<MISSING>"
            )
            street_address = (
                "".join(d.xpath('.//input[contains(@id, "addressLine1")]/@value'))
                or "<MISSING>"
            )
            if street_address == "<MISSING>":
                street_address = (
                    "".join(d.xpath('.//input[contains(@id, "addressLine2")]/@value'))
                    or "<MISSING>"
                )
            city = (
                "".join(d.xpath('.//input[contains(@id, "city")]/@value'))
                or "<MISSING>"
            )
            state = (
                "".join(d.xpath('.//input[contains(@id, "state")]/@value'))
                or "<MISSING>"
            )
            postal = (
                "".join(d.xpath('.//input[contains(@id, "postalCode")]/@value'))
                or "<MISSING>"
            )
            country_code = "AU"
            phone = (
                "".join(d.xpath('.//input[contains(@id, "telephone")]/@value'))
                .replace("Tel:", "")
                .strip()
                or "<MISSING>"
            )
            latitude = "".join(d.xpath('.//meta[@itemprop="latitude"]/@content'))
            longitude = "".join(d.xpath('.//meta[@itemprop="longitude"]/@content'))
            hours_of_operation = (
                " ".join(
                    d.xpath(
                        './/ul[@class="list-unstyled select-store--item--hour opening-hours"]/li//text()'
                    )
                )
                .replace("\n", "")
                .strip()
                or "<MISSING>"
            )
            hours_of_operation = " ".join(hours_of_operation.split())
            store_number = (
                "".join(d.xpath('.//input[contains(@id, "uniqueId")]/@value'))
                or "<MISSING>"
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
                store_number=store_number,
                phone=phone,
                location_type=SgRecord.MISSING,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hours_of_operation,
            )

            sgw.write_row(row)


def fetch_data(sgw: SgWriter):
    zips = DynamicZipSearch(
        country_codes=[SearchableCountries.AUSTRALIA],
        max_search_distance_miles=100,
        expected_search_radius_miles=100,
        max_search_results=None,
    )

    with futures.ThreadPoolExecutor(max_workers=2) as executor:
        future_to_url = {executor.submit(get_data, url, sgw): url for url in zips}
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
