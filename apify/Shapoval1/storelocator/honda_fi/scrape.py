from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address


def fetch_data(sgw: SgWriter):

    locator_domain = "https://cars.honda.fi/"
    page_url = "https://cars.honda.fi/dealer-search"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[contains(@class, "dealerResult ")]')
    for d in div:

        location_name = "".join(d.xpath(".//h3/a/text()"))
        location_type = (
            " ".join(
                d.xpath(
                    './/h4[text()="Palveluvalikoima"]/following-sibling::ul/li//text()'
                )
            )
            .replace("\n", "")
            .strip()
        )
        location_type = ",".join(location_type.split())
        ad = (
            " ".join(d.xpath('.//div[@class="dealerAddress"]/p/text()'))
            .replace("\n", "")
            .replace("\r", "")
            .strip()
        )
        ad = " ".join(ad.split())
        if ad.find("Jälleenmyyjä:") != -1:
            ad = ad.split("Jälleenmyyjä:")[1].split("Huolto")[0].strip()

        a = parse_address(International_Parser(), ad)
        street_address = f"{a.street_address_1} {a.street_address_2}".replace(
            "None", ""
        ).strip()
        state = a.state or "<MISSING>"
        postal = a.postcode or "<MISSING>"
        country_code = "FI"
        city = a.city or "<MISSING>"
        if city == "<MISSING>":
            city = ad.split()[-1].strip()
        try:
            latitude = "".join(d.xpath(".//@data-result-coords")).split(",")[0].strip()
            longitude = "".join(d.xpath(".//@data-result-coords")).split(",")[1].strip()
        except:
            latitude, longitude = "<MISSING>", "<MISSING>"
        phone = "".join(d.xpath('.//span[@itemprop="telephone"]/text()')) or "<MISSING>"
        hours_of_operation = (
            " ".join(d.xpath(".//dl//text()"))
            .replace("\n", "")
            .replace("\r", "")
            .strip()
        )
        hours_of_operation = " ".join(hours_of_operation.split()) or "<MISSING>"

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
            raw_address=ad,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(
            SgRecordID({SgRecord.Headers.STREET_ADDRESS, SgRecord.Headers.LATITUDE})
        )
    ) as writer:
        fetch_data(writer)
