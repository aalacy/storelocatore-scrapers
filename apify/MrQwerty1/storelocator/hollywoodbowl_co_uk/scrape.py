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
    r = session.get("https://www.hollywoodbowl.co.uk/centres", cookies=cookies)

    tree = html.fromstring(r.text)

    all_divs = tree.xpath("//div[@class='centre-list__item centre-list__item--hwb']")
    for div in all_divs:
        page_url = "".join(div.xpath(".//a[contains(text(), 'Visit')]/@href"))

        r = session.get(page_url, cookies=cookies)
        try:
            tree = html.fromstring(r.text)
        except:
            continue

        if tree.xpath('//h3[contains(text(), "WE ARE COMING SOON...")]'):
            continue
        location_name = "".join(div.xpath("./@data-name"))
        street_address = remove_comma(
            "".join(tree.xpath("//span[@itemprop='streetAddress']/p/text()")).strip()
        )
        city = remove_comma(
            "".join(tree.xpath("//p[@itemprop='addressLocality']/text()")).strip()
        )
        state = remove_comma(
            "".join(tree.xpath("//p[@itemprop='addressRegion']/text()")).strip()
        )
        postal = remove_comma(
            "".join(tree.xpath("//p[@itemprop='postalCode']/text()")).strip()
        )
        country_code = "GB"
        phone = "".join(tree.xpath("//p[@itemprop='telephone']/text()")).strip()
        latitude = "".join(div.xpath("./@data-lat"))
        longitude = "".join(div.xpath("./@data-lng"))

        _tmp = []
        tr = tree.xpath("//table[@class='opening-times']//tr")
        for t in tr:
            day = "".join(t.xpath("./th/text()")).strip()
            time = "".join(t.xpath("./td/text()")).strip()
            _tmp.append(f"{day}: {time}")

        hours_of_operation = ";".join(_tmp)
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
            phone=phone,
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
    session = SgRequests()
    domain = "hollywoodbowl.co.uk"
    cookies = {"book-exp": "b"}
    scrape()
