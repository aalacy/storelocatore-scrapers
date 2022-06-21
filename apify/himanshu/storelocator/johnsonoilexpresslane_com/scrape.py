from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.johnsonoilexpresslane.com/"
    api_url = "https://www.johnsonoilexpresslane.com/illinois"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[./h4[@class="font_4"]]')
    for d in div:

        page_url = "https://www.johnsonoilexpresslane.com/illinois"
        location_name = "".join(d.xpath("./h4//text()")).replace("\n", "").strip()
        street_address = "".join(
            d.xpath('./following-sibling::div[@class="_1Q9if"][1]//p[1]//text()')
        )
        if street_address.find("Daily") != -1:
            street_address = "".join(
                d.xpath('./preceding-sibling::div[@class="_1Q9if"][1]//p[1]//text()')
            )
        state = "IL"
        country_code = "US"
        city = location_name.capitalize()
        phone = (
            "".join(
                d.xpath('./following-sibling::div[@class="_1Q9if"][1]//p[2]//text()')
            )
            or "<MISSING>"
        )
        if phone == "<MISSING>":
            phone = (
                "".join(
                    d.xpath(
                        './preceding-sibling::div[@class="_1Q9if"][1]//p[2]//text()'
                    )
                )
                or "<MISSING>"
            )
        hours_of_operation = (
            " ".join(d.xpath('./following-sibling::div[@class="_1Q9if"][2]//text()'))
            .replace("\n", "")
            .strip()
        )
        if (
            street_address == "1320 17TH ST"
            or street_address == "928 SHOOTING PARK RD"
            or street_address == "3002 18TH AVE"
        ):
            hours_of_operation = (
                " ".join(
                    d.xpath('./following-sibling::div[@class="_1Q9if"][1]//text()')
                )
                .replace("\n", "")
                .strip()
            )
        if street_address.find("200 W S JOHNSON AVE") != -1:
            hours_of_operation = (
                " ".join(
                    d.xpath('./following-sibling::div[@class="_1Q9if"][3]//text()')
                )
                .replace("\n", "")
                .strip()
            )
        hours_of_operation = " ".join(hours_of_operation.split())

        row = SgRecord(
            locator_domain=locator_domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=SgRecord.MISSING,
            country_code=country_code,
            store_number=SgRecord.MISSING,
            phone=phone,
            location_type=SgRecord.MISSING,
            latitude=SgRecord.MISSING,
            longitude=SgRecord.MISSING,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)

    locator_domain = "https://www.johnsonoilexpresslane.com/"
    api_url = "https://www.johnsonoilexpresslane.com/iowa"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[./h4[@class="font_4"]]')
    for d in div:

        page_url = "https://www.johnsonoilexpresslane.com/iowa"
        location_name = "".join(d.xpath("./h4//text()")).replace("\n", "").strip()
        street_address = "".join(
            d.xpath('./following-sibling::div[@class="_1Q9if"][1]//p[1]//text()')
        )
        if street_address.find("Daily") != -1:
            street_address = "".join(
                d.xpath('./preceding-sibling::div[@class="_1Q9if"][1]//p[1]//text()')
            )
        state = "IA"
        country_code = "US"
        city = location_name.capitalize()
        phone = (
            "".join(
                d.xpath('./following-sibling::div[@class="_1Q9if"][1]//p[2]//text()')
            )
            or "<MISSING>"
        )
        if phone == "<MISSING>":
            phone = (
                "".join(
                    d.xpath(
                        './preceding-sibling::div[@class="_1Q9if"][1]//p[2]//text()'
                    )
                )
                or "<MISSING>"
            )
        hours_of_operation = (
            " ".join(d.xpath('./following-sibling::div[@class="_1Q9if"][2]//text()'))
            .replace("\n", "")
            .strip()
        )
        if hours_of_operation == "DAVENPORT":
            hours_of_operation = (
                " ".join(
                    d.xpath('./following-sibling::div[@class="_1Q9if"][1]//text()')
                )
                .replace("\n", "")
                .strip()
            )
        hours_of_operation = " ".join(hours_of_operation.split())

        row = SgRecord(
            locator_domain=locator_domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=SgRecord.MISSING,
            country_code=country_code,
            store_number=SgRecord.MISSING,
            phone=phone,
            location_type=SgRecord.MISSING,
            latitude=SgRecord.MISSING,
            longitude=SgRecord.MISSING,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
