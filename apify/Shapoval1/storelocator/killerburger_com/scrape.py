import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://killerburger.com/"
    api_url = "https://killerburger.com/locations/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[@class="location"]')
    for d in div:

        page_url = "".join(d.xpath('.//div[@class="heading"]/a/@href'))
        location_name = "".join(d.xpath('.//span[@class="thick-white"]/text()'))
        street_address = (
            "".join(d.xpath('.//div[@class="content"]/div[1]/text()'))
            .replace("\n", "")
            .strip()
        )
        ad = (
            " ".join(d.xpath('.//div[@class="content"]/div[2]/text()'))
            .replace("\n", " ")
            .strip()
        )
        state = ad.split(",")[1].split()[0].strip()
        try:
            postal = ad.split(",")[1].split()[1].strip()
        except:
            postal = "<MISSING>"
        country_code = "US"
        city = ad.split(",")[0].strip()
        jsblock = (
            "".join(
                tree.xpath('//script[contains(text(), "var KBLocations = ")]/text()')
            )
            .split("var KBLocations = ")[1]
            .split(";")[0]
        )
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        js = json.loads(jsblock)
        for j in js:
            title = j.get("name")
            if location_name == title:
                latitude = j.get("lat")
                longitude = j.get("lng")
        phone = "".join(d.xpath('.//span[@class="thin-red"]/text()'))
        a = d.xpath('.//p[contains(text(), "Open for")]/text()')
        hours_of_operation = (
            " ".join(a[1:])
            .replace("\n", " ")
            .replace("(New Hours)", "")
            .replace("Outdoor Seating Available too!", "")
            .replace("Open", "")
            .strip()
            or "<MISSING>"
        )
        if phone == "Coming Soon":
            phone = "<MISSING>"
            hours_of_operation = "Coming Soon"
        cms = "".join(
            d.xpath(
                './/p[contains(text(), "COMING")]/text() | .//p[contains(text(), "OPENING")]/text()'
            )
        )
        if cms:
            hours_of_operation = "Coming Soon"

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
