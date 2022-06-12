from lxml import html
from sgscrape.sgpostal import International_Parser, parse_address
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    api_url = "https://sangsters.com/apps/store-locator/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[./a[text()="More Info"]]')
    for d in div:
        page_url = locator_domain + "".join(d.xpath('.//a[text()="More Info"]/@href'))
        location_name = "".join(d.xpath(".//b/text()"))
        ad = (
            " ".join(d.xpath(".//b/following-sibling::text()"))
            .replace("\r\n", "")
            .strip()
        )
        ad = " ".join(ad.split())
        if ad.find("(204)") != -1:
            ad = ad.split("(204)")[0].strip()
        a = parse_address(International_Parser(), ad)
        street_address = f"{a.street_address_1} {a.street_address_2}".replace(
            "None", ""
        ).strip()
        state = a.state or "<MISSING>"
        postal = a.postcode or "<MISSING>"
        country_code = "CA"
        city = a.city or "<MISSING>"
        if location_name.find("SK - Tisdale - Tisdale Mall") != -1:
            street_address = (
                "".join(d.xpath(".//b/following-sibling::text()[2]"))
                .replace("\n", "")
                .strip()
            )
            city = (
                "".join(d.xpath(".//b/following-sibling::text()[3]"))
                .replace("\n", "")
                .split(",")[0]
                .strip()
            )
            state = (
                "".join(d.xpath(".//b/following-sibling::text()[3]"))
                .replace("\n", "")
                .split(",")[1]
                .strip()
            )
            postal = (
                "".join(d.xpath(".//b/following-sibling::text()[4]"))
                .replace("\n", "")
                .strip()
            )
        phone = (
            "".join(
                d.xpath(
                    './/a[contains(@href, "tel")]/text() | .//b/following::text()[5]'
                )
            ).strip()
            or "<MISSING>"
        )

        info = (
            " ".join(d.xpath(".//following-sibling::div[1]//text()"))
            .replace("\r\n", "")
            .strip()
        )
        if page_url == "https://sangsters.com/pages/sk-saskatoon-the-center":
            page_url = "https://sangsters.com/apps/store-locator/"
        session = SgRequests()
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)

        map_link = "".join(tree.xpath("//iframe/@src"))
        try:
            latitude = map_link.split("!3d")[1].strip().split("!")[0].strip()
            longitude = map_link.split("!2d")[1].strip().split("!")[0].strip()
        except:
            latitude, longitude = "<MISSING>", "<MISSING>"
        hours_of_operation = (
            " ".join(
                tree.xpath(
                    '//strong[text()="Address"]/preceding-sibling::text() | //strong[text()="Address"]/preceding-sibling::*/text()'
                )
            )
            or "<MISSING>"
        )

        if hours_of_operation != "<MISSING>":
            hours_of_operation = " ".join(hours_of_operation.split())
        hours_of_operation = (
            hours_of_operation.replace("Regular Store Hours", "")
            .replace(" ( ) ", " ")
            .strip()
        )
        if "Temporary closed" in info:
            hours_of_operation = "Temporary closed"
        if "Closed" in info:
            hours_of_operation = "Closed"

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
    locator_domain = "https://sangsters.com"
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
