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
        locator_domain = "https://www.ippudo.co.id"
        api_url = "https://www.ippudo.co.id/Store-List.htm"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
        }
        r = http.get(url=api_url, headers=headers)
        assert isinstance(r, httpx.Response)
        assert 200 == r.status_code
        tree = html.fromstring(r.text)
        div = tree.xpath('//div[./a[contains(@href, "/Store-List/")]]')
        for d in div:
            page_url = "".join(d.xpath('.//a[contains(@href, "/Store-List/")]/@href'))
            location_name = "".join(d.xpath('.//b/span[@itemprop="name"]/text()'))
            ad = (
                " ".join(
                    d.xpath('.//div[text()="Address"]/following-sibling::div/text()')
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
            country_code = "ID"
            city = a.city or "<MISSING>"
            map_link = "".join(d.xpath(".//iframe/@src"))
            latitude = map_link.split("!3d")[1].strip().split("!")[0].strip()
            longitude = map_link.split("!2d")[1].strip().split("!")[0].strip()
            phone = (
                " ".join(d.xpath('.//div[text()="Tel"]/following-sibling::div/text()'))
                .replace("\n", "")
                .strip()
            )
            hours_of_operation = (
                " ".join(
                    d.xpath(
                        './/div[text()="Opening Hours"]/following-sibling::div/text()'
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
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
