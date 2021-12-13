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
        locator_domain = "https://www.ippudo.com.hk"
        page_url = "https://www.ippudo.com.hk/branch"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
        }
        r = http.get(url=page_url, headers=headers)
        assert isinstance(r, httpx.Response)
        assert 200 == r.status_code
        tree = html.fromstring(r.text)
        div = tree.xpath('//div[@class="col-md-4 col-sm-12 col-xs-12"]')
        for d in div:

            location_name = "".join(
                d.xpath('.//div[@class="branch-details__district"]/text()')
            )
            ad = (
                " ".join(d.xpath('.//div[@class="branch-details__address"]/text()'))
                .replace("\n", "")
                .strip()
            )
            a = parse_address(International_Parser(), ad)
            street_address = f"{a.street_address_1} {a.street_address_2}".replace(
                "None", ""
            ).strip()
            state = a.state or "<MISSING>"
            postal = a.postcode or "<MISSING>"
            country_code = "".join(
                d.xpath(
                    './/preceding::div[@class="branch__topic site-color-heading"][1]/text()'
                )
            )
            city = location_name
            latitude = "".join(d.xpath(".//div/@data-lat"))
            longitude = "".join(d.xpath(".//div/@data-lng"))
            phone = (
                "".join(
                    d.xpath('.//div[@class="branch-details__contact"]/div[1]/a/text()')
                )
                .replace("\n", "")
                .strip()
            )
            hours_of_operation = (
                " ".join(
                    d.xpath('.//div[@class="branch-details__opening--hours"]/text()')
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
        SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        fetch_data(writer)
