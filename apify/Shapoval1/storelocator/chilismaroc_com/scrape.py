import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://chilismaroc.com/"
    api_url = "https://chilismaroc.com/location/?lang=en"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = (
        "".join(tree.xpath('//script[contains(text(), "var mmm_maps = ")]/text()'))
        .split("var mmm_maps = ")[1]
        .split(";")[0]
        .strip()
    )
    js = json.loads(div)

    for j in js:
        a = j.get("markers")
        for l in a:
            latitude = l.get("lat")
            longitude = l.get("lng")
            ids = l.get("id")
            session = SgRequests()
            headers = {
                "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
                "Accept": "*/*",
                "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
                "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                "Origin": "https://chilismaroc.com",
                "Connection": "keep-alive",
                "Referer": "https://chilismaroc.com/location/?lang=en",
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Site": "same-origin",
            }
            data = {"action": "mmm_async_content_marker", "id": f"{ids}"}

            r = session.post(
                "https://chilismaroc.com/wp-admin/admin-ajax.php",
                headers=headers,
                data=data,
            )
            tree = html.fromstring(r.text)
            page_url = "https://chilismaroc.com/location/?lang=en"
            location_name = "".join(tree.xpath("//h2/text()"))
            ad = "".join(tree.xpath('//li[@class="adresse"]/strong/text()'))
            street_address = " ".join(ad.split("-")[:-1])
            street_address = " ".join(street_address.split())
            country_code = "Morocco"
            city = ad.split("-")[-1].strip()
            phone = "".join(tree.xpath('//a[contains(@href, "tel")]/text()'))

            row = SgRecord(
                locator_domain=locator_domain,
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=SgRecord.MISSING,
                zip_postal=SgRecord.MISSING,
                country_code=country_code,
                store_number=SgRecord.MISSING,
                phone=phone,
                location_type=SgRecord.MISSING,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=SgRecord.MISSING,
                raw_address=ad,
            )

            sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
