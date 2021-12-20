from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.breadwinnerscafe.com"
    page_url = "https://www.breadwinnerscafe.com/locations"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[@class="_6lnTT"]/span')

    for d in div:

        location_name = "".join(d.xpath(".//text()"))
        if location_name.find("CATERING") != -1 or location_name.find("emplo") != -1:
            continue
        street_address = "".join(
            d.xpath('.//following::h2[@style="font-size:13px"][1]//text()')
        )
        ad = "".join(d.xpath('.//following::h2[@style="font-size:13px"][2]//text()'))
        phone = (
            "".join(d.xpath('.//following::h2[@style="font-size:13px"][3]//text()'))
            .replace("P:", "")
            .replace(" - ", "-")
            .strip()
        )
        state = ad.split(",")[1].strip().capitalize()
        postal = ad.split(",")[2].strip().capitalize()
        country_code = "US"
        city = ad.split(",")[0].strip().capitalize()
        hours_of_operation = (
            "".join(d.xpath('.//following::span[@style="font-weight:bold"][1]//text()'))
            + " "
            + "".join(
                d.xpath('.//following::span[@style="font-weight:bold"][2]//text()')
            )
        )
        hours_of_operation = (
            hours_of_operation
            + " "
            + "".join(
                d.xpath('.//following::span[@style="font-weight:bold"][3]//text()')
            )
            + " "
            + "".join(
                d.xpath('.//following::span[@style="font-weight:bold"][4]//text()')
            )
        )
        hours_of_operation = (
            hours_of_operation.replace("​ ​ ", "")
            .replace("​ ", "")
            .replace("CATERING", "")
            .strip()
        )
        if location_name.find("NORTHPARK CENTER") != -1:
            hours_of_operation = "".join(
                d.xpath('.//following::span[contains(text(), "SUN 9A-5P")]/text()')
            )
            street_address = "".join(
                d.xpath('.//following::div[@id="comp-jmjbydnm"]/h2[1]//text()')
            )
            ad = "".join(
                d.xpath('.//following::div[@id="comp-jmjbydnm"]/h2[2]//text()')
            )
            state = ad.split(",")[1].strip().capitalize()
            postal = ad.split(",")[2].strip().capitalize()
            country_code = "US"
            city = ad.split(",")[0].strip().capitalize()
            phone = (
                "".join(d.xpath('.//following::div[@id="comp-jmjbydnm"]/h2[3]//text()'))
                .replace("P:", "")
                .replace(" - ", "-")
                .strip()
            )

        hours_of_operation = (
            hours_of_operation.replace("BRUNCH:", "").replace("BRUNCH", "").strip()
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
            latitude=SgRecord.MISSING,
            longitude=SgRecord.MISSING,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
