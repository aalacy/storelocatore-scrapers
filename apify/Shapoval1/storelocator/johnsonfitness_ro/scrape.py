from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://johnsonfitness.ro"
    api_url = "https://johnsonfitness.ro/contact/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)

    page_url = "https://johnsonfitness.ro/contact/"
    location_name = (
        "".join(tree.xpath('//div[@class="column-inner"]/p[1]/strong/text()'))
        .replace("\n", "")
        .strip()
    )
    street_address = (
        "".join(tree.xpath('//div[@class="column-inner"]/p[1]/text()'))
        .replace("\n", "")
        .strip()
    )
    country_code = "RO"
    city = "<MISSING>"
    if "Otopeni" in street_address:
        city = "Otopeni"
    map_link = "".join(tree.xpath("//iframe/@src"))
    latitude = map_link.split("!3d")[1].strip().split("!")[0].strip()
    longitude = map_link.split("!2d")[1].strip().split("!")[0].strip()
    phone = (
        "".join(
            tree.xpath('//div[@class="column-inner"]//a[contains(@href, "tel")]/text()')
        )
        .replace("\n", "")
        .strip()
    )
    hours_of_operation = (
        " ".join(tree.xpath('//p[./strong[text()="Orar"]]//text()'))
        .replace("\n", "")
        .replace("Orar :", "")
        .strip()
    )

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
        hours_of_operation=hours_of_operation,
    )

    sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
