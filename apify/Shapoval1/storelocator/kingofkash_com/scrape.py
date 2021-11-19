from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://kingofkash.com"
    api_url = "https://kingofkash.com/locations/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//table[@class="locations"]')
    for d in div:

        page_url = "https://kingofkash.com/locations/"
        location_name = "".join(d.xpath(".//h4/text()"))
        street_address = "".join(d.xpath('.//a[contains(@href, "maps")]/text()'))
        state = (
            "".join(d.xpath('.//preceding::div[@class="location_header"][1]/h4/text()'))
            .split(",")[1]
            .split()[0]
            .strip()
        )
        postal = "".join(d.xpath('.//td[@class="c3"]/text()'))
        country_code = "US"
        city = (
            "".join(d.xpath('.//preceding::div[@class="location_header"][1]/h4/text()'))
            .split(",")[0]
            .strip()
        )
        text = "".join(d.xpath('.//td[@class="c1"]/a[contains(@href, "maps")]/@href'))
        try:
            if text.find("ll=") != -1:
                latitude = text.split("ll=")[1].split(",")[0]
                longitude = text.split("ll=")[1].split(",")[1].split("&")[0]
            else:
                latitude = text.split("@")[1].split(",")[0]
                longitude = text.split("@")[1].split(",")[1]
        except IndexError:
            latitude, longitude = "<MISSING>", "<MISSING>"

        phone = "".join(d.xpath('.//td[@class="c4"]/text()'))
        hours_of_operation = (
            " ".join(d.xpath('.//td[@class="c5"]/text()'))
            .replace("\n", "")
            .replace("Hours:", "")
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
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
