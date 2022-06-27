import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://ashleyfurniture.kr/"
    page_url = "https://ashleyfurniture.kr/contact"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[@class="add_main"]')
    for d in div:

        location_name = "".join(d.xpath(".//h3//text()"))
        street_address = "".join(
            d.xpath('.//li[@class="location_address"]//text()')
        ).strip()
        ad = "".join(d.xpath('.//li[@class="location_city"]//text()')).strip()
        country_code = "KR"
        postal = ad.split(",")[1].split()[-1].strip()
        city = ad.split(",")[0].strip()
        state = ad.split(",")[1].split()[0].strip()
        phone = "".join(d.xpath('.//a[contains(@href, "tel")]//text()')).strip()
        js_block = "".join(d.xpath('.//following::input[@id="address_data"]/@value'))
        js = json.loads(js_block)
        latitude = js[0].get("latitude")
        longitude = js[0].get("longitude")
        hours = js[0].get("storeHours")
        hours_of_operation = "<MISSING>"
        if hours:
            a = html.fromstring(hours)
            hours_of_operation = (
                " ".join(a.xpath("//*//text()")).replace("\n", "").strip()
            )
            hours_of_operation = " ".join(hours_of_operation.split())

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
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
