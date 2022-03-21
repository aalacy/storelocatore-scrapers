import re
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from concurrent import futures


def get_ids():
    r = session.get("https://stores.telus.com/")
    ids = re.findall(r'"id":(\d+)', r.text)

    return ids


def get_urls():
    urls = []

    ids = get_ids()
    batches = [ids[i : i + 20] for i in range(0, len(ids), 20)]
    for b in batches:
        url = f'https://sls-api-service.sweetiq-sls-production-east.sweetiq.com/4JxwourSv9myM4JuR5Ayb7Wq4uKEHl/locations-details?locale=en_US&ids={",".join(b)}&cname=stores.telus.com'
        urls.append(url)

    return urls


def get_data(url, sgw: SgWriter):
    r = session.get(url)
    js = r.json()["features"]

    for j in js:
        try:
            g = j.get("geometry").get("coordinates")
        except:
            g = [SgRecord.MISSING, SgRecord.MISSING]

        j = j.get("properties")
        location_name = j.get("name")
        if "telus" not in location_name.lower():
            continue

        page_url = f'https://stores.telus.com/{j.get("slug")}'
        street_address = (
            f'{j.get("addressLine1")} {j.get("addressLine2") or ""}'.strip()
        )
        city = j.get("city")
        state = j.get("province")
        postal = j.get("postalCode")
        country_code = j.get("country")
        phone = j.get("phoneLabel")
        latitude = g[1]
        longitude = g[0]

        _tmp = []
        hours = j.get("hoursOfOperation") or {}
        for k, v in hours.items():
            _tmp.append(f'{k}: {"".join(map("-".join, v)) or "Closed"}')

        hours_of_operation = ";".join(_tmp)

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


def fetch_data(sgw: SgWriter):
    urls = get_urls()

    with futures.ThreadPoolExecutor(max_workers=5) as executor:
        future_to_url = {executor.submit(get_data, url, sgw): url for url in urls}
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":
    locator_domain = "https://telus.com/"
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
