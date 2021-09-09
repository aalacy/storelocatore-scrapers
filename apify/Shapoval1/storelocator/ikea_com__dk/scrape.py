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
    div = tree.xpath('//div[./p/a[contains(@href, "maps")]]')
    for d in div:

        page_url = "".join(
            d.xpath(
                './/following::a[.//span[contains(text(), "Se mere om IKEA")]][1]/@href'
            )
        )
        location_name = "".join(d.xpath(".//h2/text()"))
        if location_name.find("Studio") != -1:
            continue
        text = "".join(d.xpath('.//a[text()="her"]/@href'))

        country_code = "DA"

        store_number = "<MISSING>"
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
                d.xpath(
                    './/strong[contains(text(), "Varehuset")]/following-sibling::text()'
                )
            )
            .replace("\n", "")
            .strip()
        )
        hours_of_operation = " ".join(hours_of_operation.split())
        session = SgRequests()
        r = session.get(text, headers=headers)
        tree = html.fromstring(r.text)

        ad = (
            "".join(tree.xpath('//meta[@itemprop="name"]/@content'))
            .split("·")[1]
            .strip()
        )
        location_type = "<MISSING>"
        street_address = ad.split(",")[0].strip()
        state = "<MISSING>"
        postal = ad.split(",")[1].split()[0].strip()
        phone = "<MISSING>"
        city = ad.split(",")[1].split()[1].strip()

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
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
