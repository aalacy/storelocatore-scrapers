from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address


def fetch_data(sgw: SgWriter):

    locator_domain = "https://honda.ru/"
    api_url = "https://auto.honda.ru/dealers/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//a[@class="dealers__item js_dealer-item"]')
    for d in div:
        city = "".join(d.xpath(".//@data-city"))
        if city.find("(") != -1:
            city = city.split("(")[0].strip()
        if "пос. Нагорный" in city:
            city = "пос. Нагорный"
        coords = "".join(d.xpath(".//@data-ya-map-coord"))
        store_number = "".join(d.xpath(".//@data-item-id"))
        location_type = (
            ",".join(d.xpath(".//@data-types"))
            .replace("[", "")
            .replace("]", "")
            .replace('"', "")
            .strip()
        )
        location_name = "".join(
            d.xpath('.//span[@class="dealers__name"]/text()')
        ).strip()
        ad = "".join(d.xpath('.//span[@class="dealers__address"]/text()'))
        a = parse_address(International_Parser(), ad)
        street_address = f"{a.street_address_1} {a.street_address_2}".replace(
            "None", ""
        ).strip()
        state = a.state or "<MISSING>"
        postal = a.postcode or "<MISSING>"
        country_code = "RU"
        page_url = "https://auto.honda.ru/dealers/"
        latitude = coords.split(",")[0].strip()
        longitude = coords.split(",")[1].strip()
        phone_list = d.xpath(
            f'.//following::div[@data-item-id="{store_number}"]//a[contains(@href, "tel")]/text()'
        )
        phone = "".join(phone_list[0]).replace(";", "").strip()
        hours = d.xpath(
            f'.//following::div[@data-item-id="{store_number}"]//div[@class="dealers-detail__meta-data"]/text()'
        )
        hours = list(filter(None, [a.strip() for a in hours]))
        try:
            hours_of_operation = (
                "".join(hours[0])
                .replace("<b>", "")
                .replace("</b>", "")
                .replace("Автосалон: ", "")
                .strip()
            )
        except:
            hours_of_operation = "<MISSING>"
        if hours_of_operation.find("Сервис:") != -1:
            hours_of_operation = hours_of_operation.split("Сервис: ")[0].strip()

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


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STORE_NUMBER}))
    ) as writer:
        fetch_data(writer)
