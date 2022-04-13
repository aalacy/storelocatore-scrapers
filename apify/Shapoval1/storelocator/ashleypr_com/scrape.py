from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://ashleypr.com"
    api_url = "https://ashleypr.com/location.html"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[@class="StoreAddress"]')
    for d in div:

        page_url = "https://ashleypr.com/location.html"
        location_name = "".join(d.xpath("./a[1]/strong/text()"))
        info = d.xpath("./text()")
        info = list(filter(None, [a.strip() for a in info]))
        street_address = "".join(d.xpath("./a[1]/text()[1]")).replace("\n", "").strip()
        ad = "".join(d.xpath("./a[1]/text()[3]")).replace("\n", "").strip()
        postal = ad.split(",")[1].split()[1].strip()
        country_code = "PR"
        state = ad.split(",")[1].split()[0].strip()
        city = ad.split(",")[0].strip()
        latitude = (
            "".join(
                d.xpath(
                    f'.//preceding::script[contains(text(), "{location_name}")]/text()'
                )
            )
            .split(f"{location_name}")[2]
            .split("addMarker('")[1]
            .split("'")[0]
            .strip()
        )
        longitude = (
            "".join(
                d.xpath(
                    f'.//preceding::script[contains(text(), "{location_name}")]/text()'
                )
            )
            .split(f"{location_name}")[2]
            .split("addMarker('")[1]
            .split(",")[1]
            .replace("'", "")
            .strip()
        )
        phone = "".join(d.xpath('.//a[contains(@href, "tel")]/text()'))
        hours_of_operation = "".join(info).replace("\r\n", " ").strip() or "<MISSING>"

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
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
