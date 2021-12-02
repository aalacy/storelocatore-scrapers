import httpx
import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://triumph.granmoto.ru/"
    api_url = "https://triumph.granmoto.ru/dealers"
    with SgRequests() as http:

        r = http.get(url=api_url)
        assert isinstance(r, httpx.Response)
        assert 200 == r.status_code
        tree = html.fromstring(r.text)
        div = tree.xpath('//div[contains(@class, "list-group-item ")]')
        for d in div:
            location_name = "".join(
                d.xpath('.//h5[@class="js__shop_name mb-1"]/text()')
            )
            page_url = "https://triumph.granmoto.ru/dealers"
            city = (
                "".join(d.xpath("./p[1]/text()[1]"))
                .replace("\n", "")
                .replace(",", "")
                .strip()
            )
            street_address = (
                "".join(d.xpath("./p[1]/text()[2]")).replace("\n", "").strip()
            )
            phone = (
                "".join(d.xpath('.//a[contains(@href, "tel")]//text()'))
                .replace("Тел:", "")
                .replace("\n", "")
                .strip()
                or "<MISSING>"
            )
            if phone == "<MISSING>":
                phone = (
                    "".join(d.xpath('.//p[contains(text(), "Тел")]//text()'))
                    .replace("Телефон:", "")
                    .replace("\n", "")
                    .strip()
                    or "<MISSING>"
                )
            if phone.count("+") == 2:
                phone = "+" + " " + phone.split("+")[1].strip()
            hours_of_operation = (
                " ".join(
                    d.xpath('.//*[text()="Часы работы"]/following-sibling::p/text()')
                )
                .replace("\n", "")
                .replace("\r", "")
                .strip()
            )
            hours_of_operation = " ".join(hours_of_operation.split())
            if hours_of_operation.find("*") != -1:
                hours_of_operation = hours_of_operation.split("*")[0].strip()
            js_block = "".join(d.xpath("./@data-map"))
            country_code = "RU"
            js = json.loads(js_block)
            latitude = js.get("lat")
            longitude = js.get("long")
            location_type = "<MISSING>"
            if location_name.find("СЕРВИСНЫЙ ЦЕНТР") != -1:
                location_type = "service center"

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
                location_type=location_type,
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
