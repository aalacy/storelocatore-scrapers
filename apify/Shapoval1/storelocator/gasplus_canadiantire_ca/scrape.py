from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from concurrent import futures


def get_urls():
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0",
    }
    r = session.get(
        "https://www.canadiantire.ca/sitemap_Store-en_CA-CAD.xml", headers=headers
    )
    tree = html.fromstring(r.content)
    return tree.xpath('//url/loc[contains(text(), "/store-details/")]/text()')


def get_data(url, sgw: SgWriter):
    locator_domain = "https://www.canadiantire.ca/"
    page_url = "".join(url)
    if page_url.count("/") != 6:
        return
    slug = page_url.split("-")[-1].split(".")[0].strip()

    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "Referer": "https://www.canadiantire.ca/",
        "x-web-host": "www.canadiantire.ca",
        "service-client": "ctr/web",
        "service-version": "ctc-dev2",
        "Ocp-Apim-Subscription-Key": "c01ef3612328420c9f5cd9277e815a0e",
        "baseSiteId": "CTR",
        "bannerid": "CTR",
        "Origin": "https://www.canadiantire.ca",
        "Connection": "keep-alive",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-site",
        "Cache-Control": "max-age=0",
    }

    params = {
        "lang": "en_CA",
    }
    try:
        r = session.get(
            f"https://apim.canadiantire.ca/v1/store/store/{slug}",
            params=params,
            headers=headers,
        )
        js = r.json()
    except:
        return
    location_name = js.get("name") or "<MISSING>"
    a = js.get("address")
    street_address = (
        f"{a.get('line1')} {a.get('line2') or ''}".replace("None", "").strip()
        or "<MISSING>"
    )
    city = a.get("town") or "<MISSING>"
    if city == "<MISSING>":
        city = a.get("city") or "<MISSING>"
    state = a.get("region").get("name") or "<MISSING>"
    postal = a.get("postalCode") or "<MISSING>"
    country_code = "CA"
    phone = a.get("phone") or "<MISSING>"
    latitude = js.get("geoPoint").get("latitude") or "<MISSING>"
    longitude = js.get("geoPoint").get("longitude") or "<MISSING>"
    if latitude == "0":
        latitude, longitude = "<MISSING>", "<MISSING>"
    hours = js.get("openingHours").get("weekDayOpeningList")
    tmp = []
    hours_of_operation = "<MISSING>"
    if hours:
        for h in hours:
            day = h.get("weekDay")
            try:
                opens = h.get("openingTime").get("formattedHour")
                closes = h.get("closingTime").get("formattedHour")
            except:
                opens, closes = "<MISSING>", "<MISSING>"
            line = f"{day} {opens} - {closes}"
            tmp.append(line)
        hours_of_operation = "; ".join(tmp)
    store_number = js.get("id") or "<MISSING>"
    loc_type = js.get("services")
    location_type = "<MISSING>"
    if loc_type:
        location_type = ", ".join(loc_type)

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
        location_type=location_type,
        latitude=latitude,
        longitude=longitude,
        hours_of_operation=hours_of_operation,
    )

    sgw.write_row(row)


def fetch_data(sgw: SgWriter):
    urls = get_urls()
    with futures.ThreadPoolExecutor(max_workers=1) as executor:
        future_to_url = {executor.submit(get_data, url, sgw): url for url in urls}
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.LOCATION_NAME,
                    SgRecord.Headers.LOCATION_TYPE,
                    SgRecord.Headers.STREET_ADDRESS,
                }
            )
        )
    ) as writer:
        fetch_data(writer)
