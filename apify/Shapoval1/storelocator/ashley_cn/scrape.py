from lxml import html
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgselenium.sgselenium import SgFirefox
from sgpostal.sgpostal import International_Parser, parse_address


def fetch_data(sgw: SgWriter):

    locator_domain = "https://ashley.cn"
    page_url = "https://ashley.cn/about/store"

    with SgFirefox() as driver:
        driver.get(page_url)
        a = driver.page_source
        tree = html.fromstring(a)
        div = tree.xpath('//div[@class="store-address"]')
        for d in div:

            location_name = "".join(d.xpath('.//h4[@class="city-name"]/text()'))
            ad = "".join(d.xpath('.//div[@class="address"]/p/text()'))
            a = parse_address(International_Parser(), ad)
            street_address = f"{a.street_address_1} {a.street_address_2}".replace(
                "None", ""
            ).strip()
            state = a.state or "<MISSING>"
            postal = a.postcode or "<MISSING>"
            country_code = "CN"
            city = location_name.split("·")[0].strip()
            phone = "".join(d.xpath('.//div[@class="telphone"]/p/text()'))
            ll = (
                "".join(
                    d.xpath(f'.//following::script[contains(text(), "{phone}")]/text()')
                )
                .split(f"{phone}")[1]
                .split("position")[1]
                .split("isshow")[0]
                .replace("\\", "")
                .replace('"', "")
                .replace(":", "")
                .strip()
            )
            latitude = ll.split(",")[0].strip()
            longitude = ll.split(",")[1].strip()
            hours_of_operation = (
                " ".join(d.xpath('.//div[@class="business-hours"]/p/text()'))
                .replace("\n", " ")
                .replace("\r", "")
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
                zip_postal=postal,
                country_code=country_code,
                store_number=SgRecord.MISSING,
                phone=phone,
                location_type=SgRecord.MISSING,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hours_of_operation,
                raw_address=ad,
            )

            sgw.write_row(row)


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        fetch_data(writer)
