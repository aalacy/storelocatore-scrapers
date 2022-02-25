from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://uberrito.com"
    page_url = "https://uberrito.com/locations"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//a[contains(text(), "View store details")]')

    for d in div:
        page_url = "".join(d.xpath(".//@href"))
        session = SgRequests()
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)

        location_name = "".join(tree.xpath('//h1[@itemprop="name"]/text()'))
        street_address = "".join(tree.xpath('//span[@itemprop="streetAddress"]/text()'))
        phone = (
            "".join(tree.xpath('//span[@itemprop="telephone"]/text()')) or "<MISSING>"
        )
        state = "".join(tree.xpath('//span[@itemprop="addressRegion"]/text()'))
        postal = "".join(tree.xpath('//span[@itemprop="postalCode"]/text()'))
        country_code = "US"
        city = "".join(tree.xpath('//span[@itemprop="addressLocality"]/text()'))
        text = "".join(tree.xpath('//a[contains(@href, "/maps/")]/@href'))
        try:
            if text.find("ll=") != -1:
                latitude = text.split("ll=")[1].split(",")[0]
                longitude = text.split("ll=")[1].split(",")[1].split("&")[0]
            else:
                latitude = text.split("@")[1].split(",")[0]
                longitude = text.split("@")[1].split(",")[1]
        except IndexError:
            latitude, longitude = "<MISSING>", "<MISSING>"
        hours_of_operation = (
            " ".join(tree.xpath('//time[@itemprop="openingHours"]//text()'))
            .replace("\n", "")
            .replace("   ", " ")
            .strip()
        )
        cms = "".join(tree.xpath('//img[@itemprop="image"]/@src'))
        if "Coming-Soon" in cms:
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
