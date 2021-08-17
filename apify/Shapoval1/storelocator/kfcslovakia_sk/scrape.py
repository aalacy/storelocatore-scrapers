from lxml import html
from sgscrape.sgpostal import International_Parser, parse_address
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.kfcslovakia.sk"
    api_url = "https://www.kfcslovakia.sk/restauracie/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath(
        '//a[./span[contains(text(), "Reštaurácie")]]/following-sibling::div//ul/li/a'
    )
    for d in div:

        page_url = "".join(d.xpath(".//@href"))

        session = SgRequests()
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)

        location_name = "".join(tree.xpath("//h2/text()"))
        ad = (
            " ".join(
                tree.xpath(
                    '//div[./div/div/h4[text()="Adresa"]]/following-sibling::div[1]/div/p//text()'
                )
            )
            .replace("\n", "")
            .strip()
        )
        a = parse_address(International_Parser(), ad)
        street_address = f"{a.street_address_1} {a.street_address_2}".replace(
            "None", ""
        ).strip()
        if (
            page_url
            == "https://www.kfcslovakia.sk/restauracie/kfc-bory-mall-bratislava/"
        ):
            street_address = "Lamač 6780"
        state = a.state or "<MISSING>"
        postal = a.postcode or "<MISSING>"
        country_code = "SK"
        city = a.city or "<MISSING>"
        map_link = "".join(tree.xpath("//iframe/@src"))
        latitude = map_link.split("!3d")[1].strip().split("!")[0].strip()
        longitude = map_link.split("!2d")[1].strip().split("!")[0].strip()
        hours_of_operation = (
            " ".join(
                tree.xpath(
                    '//div[./div/div/h4[text()="Otváracie hodiny"]]/following-sibling::div[1]/div/p//text()'
                )
            )
            .replace("\n", "")
            .strip()
        )
        if hours_of_operation.find("RELAXX DRIVE") != -1:
            hours_of_operation = hours_of_operation.split("RELAXX DRIVE")[0].strip()
        if hours_of_operation.find("(") != -1:
            hours_of_operation = hours_of_operation.split("(")[0].strip()

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
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.GeoSpatialId)) as writer:
        fetch_data(writer)
