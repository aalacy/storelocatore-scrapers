from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address


def fetch_data(sgw: SgWriter):

    locator_domain = "https://xingfutang.ca/"
    api_url = "https://xingfutang.ca/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath(
        '//ul[@id="top-menu"]//a[text()="Stores"]/following-sibling::ul/li/a'
    )
    for d in div:

        page_url = "".join(d.xpath(".//@href"))
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)
        div = tree.xpath('//h4[@class="order-title"]')
        for d in div:

            ad = "".join(d.xpath(".//preceding::h4[1]/text()")).strip()
            location_name = "".join(d.xpath(".//preceding::h4[2]/text()")).strip()
            a = parse_address(International_Parser(), ad)
            street_address = f"{a.street_address_1} {a.street_address_2}".replace(
                "None", ""
            ).strip()
            state = a.state or "<MISSING>"
            postal = a.postcode or "<MISSING>"
            country_code = "CA"
            city = a.city or "<MISSING>"
            map_link = "".join(d.xpath(".//following::iframe[1]/@src"))
            latitude = map_link.split("!3d")[1].strip().split("!")[0].strip()
            longitude = map_link.split("!2d")[1].strip().split("!")[0].strip()
            phone = (
                "".join(
                    d.xpath(
                        './/preceding::strong[contains(text(), "Phone")][1]/following-sibling::a//text()'
                    )
                ).strip()
                or "<MISSING>"
            )
            hours_of_operation = (
                " ".join(
                    d.xpath(
                        './/preceding::strong[contains(text(), "Hours")][1]/following-sibling::text()'
                    )
                )
                .replace("\n", "")
                .strip()
            )
            if hours_of_operation.find("until") != -1:
                hours_of_operation = hours_of_operation.split("until")[0].strip()

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
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        fetch_data(writer)
