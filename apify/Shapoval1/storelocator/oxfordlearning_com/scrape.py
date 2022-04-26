from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.oxfordlearning.com"
    api_url = "https://www.oxfordlearning.com/locations/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[@class="location-item-content"]')
    for d in div:

        page_url = "".join(d.xpath('.//a[contains(text(), "Centre Details")]/@href'))
        if page_url == "https://oxfordlearning.cn":
            continue
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)

        location_name = (
            " ".join(tree.xpath('//h1[@itemprop="name"]//text()'))
            .replace("\n", "")
            .strip()
            or "<MISSING>"
        )
        location_type = "<MISSING>"
        ad = (
            " ".join(tree.xpath('//span[@itemprop="streetAddress"]//text()'))
            .replace("\n", "")
            .strip()
            or "<MISSING>"
        )
        a = parse_address(International_Parser(), ad)
        street_address = (
            f"{a.street_address_1} {a.street_address_2}".replace("None", "").strip()
            or "<MISSING>"
        )
        if street_address == "<MISSING>" or street_address.isdigit():
            street_address = ad
        state = (
            " ".join(tree.xpath('//span[@itemprop="addressRegion"]//text()'))
            .replace("\n", "")
            .strip()
            or "<MISSING>"
        )
        postal = (
            " ".join(tree.xpath('//span[@itemprop="postalCode"]//text()'))
            .replace("\n", "")
            .strip()
            or "<MISSING>"
        )
        country_code = "CA"
        city = (
            " ".join(tree.xpath('//span[@itemprop="addressLocality"]//text()'))
            .replace("\n", "")
            .replace(",", "")
            .strip()
            or "<MISSING>"
        )
        phone = (
            "".join(
                tree.xpath(
                    '//div[@class="location-phone"]//a[contains(@href, "tel")]//text()'
                )
            )
            .replace("\n", "")
            .strip()
            or "<MISSING>"
        )
        ll = "".join(
            tree.xpath('//script[contains(text(), "var olc_elements =")]/text()')
        )
        try:
            latitude = (
                ll.split(f"{phone}")[1].split('"latitude":"')[1].split('"')[0].strip()
            )
            longitude = (
                ll.split(f"{phone}")[1].split('"longitude":"')[1].split('"')[0].strip()
            )
        except:
            latitude, longitude = "<MISSING>", "<MISSING>"
        if phone.find(".LIRE") != -1:
            phone = phone.replace(".LIRE", "").strip()
        hours_of_operation = (
            " ".join(tree.xpath('//div[@class="center-hours-container"]//div//text()'))
            .replace("\n", "")
            .strip()
            or "<MISSING>"
        )
        hours_of_operation = " ".join(hours_of_operation.split())
        if location_name.find("Bahamas") != -1:
            country_code = "Bahamas"
        if location_name.find("Bermuda") != -1:
            country_code = "Bermuda"
        if location_name.find("Kuwait") != -1:
            country_code = "Kuwait"
        if location_name.find("Qatar") != -1:
            country_code = "Qatar"

        if street_address == "Temporarily Closed":
            street_address = "<MISSING>"
            hours_of_operation = "Temporarily Closed"

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
            location_type=location_type,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.PAGE_URL,
                    SgRecord.Headers.STREET_ADDRESS,
                    SgRecord.Headers.LATITUDE,
                }
            )
        )
    ) as writer:
        fetch_data(writer)
