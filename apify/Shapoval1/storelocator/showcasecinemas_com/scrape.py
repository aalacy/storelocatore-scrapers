from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.showcasecinemas.com"
    api_url = "https://www.showcasecinemas.com/theaters"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    js_block = (
        "".join(tree.xpath('//script[contains(text(), "pc.cinemas")]/text()'))
        .split("pc.cinemas = ")[1]
        .split(";")[0]
        .replace("false", "False")
        .strip()
    )
    js = eval(js_block)
    for j in js:

        slug = j.get("CinemaInfoUrl")
        page_url = f"{locator_domain}/{slug}"
        location_name = "".join(j.get("CinemaName"))
        location_type = "Showcase Cinema"
        street_address = j.get("Address1")
        state = j.get("StateCode")
        postal = j.get("ZipCode")
        country_code = "USA"
        city = j.get("City")
        latitude = j.get("Latitude")
        longitude = j.get("Longitude")
        phone = "<MISSING>"

        r = session.get("https://www.showcasecinemas.com/contact-us", headers=headers)
        tree = html.fromstring(r.text)
        loc_name = tree.xpath("//ul/li/strong")

        hours_of_operation = "<MISSING>"

        for l in loc_name:
            l_name = "".join(l.xpath(".//text()")).capitalize()
            if l_name.find(" ") != -1:
                l_name = l_name.split()[0].capitalize().strip()
            if l_name == "N.":
                l_name = "North"
            if location_name.find(l_name) != -1:
                phone = "".join(l.xpath(".//following-sibling::a//text()"))

        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)
        cls = "".join(tree.xpath('//*[contains(text(), "TEMPORARILY CLOSED")]/text()'))
        if cls:
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
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        fetch_data(writer)
