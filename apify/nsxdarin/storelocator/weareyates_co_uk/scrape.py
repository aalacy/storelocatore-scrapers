from lxml import html
from datetime import datetime
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgzip.dynamic import DynamicZipSearch, SearchableCountries
from concurrent import futures


def get_data(zips, sgw: SgWriter):

    locator_domain = "https://weareyates.co.uk/"

    session = SgRequests()

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
        "Accept": "*/*",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "X-Requested-With": "XMLHttpRequest",
        "Origin": "https://www.greatukpubs.co.uk",
        "Connection": "keep-alive",
        "Referer": "https://www.greatukpubs.co.uk/",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "TE": "trailers",
    }

    data = {"postcode": f"{zips}"}

    r = session.post("https://www.greatukpubs.co.uk/", headers=headers, data=data)
    try:
        js = r.json()["mapPoints"]
    except:
        return
    for j in js:
        store_number = j.get("id") or "<MISSING>"
        slug = j.get("UrlText")
        page_url = f"https://www.greatukpubs.co.uk/{slug}"
        location_name = j.get("UnitName") or "<MISSING>"
        street_address = (
            f"{j.get('Address1')} {j.get('Address2')}".replace("Market House", "")
            .replace("Marshall House", "")
            .strip()
        )
        street_address = " ".join(street_address.split())
        city = j.get("TownCity") or "<MISSING>"
        state = "<MISSING>"
        postal = j.get("PostCode") or "<MISSING>"
        country_code = "UK"
        phone = j.get("Telephone") or "<MISSING>"
        latitude = j.get("lat") or "<MISSING>"
        longitude = j.get("lng") or "<MISSING>"
        if longitude == "0" or longitude == 0:
            longitude = "<MISSING>"
        r = session.get(page_url)
        tree = html.fromstring(r.text)
        hours_of_operation = (
            " ".join(tree.xpath('//div[@class="opening-times"]/div//text()'))
            .replace("\n", "")
            .strip()
        )
        today = datetime.today().strftime("%A")
        hours_of_operation = (
            " ".join(hours_of_operation.split()).replace("Today", f"{today}").strip()
        )
        if hours_of_operation.count("Closed") == 7:
            hours_of_operation = "Closed"
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
        country_codes=[SearchableCountries.BRITAIN],
        max_search_distance_miles=20,
        expected_search_radius_miles=20,
        max_search_results=None,
    )

    with futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(get_data, url, sgw): url for url in zips}
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
