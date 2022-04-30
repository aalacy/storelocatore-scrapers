from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.brooklinebank.com/"
    api_url = "https://www.brooklinebank.com/locations/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//a[contains(text(), "Location Details")]')
    for d in div:

        page_url = "".join(d.xpath(".//@href"))
        ad = "".join(d.xpath(".//preceding::span[1]/text()"))
        location_name = "".join(d.xpath(".//preceding::h2[1]/text()"))
        street_address = "".join(d.xpath(".//preceding::span[2]/text()"))
        state = ad.split(",")[1].split()[0].strip()
        postal = ad.split(",")[1].split()[1].strip()
        country_code = "US"
        city = ad.split(",")[0].strip()
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)
        info = tree.xpath("//span/text()")

        map_link = "".join(tree.xpath("//iframe/@src"))
        latitude = map_link.split("!3d")[1].strip().split("!")[0].strip()
        longitude = map_link.split("!2d")[1].strip().split("!")[0].strip()
        phone = "<MISSING>"
        for i in info:
            if "(" in i and ")" in i:
                phone = str(i)
        _tmp = []
        days = tree.xpath(
            '//table[./*[text()="Office Hours"]]//tr[position()>1]/th/text()'
        )
        opens = tree.xpath(
            '//table[./*[text()="Office Hours"]]//tr[position()>1]/td[1]/text()'
        )
        closes = tree.xpath(
            '//table[./*[text()="Office Hours"]]//tr[position()>1]/td[2]/text()'
        )
        for d, o, c in zip(days, opens, closes):
            _tmp.append(f"{d.strip()}: {o.strip()} - {c.strip()}")
        hours_of_operation = "; ".join(_tmp)

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
