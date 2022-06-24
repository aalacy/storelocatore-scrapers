from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.hfcu.info"
    page_url = "https://www.hfcu.info/about-us/locations-and-hours"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[@class="listbox"]')
    for d in div:

        location_name = "".join(d.xpath('.//span[@class="cuname"]/a/text()')).strip()
        street_address = (
            "".join(
                d.xpath('.//p[@class="locicons"]/following-sibling::p[1]/text()[1]')
            )
            .replace("\n", "")
            .strip()
        )
        ad = (
            "".join(
                d.xpath('.//p[@class="locicons"]/following-sibling::p[1]/text()[2]')
            )
            .replace("\n", "")
            .strip()
        )
        phone = (
            "".join(d.xpath('.//p[./strong[contains(text(), "Phone:")]]/text()'))
            .replace("\n", "")
            .strip()
        )
        if phone.find("MYCU") != -1:
            phone = phone.replace("MYCU ", "").strip()
        if phone.find("Ext") != -1:
            phone = phone.split("Ext")[0]
        state = ad.split(",")[1].split()[0].strip()
        postal = ad.split(",")[1].split()[-1].strip()
        country_code = "US"
        city = ad.split(",")[0].strip()
        try:
            ll = (
                "".join(
                    d.xpath('.//following::script[contains(text(), "LatLng")]/text()')
                )
                .split(location_name)[1]
                .split("'getDir(")[1]
                .split(");'")[0]
            )
        except IndexError:
            ll = (
                "".join(
                    d.xpath('.//following::script[contains(text(), "LatLng")]/text()')
                )
                .split(location_name)[2]
                .split("'getDir(")[1]
                .split(");'")[0]
            )
        latitude = ll.split(",")[0].strip()
        longitude = ll.split(",")[1].strip()
        hours = d.xpath(
            './/p[./u[contains(text(), "Lobby")]]//text() | .//h3[contains(text(), "Hours")]/following-sibling::p//text()'
        )
        hours = list(filter(None, [a.strip() for a in hours]))
        hours_of_operation = " ".join(hours) or "<MISSING>"
        if hours_of_operation.find("Lobby") != -1:
            hours_of_operation = hours_of_operation.split("Lobby")[1].split(
                "Drive-Thru"
            )[0]
        hours_of_operation = (
            hours_of_operation.replace(":", "")
            .replace("Drive-Thru Only", "")
            .replace("Available after hours by appointment.", "")
            .replace("30", ":30")
            .replace("Closed 1 hour for lunch daily", "")
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
            raw_address=f"{street_address} {ad}",
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {SgRecord.Headers.STREET_ADDRESS, SgRecord.Headers.LOCATION_NAME}
            )
        )
    ) as writer:
        fetch_data(writer)
