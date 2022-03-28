from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://samandlouies.com"
    api_url = "https://samandlouies.com/locations/"
    session = SgRequests()

    r = session.get(api_url)
    tree = html.fromstring(r.text)
    block = tree.xpath('//a[./span/span[text()="Choose Location"]]')
    for b in block:
        page_url = "".join(b.xpath(".//@href"))
        street_address = (
            "".join(b.xpath(".//preceding::*[text()][1]/text()[1]"))
            .replace("Choose Location", "")
            .replace("\n", "")
            .strip()
            or "<MISSING>"
        )
        ad = (
            "".join(b.xpath(".//preceding::*[text()][1]/text()[2]"))
            .replace("Choose Location", "")
            .replace("\n", "")
            .strip()
            or "<MISSING>"
        )
        city = ad.split(",")[0].strip()
        state = ad.split(",")[1].split()[0].strip()
        country_code = "US"
        postal = ad.split(",")[1].split()[1].strip()
        location_name = "".join(b.xpath(".//preceding::h2[2]/text()"))
        r = session.get(page_url)
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
                    '//a[contains(text(), "AM")]/text() | //a[contains(text(), "am-")]/text() | //a[contains(text(), "am-")]/text() | //a[contains(text(), "Sunday")]/text() | //a[contains(text(), "Monday")]/text()'
                )
            )
            .replace("\n", "")
            .strip()
            or "<MISSING>"
        )
        hours_of_operation = " ".join(hours_of_operation.split())
        phone = (
            "".join(tree.xpath('//a[contains(@href, "tel")]/@href'))
            .replace("tel:", "")
            .replace("%20", "")
            .strip()
            or "<MISSING>"
        )
        cms = "".join(tree.xpath('//*[text()="COMING SOON"]/text()'))
        if cms:
            hours_of_operation = "Coming Soon"
        if page_url == "https://samandlouies.com/locations/corpus-christi-tx/":
            street_address = (
                "".join(tree.xpath('//a[contains(text(), "Blvd")]/text()'))
                .split("|")[0]
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
            raw_address=f"{street_address} {city}, {state} {postal}",
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        fetch_data(writer)
