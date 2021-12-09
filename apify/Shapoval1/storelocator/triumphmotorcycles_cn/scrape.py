from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.triumphmotorcycles.cn/"
    api_url = "https://www.triumphmotorcycles.cn/dealers"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[contains(@class, "dealer-item")]')
    for d in div:

        page_url = "https://www.triumphmotorcycles.cn/dealers"
        location_name = "".join(d.xpath(".//h3/text()"))
        ad = "".join(d.xpath('.//p[@class="address"]/text()'))
        a = parse_address(International_Parser(), ad)
        street_address = f"{a.street_address_1} {a.street_address_2}".replace(
            "None", ""
        ).strip()
        state = "".join(d.xpath(".//@data-province"))
        postal = a.postcode or "<MISSING>"
        country_code = "CH"
        city = "".join(d.xpath(".//@data-city"))
        store_number = "".join(d.xpath(".//@data-index"))
        longitude = (
            "".join(
                d.xpath(
                    f'.//following::script[contains(text(), "dituContent-{store_number}")]/text()'
                )
            )
            .split(f"dituContent-{store_number}")[1]
            .split("BMap.Point(")[1]
            .split(",")[0]
            .strip()
        )
        latitude = (
            "".join(
                d.xpath(
                    f'.//following::script[contains(text(), "dituContent-{store_number}")]/text()'
                )
            )
            .split(f"dituContent-{store_number}")[1]
            .split("BMap.Point(")[1]
            .split(",")[1]
            .split(")")[0]
            .strip()
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
            store_number=store_number,
            phone=SgRecord.MISSING,
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
        SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        fetch_data(writer)
