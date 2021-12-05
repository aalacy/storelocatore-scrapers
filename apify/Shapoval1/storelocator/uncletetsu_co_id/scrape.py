from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address


def fetch_data(sgw: SgWriter):

    locator_domain = "http://uncletetsu.co.id/"
    page_url = "http://uncletetsu.co.id/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[@class="item"]')
    for d in div:
        ad = (
            " ".join(
                d.xpath('.//div[text()="Operating Hour:"]/preceding-sibling::text()')
            )
            .replace("\n", "")
            .strip()
        )
        if not ad:
            continue

        a = parse_address(International_Parser(), ad)
        street_address = f"{a.street_address_1} {a.street_address_2}".replace(
            "None", ""
        ).strip()
        if ad.find("MKG - Lantai LG - Unit 161a") != -1:
            street_address = (
                "".join(
                    d.xpath(
                        './/div[text()="Operating Hour:"]/preceding-sibling::div[text()="Address:"]/following-sibling::text()[1]'
                    )
                )
                .replace("\n", "")
                .strip()
                + " "
                + "".join(
                    d.xpath(
                        './/div[text()="Operating Hour:"]/preceding-sibling::div[text()="Address:"]/following-sibling::text()[4]'
                    )
                )
                .replace("\n", "")
                .split(",")[0]
                .strip()
            )
        if ad.find("TP - Lantai LG") != -1:
            street_address = (
                "".join(
                    d.xpath(
                        './/div[text()="Operating Hour:"]/preceding-sibling::div[text()="Address:"]/following-sibling::text()[1]'
                    )
                )
                .replace("\n", "")
                .strip()
                + " "
                + "".join(
                    d.xpath(
                        './/div[text()="Operating Hour:"]/preceding-sibling::div[text()="Address:"]/following-sibling::text()[4]'
                    )
                )
                .replace("\n", "")
                .strip()
            )
        if ad.find("PIM 1 - Lantai 2") != -1:
            street_address = (
                "".join(
                    d.xpath(
                        './/div[text()="Operating Hour:"]/preceding-sibling::div[text()="Address:"]/following-sibling::text()[1]'
                    )
                )
                .replace("\n", "")
                .strip()
                + " "
                + "".join(
                    d.xpath(
                        './/div[text()="Operating Hour:"]/preceding-sibling::div[text()="Address:"]/following-sibling::text()[4]'
                    )
                )
                .replace("\n", "")
                .strip()
            )
        if ad.find("PVJ - lantai GL") != -1:
            street_address = (
                "".join(
                    d.xpath(
                        './/div[text()="Operating Hour:"]/preceding-sibling::div[text()="Address:"]/following-sibling::text()[1]'
                    )
                )
                .replace("\n", "")
                .strip()
                + " "
                + "".join(
                    d.xpath(
                        './/div[text()="Operating Hour:"]/preceding-sibling::div[text()="Address:"]/following-sibling::text()[3]'
                    )
                )
                .replace("\n", "")
                .strip()
            )
        if ad.find("Lippo Mall Puri") != -1:
            street_address = (
                "".join(
                    d.xpath(
                        './/div[text()="Operating Hour:"]/preceding-sibling::div[text()="Address:"]/following-sibling::text()[1]'
                    )
                )
                .replace("\n", "")
                .replace("Lippo Mall Puri -", "")
                .strip()
                + " "
                + "".join(
                    d.xpath(
                        './/div[text()="Operating Hour:"]/preceding-sibling::div[text()="Address:"]/following-sibling::text()[3]'
                    )
                )
                .replace("\n", "")
                .strip()
            )

        state = a.state or "<MISSING>"
        postal = a.postcode or "<MISSING>"
        country_code = "ID"
        city = a.city or "<MISSING>"
        if ad.find("SMB - lantai GF") != -1:
            street_address = (
                "".join(
                    d.xpath(
                        './/div[text()="Operating Hour:"]/preceding-sibling::div[text()="Address:"]/following-sibling::text()[1]'
                    )
                )
                .replace("\n", "")
                .strip()
                + " "
                + "".join(
                    d.xpath(
                        './/div[text()="Operating Hour:"]/preceding-sibling::div[text()="Address:"]/following-sibling::text()[4]'
                    )
                )
                .replace("\n", "")
                .strip()
            )
            city = "Bekasi"
        if ad.find("Central Park Mall") != -1:
            street_address = (
                "".join(
                    d.xpath(
                        './/div[text()="Operating Hour:"]/preceding-sibling::div[text()="Address:"]/following-sibling::text()[1]'
                    )
                )
                .replace("\n", "")
                .replace("Central Park Mall -", "")
                .strip()
                + " "
                + "".join(
                    d.xpath(
                        './/div[text()="Operating Hour:"]/preceding-sibling::div[text()="Address:"]/following-sibling::text()[4]'
                    )
                )
                .replace("\n", "")
                .strip()
            )
        if ad.find("Pluit Village") != -1:
            street_address = (
                "".join(
                    d.xpath(
                        './/div[text()="Operating Hour:"]/preceding-sibling::div[text()="Address:"]/following-sibling::text()[1]'
                    )
                )
                .replace("\n", "")
                .replace("Pluit Village -", "")
                .strip()
                + " "
                + "".join(
                    d.xpath(
                        './/div[text()="Operating Hour:"]/preceding-sibling::div[text()="Address:"]/following-sibling::text()[4]'
                    )
                )
                .replace("\n", "")
                .split(",")[0]
                .strip()
            )
        hours_of_operation = (
            " ".join(
                d.xpath('.//div[text()="Operating Hour:"]/following-sibling::text()')
            )
            .replace("\n", "")
            .strip()
        )

        row = SgRecord(
            locator_domain=locator_domain,
            page_url=page_url,
            location_name=SgRecord.MISSING,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code=country_code,
            store_number=SgRecord.MISSING,
            phone=SgRecord.MISSING,
            location_type=SgRecord.MISSING,
            latitude=SgRecord.MISSING,
            longitude=SgRecord.MISSING,
            hours_of_operation=hours_of_operation,
            raw_address=ad,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
