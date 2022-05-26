from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://centralrockgym.com"
    api_url = "https://centralrockgym.com/locations/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath(
        '//div[@id="accordion"]//div[@class="panel-group"]/div[@class="thumbnail thumbnail-blank"]'
    )
    for d in div:

        slug = "".join(d.xpath('.//a[text()="Gym Page"]/@href'))
        page_url = f"https://centralrockgym.com{slug}"
        location_name = "".join(d.xpath(".//h3/text()")).replace("\n", "").strip()
        street_address = (
            "".join(d.xpath(".//address/text()[1]")).replace("\n", "").strip()
        )
        ad = "".join(d.xpath(".//address/text()[2]")).replace("\n", "").strip()
        state = ad.split(",")[1].split()[0].strip()
        postal = ad.split(",")[1].split()[1].strip()
        country_code = "US"
        city = ad.split(",")[0].strip()
        store_number = "".join(d.xpath(".//h3/span/text()")).strip()
        phone = "".join(d.xpath('.//a[contains(@href, "tel")]//text()')) or "<MISSING>"
        cms = "".join(d.xpath('.//*[contains(text(), "Coming Soon")]/text()'))

        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)
        text = "".join(tree.xpath('//a[contains(@href, "maps")]/@href'))
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
            " ".join(
                tree.xpath(
                    '//h1/following-sibling::div[1]//strong[text()="Hours"]/following-sibling::text()'
                )
            )
            .replace("\n", "")
            .strip()
            or "<MISSING>"
        )
        hours_of_operation = " ".join(hours_of_operation.split())
        if hours_of_operation.find("The minimum") != -1:
            hours_of_operation = hours_of_operation.split("The minimum")[0].strip()
        if hours_of_operation.find("*") != -1:
            hours_of_operation = hours_of_operation.split("*")[0].strip()
        if hours_of_operation.find("KIDS") != -1:
            hours_of_operation = hours_of_operation.split("KIDS")[0].strip()
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
            store_number=store_number,
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
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        fetch_data(writer)
