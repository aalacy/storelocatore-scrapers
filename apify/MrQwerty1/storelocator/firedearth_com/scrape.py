from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def get_additional(page_url):
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)

    country = (
        "".join(
            tree.xpath(
                "//div[@class='amlocator-block amlocator-location-info']//span[contains(text(), ', ')]/text()"
            )
        )
        .split(", ")[-1]
        .strip()
    )
    phone = "".join(tree.xpath("//a[contains(@href, 'tel:')]/@href")).replace(
        "tel:", ""
    )

    _tmp = []
    hours = tree.xpath("//div[@class='amlocator-schedule-table']/div")
    for h in hours:
        day = "".join(h.xpath("./span[1]//text()")).strip()
        inter = "".join(h.xpath("./span[2]//text()")).strip()
        _tmp.append(f"{day}: {inter}")

    return country, phone, ";".join(_tmp)


def fetch_data(sgw: SgWriter):
    api = "https://www.firedearth.com/amlocator/index/ajax/"
    r = session.post(api, headers=headers, data=data)
    js = r.json()["items"]

    for j in js:
        latitude = j.get("lat")
        longitude = j.get("lng")
        store_number = j.get("id")
        source = j.get("popup_html") or "<html/>"
        d = html.fromstring(source)
        location_name = "".join(d.xpath(".//a[@class='amlocator-link']/text()")).strip()
        page_url = "".join(d.xpath(".//a[@class='amlocator-link']/@href"))
        line = d.xpath("./text()")
        line = list(filter(None, [l.strip() for l in line]))
        city = line.pop(0).replace("City:", "").strip()
        state = SgRecord.MISSING
        if ", " in city:
            city, state = city.split(", ")[:2]
        if city[-1].isdigit():
            city = state
            state = SgRecord.MISSING

        postal = line.pop(0).replace("Zip:", "").strip()
        street_address = line.pop(0).replace("Address:", "").strip()
        country, phone, hours_of_operation = get_additional(page_url)
        if "/" in phone:
            phone = phone.split("/")[0].strip()

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code=country,
            store_number=store_number,
            phone=phone,
            latitude=latitude,
            longitude=longitude,
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.firedearth.com/"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:96.0) Gecko/20100101 Firefox/96.0",
        "Accept": "*/*",
        "Accept-Language": "ru,en-US;q=0.7,en;q=0.3",
        "Accept-Encoding": "gzip, deflate, br",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "X-Requested-With": "XMLHttpRequest",
        "Origin": "https://www.firedearth.com",
        "Connection": "keep-alive",
        "Referer": "https://www.firedearth.com/find-a-showroom/",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "TE": "trailers",
    }

    data = {
        "lat": "0",
        "lng": "0",
        "radius": "",
        "product": "0",
        "category": "0",
        "sortByDistance": "1",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        fetch_data(writer)
