from lxml import html
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgselenium.sgselenium import SgFirefox
from sgpostal.sgpostal import International_Parser, parse_address


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.harvey-norman.co.uk/"
    page_url = "https://www.harvey-norman.co.uk/store-finder.html"

    with SgFirefox() as driver:
        driver.get(page_url)
        a = driver.page_source
        tree = html.fromstring(a)
        div = tree.xpath('//div[@class="pinned-map map-and-details utility-border"]')
        for d in div:

            location_name = "".join(d.xpath(".//h3//text()"))
            ad = (
                " ".join(
                    d.xpath('.//h4[text()="Address"]/following-sibling::p[1]//text()')
                )
                .replace("\n", "")
                .strip()
            )
            ad = " ".join(ad.split())
            a = parse_address(International_Parser(), ad)
            street_address = (
                f"{a.street_address_1} {a.street_address_2}".replace("None", "").strip()
                or "<MISSING>"
            )
            state = a.state or "<MISSING>"
            postal = a.postcode or "<MISSING>"
            country_code = "UK"
            city = a.city or "<MISSING>"
            map_link = "".join(d.xpath(".//iframe/@src"))
            latitude = map_link.split("!3d")[1].strip().split("!")[0].strip()
            longitude = map_link.split("!2d")[1].strip().split("!")[0].strip()
            phone = (
                "".join(d.xpath('.//a[contains(@href, "tel")]//text()')) or "<MISSING>"
            )
            hours_of_operation = (
                " ".join(
                    d.xpath(
                        './/h4[contains(text(), "Hours")]/following-sibling::div[1]//text()'
                    )
                )
                .replace("\n", "")
                .strip()
            )
            hours_of_operation = " ".join(hours_of_operation.split()) or "<MISSING>"
            if hours_of_operation.find("*") != -1:
                hours_of_operation = hours_of_operation.split("*")[0].strip()

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
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
