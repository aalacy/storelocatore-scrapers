from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address


def fetch_data(sgw: SgWriter):

    locator_domain = "https://chilisphilippines.com/"
    api_url = "https://chilisphilippines.com/locations/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//article[contains(@id, "ls_location")]')
    for d in div:

        page_url = "https://chilisphilippines.com/locations/"
        location_name = "".join(d.xpath('.//h2[@class="title"]/text()'))
        ad = (
            " ".join(d.xpath('.//div[@class="desc"]/p/text()'))
            .replace("\n", "")
            .strip()
        )
        a = parse_address(International_Parser(), ad)
        street_address = f"{a.street_address_1} {a.street_address_2}".replace(
            "None", ""
        ).strip()
        postal = a.postcode or "<MISSING>"
        country_code = "Philippines"
        city = ad.split(",")[-1].replace("City", "").strip()
        try:
            latitude = (
                "".join(
                    tree.xpath(f'//script[contains(text(), "{location_name}")]/text()')
                )
                .split(f'"{location_name}"')[1]
                .split(",")[1]
                .strip()
            )
            longitude = (
                "".join(
                    tree.xpath(f'//script[contains(text(), "{location_name}")]/text()')
                )
                .split(f'"{location_name}"')[1]
                .split(",")[2]
                .strip()
            )
        except:
            latitude, longitude = "<MISSING>", "<MISSING>"
        phone = "".join(
            d.xpath(
                './/div[@class="maplink_phone"]/a[contains(@href, "tel")][1]/text()'
            )
        )
        hours_of_operation = (
            " ".join(
                d.xpath(
                    './/div[contains(text(), "Opening Hours")]/following-sibling::div//text()'
                )
            )
            .replace("\n", "")
            .strip()
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
