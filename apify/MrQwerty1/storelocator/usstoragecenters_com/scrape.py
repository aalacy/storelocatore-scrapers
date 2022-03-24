from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from concurrent import futures


def get_hours(slug):
    url = f"https://www.usstoragecenters.com{slug}"
    r = session.get(url, headers=headers)
    tree = html.fromstring(r.text)

    _tmp = []
    li = tree.xpath("//div[@class='ww-location-d__office_hours']//li")
    for l in li:
        day = "".join(l.xpath("./span[1]//text()")).strip()
        time = "".join(l.xpath("./span[2]//text()")).strip()
        _tmp.append(f"{day}: {time}")

    return ";".join(_tmp)


def fetch_data(sgw: SgWriter):
    urls, hours = list(), dict()
    api = "https://www.usstoragecenters.com/storage-units/?spa=true"
    r = session.get(api, headers=headers)
    js = r.json()["data"]["content"][0]["context"]["items"]

    for j in js:
        urls.append(j.get("url"))

    with futures.ThreadPoolExecutor(max_workers=3) as executor:
        future_to_url = {executor.submit(get_hours, url): url for url in urls}
        for future in futures.as_completed(future_to_url):
            val = future.result()
            key = future_to_url[future]
            hours[key] = val

    for j in js:
        a = j.get("address")
        street_address = a.get("address")
        city = a.get("city")
        state = a.get("state")
        postal = a.get("zip")
        country_code = "US"
        store_number = j.get("locationCode")
        slug = j.get("url")
        page_url = f"https://www.usstoragecenters.com{slug}"
        location_name = j.get("sanitizedHeader") or "US Storage Centers"
        location_name = location_name.replace("&amp;", "&")
        try:
            phone = j["phone"]["label"]["value"]
        except TypeError:
            phone = SgRecord.MISSING
        latitude = a.get("latitude")
        longitude = a.get("longitude")
        if "°" in latitude or "°" in longitude:
            latitude = (
                latitude.replace(".", "")
                .replace("'", "")
                .replace('"', "")
                .replace("N", "")
                .replace("°", ".")
            )
            longitude = "-" + longitude.replace(".", "").replace("'", "").replace(
                '"', ""
            ).replace("W", "").replace("°", ".")

        hours_of_operation = hours.get(slug)

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code=country_code,
            latitude=latitude,
            longitude=longitude,
            phone=phone,
            store_number=store_number,
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.usstoragecenters.com/"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:97.0) Gecko/20100101 Firefox/97.0",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
