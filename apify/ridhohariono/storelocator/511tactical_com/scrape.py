from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address


def fetch_data(sgw: SgWriter):
    locator_domain = "https://www.511tactical.com/"
    api_url = "https://www.511tactical.com/store-locator"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[contains(@class, "info-location")]')
    for d in div:
        page_url = (
            "".join(d.xpath('.//h4[@class="heading-quinary"]//a/@href'))
            or "https://www.511tactical.com/store-locator"
        )
        if page_url.find("http") == -1:
            page_url = f"https://www.511tactical.com{page_url}"
        if page_url == "https://www.511tactical.comalbuquerque-nm-87110":
            page_url = "https://www.511tactical.com/albuquerque-nm-87110"
        ad = " ".join(d.xpath(".//address//text()")).replace("\n", "").strip()
        ad = " ".join(ad.split())

        location_name = (
            " ".join(d.xpath('.//h4[@class="heading-quinary"]//text()'))
            .replace("\n", "")
            .replace("\r", "")
            .strip()
            or "<MISSING>"
        )
        location_name = " ".join(location_name.split())
        a = parse_address(International_Parser(), ad)
        street_address = (
            f"{a.street_address_1} {a.street_address_2}".replace("None", "").strip()
            or "<MISSING>"
        )
        state = a.state or "<MISSING>"
        postal = a.postcode or "<MISSING>"
        country_code = a.country or "<MISSING>"
        if "U.A.E" in ad:
            country_code = "U.A.E"
            street_address = (
                str(street_address).replace("Tecom Dubai U.A.E Europe", "").strip()
            )
        if country_code == "<MISSING>":
            country_code = "US"
        city = a.city or "<MISSING>"
        if "Dubai" in ad:
            city = "Dubai"
        if "Bankstown" in ad:
            city = "Bankstown"
        phone = (
            "".join(d.xpath(".//address/following-sibling::p[1]/text()[1]"))
            .replace("\n", "")
            .strip()
            or "<MISSING>"
        )
        if phone.find("/") != -1:
            phone = phone.split("/")[0].strip()
        hours_of_operation = " ".join(
            d.xpath(".//address/following-sibling::p[1]/text()[position() > 1]")
        )
        hours_of_operation = " ".join(hours_of_operation.split()) or "<MISSING>"
        per_closed = "".join(
            d.xpath('.//*[contains(text(), "PERMANENTLY CLOSED")]/text()')
        )
        if per_closed:
            continue
        try:
            r = session.get(page_url, headers=headers)
            tree = html.fromstring(r.text)
            latitude = (
                "".join(tree.xpath('//h3[text()="GEO"]/following-sibling::div/text()'))
                .split(",")[0]
                .strip()
            )
            longitude = (
                "".join(tree.xpath('//h3[text()="GEO"]/following-sibling::div/text()'))
                .split(",")[1]
                .strip()
            )
        except:
            latitude, longitude = "<MISSING>", "<MISSING>"

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
            raw_address=ad,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        fetch_data(writer)
