from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.spiceandtea.com/"
    api_url = "https://www.spiceandtea.com/where-to-buy"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[@class="amlocator-store-desc"]')
    for d in div:

        page_url = "".join(d.xpath('.//a[text()="More Info"]/@href'))
        location_name = "".join(
            d.xpath('.//div[@class="amlocator-title"]/text()')
        ).strip()
        info = d.xpath('.//div[@class="amlocator-title"]/following-sibling::text()')
        info = list(filter(None, [a.strip() for a in info]))
        street_address = "<MISSING>"
        for i in info:
            if "Address" in i:
                street_address = "".join(i).replace("Address:", "").strip()
        if street_address.find("(") != -1:
            street_address = street_address.split("(")[0].strip()
        state = "<MISSING>"
        for i in info:
            if "State" in i:
                state = "".join(i).replace("State:", "").strip() or "<MISSING>"
        postal = "<MISSING>"
        for i in info:
            if "Zip" in i:
                postal = (
                    "".join(i).replace("Zip:", "").replace("*", "").strip()
                    or "<MISSING>"
                )
        country_code = "US"
        city = "<MISSING>"
        for i in info:
            if "City" in i:
                city = "".join(i).replace("City:", "").strip() or "<MISSING>"

        if page_url == "https://www.spiceandtea.com/sedona":
            state = "".join(info[-2]).replace("State:", "").strip()
        hours_of_operation = (
            " ".join(d.xpath('.//div[@class="amlocator-week"]/div/div//text()'))
            .replace("\n", "")
            .strip()
            or "<MISSING>"
        )
        hours_of_operation = " ".join(hours_of_operation.split())
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)
        text = "".join(tree.xpath('//a[text()="Get Directions"]/@href'))
        try:
            if text.find("ll=") != -1:
                latitude = text.split("ll=")[1].split(",")[0]
                longitude = text.split("ll=")[1].split(",")[1].split("&")[0]
            else:
                latitude = text.split("@")[1].split(",")[0]
                longitude = text.split("@")[1].split(",")[1]
        except IndexError:
            latitude, longitude = "<MISSING>", "<MISSING>"
        phone = "".join(tree.xpath('//a[contains(@href, "tel")]/text()')) or "<MISSING>"
        cms = "".join(tree.xpath('//div[contains(text(), "coming soon")]/text()'))
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
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        fetch_data(writer)
