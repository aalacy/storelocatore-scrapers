from lxml import html
from sgscrape.sgpostal import International_Parser, parse_address
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    page_url = "https://lucchese.com/pages/store-locator"
    session = SgRequests()

    r = session.get(page_url)
    tree = html.fromstring(r.text)
    block = tree.xpath('//div[@class="stores-wrapper"]')
    for b in block:
        ad = (
            " ".join(
                b.xpath(
                    './/div[@class="address-phone-wrapper"]//p[@class="store-address"]/text()'
                )
            )
            .replace("\n", "")
            .strip()
        )
        ad = " ".join(ad.split())
        a = parse_address(International_Parser(), ad)

        street_address = f"{a.street_address_1} {a.street_address_2}".replace(
            "None", ""
        ).strip()
        city = a.city or "<MISSING>"
        state = a.state or "<MISSING>"
        country_code = "US"
        postal = a.postcode or "<MISSING>"
        location_name = "".join(b.xpath(".//h2/text()")).replace("\n", "").strip()
        phone = (
            "".join(b.xpath('.//a[@class="store-phone"]/text()'))
            .replace("\n", "")
            .strip()
            or "<MISSING>"
        )
        text = "".join(b.xpath(".//a[@class='store-address']/@href"))
        try:
            if text.find("ll=") != -1:
                latitude = text.split("ll=")[1].split(",")[0]
                longitude = text.split("ll=")[1].split(",")[1].split("&")[0]
            else:
                latitude = text.split("@")[1].split(",")[0]
                longitude = text.split("@")[1].split(",")[1]
        except IndexError:
            latitude, longitude = "<MISSING>", "<MISSING>"
        location_type = "store"
        hours_of_operation = (
            " ".join(b.xpath('.//div[@class="store-hours-info"]/text()'))
            .replace("\n", " ")
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
            store_number=SgRecord.MISSING,
            phone=phone,
            location_type=location_type,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    locator_domain = "https://www.lucchese.com"
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
