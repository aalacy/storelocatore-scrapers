from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address


def fetch_data(sgw: SgWriter):

    locator_domain = "http://www.apc-korea.com/"
    api_url = "http://www.apc-korea.com/cs/store.do"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//li[@class="cms-store-list"]')
    for d in div:
        ids = (
            "".join(d.xpath("./@onclick"))
            .split("(")[1]
            .split(")")[0]
            .replace("'", "")
            .strip()
        )

        page_url = "http://www.apc-korea.com/cs/store.do"
        location_name = (
            "".join(d.xpath('./div[@class="shop-name"]/text()'))
            .replace("\n", "")
            .replace("\r", "")
            .strip()
        )
        ad = (
            "".join(
                d.xpath(
                    './div[@class="shop-name"]/div[1]/div[@class="shop-address"]/text()'
                )
            )
            .replace("\n", "")
            .strip()
        )
        a = parse_address(International_Parser(), ad)
        street_address = f"{a.street_address_1} {a.street_address_2}".replace(
            "None", ""
        ).strip()
        state = a.state or "<MISSING>"
        postal = a.postcode or "<MISSING>"
        country_code = "Korea"
        city = a.city or "<MISSING>"
        map_link = "".join(d.xpath(f'.//preceding::div[@id="map{ids}"]//iframe/@src'))
        latitude = map_link.split("!3d")[1].strip().split("!")[0].strip()
        longitude = map_link.split("!2d")[1].strip().split("!")[0].strip()
        phone = (
            "".join(
                d.xpath(
                    './div[@class="shop-name"]/div[1]/div[@class="shop-call"]/text()'
                )
            )
            .replace("\n", "")
            .replace("T", "")
            .strip()
        )
        hours_of_operation = (
            " ".join(
                d.xpath(
                    './div[@class="shop-name"]/div[1]/div[@class="shop-work"]/text()'
                )
            )
            .replace("\n", "")
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
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(
            SgRecordID({SgRecord.Headers.RAW_ADDRESS, SgRecord.Headers.LOCATION_NAME})
        )
    ) as writer:
        fetch_data(writer)
