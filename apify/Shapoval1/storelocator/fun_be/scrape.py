from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.fun.be"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
        "Accept": "*/*",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "X-Requested-With": "XMLHttpRequest",
        "Origin": "https://www.fun.be",
        "Connection": "keep-alive",
        "Referer": "https://www.fun.be/nl_BE/winkels/",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
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
        "https://www.fun.be/nl_BE/amlocator/index/ajax/", headers=headers, data=data
    )
    js = r.json()["items"]
    for j in js:
        store_number = j.get("id") or "<MISSING>"
        latitude = j.get("lat") or "<MISSING>"
        longitude = j.get("lng") or "<MISSING>"
        info = j.get("popup_html")
        a = html.fromstring(info)
        page_url = "".join(a.xpath('//a[@class="amlocator-link"]/@href'))
        location_name = "".join(a.xpath('//a[@class="amlocator-link"]/text()'))
        street_address = (
            "".join(a.xpath('//div[@class="amlocator-address"]/text()[1]'))
            .replace("\n", "")
            .strip()
        )
        ad = (
            "".join(a.xpath('//div[@class="amlocator-address"]/text()[2]'))
            .replace("\n", "")
            .strip()
        )
        postal = ad.split()[0].strip()
        country_code = "BE"
        city = " ".join(ad.split()[1:])
        phone = "".join(a.xpath('//a[contains(@href, "tel")]//text()')) or "<MISSING>"
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)

        hours_of_operation = (
            " ".join(
                tree.xpath(
                    '//div[@class="amlocator-schedule-table"]//div//span//text()'
                )
            )
            .replace("\n", "")
            .strip()
        )
        hours_of_operation = (
            " ".join(hours_of_operation.split()).replace("Vandaag open", "").strip()
            or "<MISSING>"
        )

        row = SgRecord(
            locator_domain=locator_domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=SgRecord.MISSING,
            zip_postal=postal,
            country_code=country_code,
            store_number=store_number,
            phone=phone,
            location_type=SgRecord.MISSING,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
            raw_address=f"{street_address} {ad}",
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STORE_NUMBER}))
    ) as writer:
        fetch_data(writer)
