from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import USA_Best_Parser, parse_address
from concurrent import futures


def get_urls():
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0",
    }
    r = session.get("https://www.larosas.com/sitemap.xml", headers=headers)
    tree = html.fromstring(r.content)
    return tree.xpath("//url/loc[contains(text(), '/locations/')]/text()")


def get_data(url, sgw: SgWriter):
    locator_domain = "https://www.larosas.com/"
    page_url = "".join(url)
    slug = page_url.split("/")[-1].strip()

    session = SgRequests()
    cookies = {
        "ARRAffinity": "3772d17e7d4181d33dc3e0adc3afe14a56f68e1300716d41e4d3fabc64869006",
        "ARRAffinitySameSite": "3772d17e7d4181d33dc3e0adc3afe14a56f68e1300716d41e4d3fabc64869006",
        "ai_user": "btJHw|2022-05-29T11:12:49.742Z",
        "_gcl_au": "1.1.354208788.1653822770",
        "_ga_XQLV2EFWD7": "GS1.1.1653822769.1.1.1653822920.0",
        "_ga": "GA1.1.1278483196.1653822770",
        "_scid": "5d695c18-e88a-4b1b-b3a0-cc653e321000",
        "_gid": "GA1.2.933811264.1653822771",
        "_tt_enable_cookie": "1",
        "_ttp": "178888cf-72fc-4abb-82da-73d932eca41f",
        "_sctr": "1|1653771600000",
        "ai_session": "EbnFW|1653822770814|1653822907712",
        "_fbp": "fb.1.1653822771010.958854286",
        ".AspNetCore.Antiforgery.w5W7x28NAIs": "CfDJ8Cr3cY5hsCtFsO8Yv7yKxa2QMNubecgSsDF0nzeUfc6i6tg8ysO3MnuRi2K278iojTkqP7NBjK8004K6rwbxFnn9Bu2xB90pYNyV8Lkrb9L65-FtlrFBplsx8ps0fAF39z79-5SsFQwpyt9HXOre2FA",
        "_gat": "1",
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
        "Accept": "*/*",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "RequestVerificationToken": "CfDJ8Cr3cY5hsCtFsO8Yv7yKxa1K1Gu_e7o7PI2S-61BSOWnApluUoLbSZ6mhDqK4fOM88g7w-vX2oOwpUFon2-h7oDE8uuMidO__tMpM-xijAANE9Qu-Ry-pAmuHt0kmode-D37zd9Bf0uzmgSrQQfzV_Q",
        "X-Requested-With": "XMLHttpRequest",
        "Origin": "https://www.larosas.com",
        "Connection": "keep-alive",
        "Referer": f"{page_url}",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "Cache-Control": "max-age=0",
    }

    params = {
        "handler": "GetLocationBySlug",
    }

    data = {
        "slug": f"{slug}",
    }

    r = session.post(
        "https://www.larosas.com/api/locations",
        params=params,
        headers=headers,
        data=data,
        cookies=cookies,
    )
    js = r.json()
    ad = js.get("address")
    a = parse_address(USA_Best_Parser(), ad)
    street_address = (
        f"{a.street_address_1} {a.street_address_2}".replace("None", "").strip()
        or "<MISSING>"
    )
    state = a.state or "<MISSING>"
    postal = a.postcode or "<MISSING>"
    country_code = "US"
    city = a.city or "<MISSING>"
    location_name = js.get("name") or "<MISSING>"
    phone = js.get("phone") or "<MISSING>"
    if phone == "888-LAROSAS":
        phone = "<MISSING>"
    hours_of_operation = js.get("diningRoomHours") or "<MISSING>"
    hours_of_operation = (
        str(hours_of_operation).replace("<br/>", " ").replace("<br>", " ").strip()
    )
    latitude = js.get("latitude") or "<MISSING>"
    longitude = js.get("longitude") or "<MISSING>"

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
        raw_address=ad,
    )

    sgw.write_row(row)


def fetch_data(sgw: SgWriter):
    urls = get_urls()
    with futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(get_data, url, sgw): url for url in urls}
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        fetch_data(writer)
