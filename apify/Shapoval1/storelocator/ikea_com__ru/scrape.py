from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address


def fetch_data(sgw: SgWriter):
    session = SgRequests()
    locator_domain = "https://www.ikea.com/ru/ru/"
    api_url = "https://www.ikea.com/ru/ru/stores/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//a[@class="pub__btn pub__btn--small pub__btn--secondary"]')
    for d in div:

        page_url = "".join(d.xpath(".//@href"))
        session = SgRequests()
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)

        ad = (
            " ".join(
                tree.xpath(
                    '//strong[contains(text(), "Адрес магазина:")]/following-sibling::text() | //strong[contains(text(), "Адрес:")]/following-sibling::text() | //p[./strong[contains(text(), "Адрес:")]]/following-sibling::p[1]//text() | //p[./strong[contains(text(), "Адрес студии:")]]/text()'
                )
            )
            .replace("\n", "")
            .strip()
        )
        if page_url == "https://www.ikea.com/ru/ru/stores/tyumen/":
            ad = (
                " ".join(
                    tree.xpath(
                        '//strong[contains(text(), "Адрес студии:")]/following-sibling::text()'
                    )
                )
                .replace("\n", "")
                .strip()
            )
        if ad.find("Время") != -1:
            ad = ad.split("Время")[0].strip()
        if ad.find("Ежедневно") != -1:
            ad = ad.split("Ежедневно")[0].strip()
        location_name = "".join(tree.xpath("//h1/text()"))
        a = parse_address(International_Parser(), ad)
        street_address = f"{a.street_address_1} {a.street_address_2}".replace(
            "None", ""
        ).strip()
        street_address = (
            street_address.replace("Поселок Сосенское", "")
            .replace("Cело Федяково", "")
            .replace("Или 41 Км Мкад", "")
            .strip()
        )
        state = a.state or "<MISSING>"
        postal = a.postcode or "<MISSING>"
        country_code = "RU"
        city = a.city or "<MISSING>"
        map_link = "".join(tree.xpath("//iframe/@src"))
        latitude = map_link.split("!3d")[1].strip().split("!")[0].strip()
        longitude = map_link.split("!2d")[1].strip().split("!")[0].strip()
        hours_of_operation = (
            " ".join(
                tree.xpath(
                    '//strong[contains(text(), "Время работы магазина:")]/following-sibling::text()'
                )
            )
            .replace("\n", "")
            .strip()
            or "<MISSING>"
        )
        if hours_of_operation == "<MISSING>":
            hours_of_operation = (
                " ".join(
                    tree.xpath(
                        '//strong[contains(text(), "Время работы магазина")]/following-sibling::text()'
                    )
                )
                .replace("\n", "")
                .strip()
                or "<MISSING>"
            )
        if hours_of_operation == "<MISSING>":
            hours_of_operation = (
                " ".join(
                    tree.xpath(
                        '//strong[contains(text(), "Время работы")]/following-sibling::text()'
                    )
                )
                .replace("\n", "")
                .strip()
                or "<MISSING>"
            )
        if hours_of_operation == "<MISSING>":
            hours_of_operation = (
                " ".join(
                    tree.xpath(
                        '//p[./strong[contains(text(), "Время работы")]]/following-sibling::p[1]/text()'
                    )
                )
                .replace("\n", "")
                .strip()
                or "<MISSING>"
            )
        if hours_of_operation == "<MISSING>":
            hours_of_operation = (
                " ".join(
                    tree.xpath('//p[./strong[contains(text(), "Магазин (")]]/text()')
                )
                .replace("\n", "")
                .strip()
                or "<MISSING>"
            )

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
            phone=SgRecord.MISSING,
            location_type=SgRecord.MISSING,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
            raw_address=ad,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        fetch_data(writer)
