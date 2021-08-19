from lxml import html

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def remove_comma(text):
    if text.endswith(","):
        return text[:-1]
    return text


def fetch_data():
    session = SgRequests()
    r = session.get("https://www.hollywoodbowl.co.uk/centres")
    tree = html.fromstring(r.text)

    all_divs = tree.xpath("//div[@class='centre-data__item']")
    for div in all_divs:
        domain = "hollywoodbowl.co.uk"
        page_url = "".join(div.xpath("./@data-link"))

        session = SgRequests()
        r = session.get(page_url)
        tree = html.fromstring(r.text)

        if tree.xpath('//h3[contains(text(), "WE ARE COMING SOON...")]'):
            continue
        location_name = "".join(div.xpath("./@data-name"))
        street_address = (
            remove_comma(
                "".join(
                    tree.xpath("//span[@itemprop='streetAddress']/p/text()")
                ).strip()
            )
            or "<MISSING>"
        )
        city = (
            remove_comma(
                "".join(tree.xpath("//p[@itemprop='addressLocality']/text()")).strip()
            )
            or "<MISSING>"
        )
        state = (
            remove_comma(
                "".join(tree.xpath("//p[@itemprop='addressRegion']/text()")).strip()
            )
            or "<MISSING>"
        )
        postal = (
            remove_comma(
                "".join(tree.xpath("//p[@itemprop='postalCode']/text()")).strip()
            )
            or "<MISSING>"
        )
        country_code = "GB"
        store_number = "<MISSING>"
        phone = (
            "".join(tree.xpath("//p[@itemprop='telephone']/text()")).strip()
            or "<MISSING>"
        )
        latitude = "".join(div.xpath("./@data-lat")) or "<MISSING>"
        longitude = "".join(div.xpath("./@data-lng")) or "<MISSING>"
        location_type = "<MISSING>"

        _tmp = []
        tr = tree.xpath("//table[@class='opening-times']//tr")
        for t in tr:
            day = "".join(t.xpath("./th/text()")).strip()
            time = "".join(t.xpath("./td/text()")).strip()
            _tmp.append(f"{day}: {time}")

        hours_of_operation = ";".join(_tmp) or "<MISSING>"
        if hours_of_operation.lower().count("closed") == 7:
            hours_of_operation = "Closed"

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code=country_code,
            store_number=store_number,
            phone=phone,
            location_type=location_type,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
        )

        yield item


def scrape():
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {SgRecord.Headers.LOCATION_NAME, SgRecord.Headers.STREET_ADDRESS}
            )
        )
    ) as writer:
        for item in fetch_data():
            writer.write_row(item)


if __name__ == "__main__":
    scrape()
