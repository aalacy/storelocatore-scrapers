import httpx
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address


def fetch_data(sgw: SgWriter):
    with SgRequests() as http:
        locator_domain = "http://www.ippudo.com.sg"
        page_url = "http://www.ippudo.com.sg/store/"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
        }
        r = http.get(url=page_url, headers=headers)
        assert isinstance(r, httpx.Response)
        assert 200 == r.status_code
        tree = html.fromstring(r.text)
        div = tree.xpath('//div[@class="central_block"]')
        for d in div:

            location_name = (
                " ".join(d.xpath('.//h3[@class="title center"]//text()'))
                .replace("\n", "")
                .replace("  ", " ")
                .strip()
            )
            ad = (
                " ".join(
                    d.xpath('.//th[text()="Address"]/following-sibling::td/text()')
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
            country_code = "SG"
            city = a.city or "<MISSING>"
            map_link = "".join(d.xpath(".//iframe/@src"))
            latitude = map_link.split("!3d")[1].strip().split("!")[0].strip()
            longitude = map_link.split("!2d")[1].strip().split("!")[0].strip()
            phone = "".join(d.xpath('.//a[contains(@href, "tel")]/text()'))
            hours_of_operation = (
                " ".join(
                    d.xpath(
                        './/th[text()="Opening Hours"]/following-sibling::td/text()'
                    )
                )
                .replace("\n", "")
                .strip()
            )
            hours_of_operation = (
                " ".join(hours_of_operation.split())
                .replace("(Last Order 9:20pm)", "")
                .replace("(Last Order 2:30pm)", "")
                .replace("(Last Order 3:00pm)", "")
                .replace("(Last Call 8:30pm)", "")
                .replace("(Last Call 9:20pm)", "")
                .replace("(Last Order9:20pm)", "")
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
