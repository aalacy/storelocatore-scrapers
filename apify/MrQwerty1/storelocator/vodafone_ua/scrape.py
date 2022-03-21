import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from concurrent import futures


def get_token():
    r = session.get("https://www.vodafone.ua/support/search-shop")
    tree = html.fromstring(r.text)

    return "".join(tree.xpath("//meta[@name='csrf-token']/@content"))


def get_session():
    r = session.get("https://www.vodafone.ua/")

    return r.cookies.get("www_vodafone_ua_session")


def get_data(_id, sgw: SgWriter):
    data = json.dumps({"city_id": _id})
    r = session.post(
        "https://www.vodafone.ua/shops", data=data, headers=headers, cookies=cookies
    )

    if r.status_code == 500:
        return

    jso = r.json()
    js = jso["data"]
    c = jso["city"]
    city = c.get("label")

    for j in js:
        location_name = j.get("name")
        street_address = location_name
        p = j.get("position") or {}
        latitude = p.get("lat")
        longitude = p.get("lng")
        if latitude == 0:
            latitude, longitude = SgRecord.MISSING, SgRecord.MISSING
        hours_of_operation = j.get("work_hours") or ""
        hours_of_operation = " ".join(hours_of_operation.replace("<br>", ";").split())
        if "Згідно" in hours_of_operation:
            hours_of_operation = SgRecord.MISSING

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            country_code="UA",
            latitude=latitude,
            longitude=longitude,
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


def fetch_data(sgw: SgWriter):
    ids = [str(i) for i in range(1, 400)]

    with futures.ThreadPoolExecutor(max_workers=3) as executor:
        future_to_url = {executor.submit(get_data, _id, sgw): _id for _id in ids}
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":
    locator_domain = "https://www.vodafone.ua/"
    page_url = "https://www.vodafone.ua/en/support/search-shop"
    session = SgRequests(proxy_country="ua")

    headers = {
        "Content-Type": "application/json; charset=UTF-8",
        "X-CSRF-TOKEN": get_token(),
    }
    cookies = {"www_vodafone_ua_session": get_session()}

    with SgWriter(
        SgRecordDeduper(
            SgRecordID({SgRecord.Headers.STREET_ADDRESS, SgRecord.Headers.CITY})
        )
    ) as writer:
        fetch_data(writer)
