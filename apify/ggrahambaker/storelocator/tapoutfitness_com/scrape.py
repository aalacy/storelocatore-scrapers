from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address


def fetch_data(sgw: SgWriter):

    locator_domain = "https://tapoutfitness.com/"
    api_url = "https://tapoutfitness.com/locations/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[./div[@class="location-info"]]')
    for d in div:

        slug = "".join(d.xpath('.//a[@class="icon-monitor"]/@href'))
        page_url = f"https:{slug}"
        location_name = "".join(d.xpath(".//h3//text()"))
        ad = (
            " ".join(d.xpath('.//div[@class="location-info"]/div[1]/p/text()'))
            .replace("\n", "")
            .strip()
        )
        ad = " ".join(ad.split())
        a = parse_address(International_Parser(), ad)
        street_address = (
            f"{a.street_address_1} {a.street_address_2}".replace("None", "").strip()
            or "<MISSING>"
        )
        state = a.state or "<MISSING>"
        postal = a.postcode or "<MISSING>"
        country_code = "US"
        city = a.city or "<MISSING>"
        if state == "ON":
            country_code = "CA"
        if location_name.find("Bangladesh") != -1:
            country_code = "Bangladesh"
        if location_name.find("MX") != -1:
            country_code = "MX"
        if location_name.find("Indonesia") != -1:
            country_code = "Indonesia"
        if location_name.find("Philippines") != -1:
            country_code = "Philippines"
        if location_name.find("Singapore") != -1:
            country_code = "Singapore"
        phone = (
            "".join(d.xpath('.//a[contains(@href, "tel")]/text()'))
            .replace("P:", "")
            .strip()
            or "<MISSING>"
        )
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)
        hours_of_operation = (
            " ".join(tree.xpath('//span[@class="map_block_hours"]/text()'))
            .replace("\n", "")
            .strip()
            or "<MISSING>"
        )
        hours_of_operation = " ".join(hours_of_operation.split())
        desc = "".join(tree.xpath('//meta[@name="description"]/@content'))
        if "24/7" in desc and hours_of_operation == "<MISSING>":
            hours_of_operation = "24/7"

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
            latitude=SgRecord.MISSING,
            longitude=SgRecord.MISSING,
            hours_of_operation=hours_of_operation,
            raw_address=ad,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        fetch_data(writer)
