import re
from sgrequests import SgRequests
from concurrent import futures
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


def get_ids():
    r = session.get("https://stores.sportinglife.ca/en", headers=headers)
    ids = re.findall(r'"id":(\d+)', r.text)

    return ids


def get_urls():
    urls = []

    ids = get_ids()
    batches = [ids[i : i + 20] for i in range(0, len(ids), 20)]
    for b in batches:
        url = f'https://sls-api-service.sweetiq-sls-production-east.sweetiq.com/bu0CZYVJ3RYzVPxbBx5en7FF68xew9/locations-details?locale=en_CA&ids={",".join(b)}&clientId=5d3b8ea0622a30a967bc87c7&cname=stores.sportinglife.ca'
        urls.append(url)

    return urls


def get_data(url, sgw):
    r = session.get(url, headers=headers)
    js = r.json()["features"]

    for j in js:
        try:
            g = j.get("geometry").get("coordinates")
        except:
            g = ["<MISSING>", "<MISSING>"]

        j = j.get("properties")
        location_name = j.get("name")
        page_url = f'https://stores.sportinglife.ca/{j.get("slug")}'
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
            store_number=SgRecord.MISSING,
            phone=phone,
            location_type=SgRecord.MISSING,
            latitude=latitude,
            longitude=longitude,
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


def fetch_data(sgw: SgWriter):
    urls = get_urls()

    with futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(get_data, url, sgw): url for url in urls}
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":
    locator_domain = "https://www.sportinglife.ca/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:94.0) Gecko/20100101 Firefox/94.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "ru,en-US;q=0.7,en;q=0.3",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "If-None-Match": 'W/"13e84-sa6JY1UVtZx+6rcbjCcq75dGrh0"',
        "Cache-Control": "max-age=0",
        "TE": "trailers",
    }

    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
