from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "http://tacobell.nl/"
    api_url = "http://tacobell.nl/en/locations/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[@class="find-Us-Branches"]')
    for d in div:

        page_url = "http://tacobell.nl/en/locations/"
        location_name = "".join(d.xpath(".//h5/text()"))
        ad = (
            " ".join(d.xpath('.//p[@class="findus_addr"]/text()'))
            .replace("\r\n", "")
            .replace("\n", "")
            .strip()
        )
        street_address = ad.split(",")[0].strip()
        state = ad.split(",")[1].split()[1].strip()
        postal = ad.split(",")[1].split()[0].strip()
        country_code = "Netherlands"
        city = ad.split()[-1].strip()
        latitude = (
            "".join(
                d.xpath(
                    './/div[@class="findUs-Branch-Address"]/following-sibling::a[1]/@href'
                )
            )
            .split("q=")[1]
            .split(",")[0]
            .strip()
        )
        longitude = (
            "".join(
                d.xpath(
                    './/div[@class="findUs-Branch-Address"]/following-sibling::a[1]/@href'
                )
            )
            .split("q=")[1]
            .split(",")[1]
            .strip()
        )
        phone = "".join(d.xpath('.//a[contains(@href, "tel")]/text()'))
        if phone == "NA":
            phone = "<MISSING>"
        hours_of_operation = (
            "".join(d.xpath('.//p[@class="opening_hours"]/text()'))
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
        SgRecordDeduper(SgRecordID({SgRecord.Headers.LOCATION_NAME}))
    ) as writer:
        fetch_data(writer)
