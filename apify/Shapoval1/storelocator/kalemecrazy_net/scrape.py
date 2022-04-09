from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://kalemecrazy.net/"
    api_url = "https://kalemecrazy.net/locations/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath("//div[./h5]")
    for d in div:

        location_name = "".join(d.xpath(".//h5//text()"))
        info = d.xpath(
            ".//h5/following-sibling::p//text() | .//h5/following-sibling::div//text()"
        )
        info = list(filter(None, [a.strip() for a in info]))
        street_address = info[0]
        if len(info) > 3:
            street_address = " ".join(info[:2])
        street_address = street_address.replace(",", "").strip()
        cms = "".join(
            d.xpath(
                './/following-sibling::div//*[contains(text(), "COMING SOON")]/text()'
            )
        )
        phone = "<MISSING>"
        if not cms:
            phone = "".join(info[-1]).strip()
        adr = " ".join(info)
        if not cms:
            adr = " ".join(info).split(f"{phone}")[0].strip()
        state = location_name.split("-")[0].strip()
        postal = adr.split()[-1].strip()
        country_code = "US"
        city = location_name.split("-")[1].strip()
        if city.find("/") != -1:
            city = city.split("/")[0].strip()
        urls = d.xpath(".//following-sibling::div//a[1]/@href") or "<MISSING>"
        page_url = (
            urls[0].replace("<", "").strip() or "https://kalemecrazy.net/locations/"
        )
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)
        latitude = (
            "".join(tree.xpath('//meta[@itemprop="latitude"]/@content')) or "<MISSING>"
        )
        longitude = (
            "".join(tree.xpath('//meta[@itemprop="longitude"]/@content')) or "<MISSING>"
        )
        if page_url != "https://kalemecrazy.net/locations/" and latitude != "<MISSING>":
            city = (
                "".join(tree.xpath('//span[@itemprop="addressLocality"]//text()'))
                .replace(".", "")
                .strip()
                or "<MISSING>"
            )
        hours_of_operation = "<MISSING>"
        hours = tree.xpath('//meta[@itemprop="openingHours"]/@content') or "<MISSING>"
        if hours != "<MISSING>":
            hours_of_operation = " ".join(hours[1:])
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
            raw_address=f"{street_address} {city}, {state} {postal}",
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
