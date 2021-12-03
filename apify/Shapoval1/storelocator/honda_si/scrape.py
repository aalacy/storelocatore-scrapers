from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://honda.si"
    api_url = "https://honda.si/moja-honda/prodajno-servisna-mreza/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath(
        '//div[@class="col-sm-12 prodajalci_wrap"]/div[contains(@id, "prodaja")]'
    )
    for d in div:

        page_url = "".join(
            d.xpath('.//div[./img[contains(@src, "www")]]/following-sibling::a/@href')
        )
        location_name = "".join(d.xpath('.//strong[@class="ttt"]/text()'))
        street_address = (
            "".join(
                d.xpath(
                    './/div[./img[contains(@src, "location")]]/following-sibling::div[@class="prod_cont"]/text()[1]'
                )
            )
            .replace("\n", "")
            .strip()
        )
        ad = (
            "".join(
                d.xpath(
                    './/div[./img[contains(@src, "location")]]/following-sibling::div[@class="prod_cont"]/text()[2]'
                )
            )
            .replace("\n", "")
            .strip()
        )
        postal = ad.split()[0].strip()
        country_code = "SI"
        city = " ".join(ad.split()[1:]).strip()
        latitude = (
            "".join(tree.xpath(f'//script[contains(text(), "{location_name}")]/text()'))
            .split(f"{location_name}")[1]
            .split("lat:")[1]
            .split(",")[0]
            .strip()
        )
        longitude = (
            "".join(tree.xpath(f'//script[contains(text(), "{location_name}")]/text()'))
            .split(f"{location_name}")[1]
            .split("lng:")[1]
            .split("}")[0]
            .strip()
        )
        phone = (
            "".join(
                d.xpath(
                    './/div[@class="openKontakti"]/div[1]//div[@class="prod_cont"]/div[last()]/text()'
                )
            )
            or "<MISSING>"
        )

        row = SgRecord(
            locator_domain=locator_domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=SgRecord.MISSING,
            zip_postal=postal,
            country_code=country_code,
            store_number=SgRecord.MISSING,
            phone=phone,
            location_type=SgRecord.MISSING,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=SgRecord.MISSING,
            raw_address=f"{street_address} {ad}",
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        fetch_data(writer)
