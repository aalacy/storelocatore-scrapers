from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://jysk.com.kw/"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
        "Accept": "*/*",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "X-Requested-With": "XMLHttpRequest",
        "Origin": "https://jysk.com.kw",
        "Connection": "keep-alive",
        "Referer": "https://jysk.com.kw/stores",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "TE": "trailers",
    }
    data = {
        "lat": "0",
        "lng": "0",
        "radius": "0",
        "product": "0",
        "category": "0",
        "sortByDistance": "1",
    }

    r = session.post(
        "https://jysk.com.kw/amlocator/index/ajax/", headers=headers, data=data
    )
    js = r.json()["items"]
    for j in js:

        latitude = j.get("lat")
        longitude = j.get("lng")
        store_number = j.get("id")
        info = j.get("popup_html")
        a = html.fromstring(info)

        location_name = "".join(a.xpath('//div[@class="amlocator-title"]//text()'))
        page_url = "".join(a.xpath('//div[@class="amlocator-title"]/a/@href'))
        info_addr = a.xpath("//*//text()")
        info_addr = list(filter(None, [b.strip() for b in info_addr]))
        street_address = "<MISSING>"
        for i in info_addr:
            if "Address" in i:
                street_address = str(i).replace("Address:", "").replace(",", "").strip()
        state = "<MISSING>"
        for i in info_addr:
            if "Governorate" in i:
                state = str(i).replace("Governorate:", "").strip()
        postal = "<MISSING>"
        country_code = "KW"
        city = "<MISSING>"
        for i in info_addr:
            if "Area" in i:
                city = str(i).replace("Area:", "").strip()
        info_addr_str = " ".join(info_addr)
        phone = info_addr_str.split("Telephone:")[1].strip()
        if phone.find("Email") != -1:
            phone = phone.split("Email")[0].strip()
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)

        hours_of_operation = (
            " ".join(
                tree.xpath('//div[@class="amlocator-schedule-table"]//div//text()')
            )
            .replace("\n", "")
            .strip()
        )
        hours_of_operation = " ".join(hours_of_operation.split()) or "<MISSING>"

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


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.LATITUDE}))) as writer:
        fetch_data(writer)
