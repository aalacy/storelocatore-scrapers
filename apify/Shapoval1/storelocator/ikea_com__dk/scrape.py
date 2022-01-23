import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.ikea.com/dk/da"
    api_url = "https://www.ikea.com/dk/da/stores/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//a[@class="pub__link-list__item"]')
    for d in div:

        page_url = "".join(d.xpath(".//@href"))
        if page_url.find("planning-studios") != -1:
            continue
        country_code = "DA"
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)
        store_number = "<MISSING>"

        hours_of_operation = (
            " ".join(
                tree.xpath('//h2[text()="Varehus"]/following-sibling::*[1]//text()')
            )
            .replace("\n", "")
            .strip()
        )
        hours_of_operation = " ".join(hours_of_operation.split())
        location_name = "".join(tree.xpath("//h1/text()"))
        ad = tree.xpath("//h2/following-sibling::p/text()")
        ad = list(filter(None, [a.strip() for a in ad]))
        js = "".join(tree.xpath('//script[contains(text(), "latitude")]/text()'))
        j = json.loads(js)
        latitude = j.get("geo").get("latitude")
        longitude = j.get("geo").get("longitude")
        location_type = "<MISSING>"
        street_address = "".join(ad[1]).strip()
        state = "<MISSING>"
        postal = "".join(ad[2]).split()[0]
        phone = "<MISSING>"
        city = " ".join("".join(ad[2]).split()[1:])

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
            location_type=location_type,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
            raw_address=" ".join(ad[1:]),
        )

        sgw.write_row(row)

    locator_domain = "https://www.ikea.com/fi/fi/"
    api_url = "https://www.ikea.com/fi/fi/stores/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[./p/a[contains(@href, "goo")]]')
    for d in div:

        page_url = "".join(
            d.xpath(
                './/following::a[@class="pub__btn pub__btn--small pub__btn--primary"][1]/@href'
            )
        )
        location_name = "".join(d.xpath(".//h3/text()"))
        if location_name.find("studio") != -1:
            continue
        country_code = "FI"
        store_number = "<MISSING>"

        location_type = "<MISSING>"
        street_address = (
            "".join(d.xpath(".//h3/following-sibling::p[1]/text()[1]"))
            .replace("\n", "")
            .strip()
        )
        cp = (
            "".join(d.xpath(".//h3/following-sibling::p[1]/text()[2]"))
            .replace("\n", "")
            .strip()
        )
        state = "<MISSING>"
        postal = cp.split()[0].strip()
        phone = "<MISSING>"
        city = cp.split()[1].strip()
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        session = SgRequests()
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)

        hours_of_operation = (
            "".join(
                tree.xpath('//strong[text()="Aukioloajat"]/following-sibling::text()')
            )
            .replace("\n", "")
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
            store_number=store_number,
            phone=phone,
            location_type=location_type,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
            raw_address=f"{street_address} {cp}",
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        fetch_data(writer)
