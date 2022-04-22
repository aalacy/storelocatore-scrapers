import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.freshpoint.com/"
    api_url = "https://www.freshpoint.com/find-your-location/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath("//div[./div/h4]")
    for d in div:

        location_name = "".join(d.xpath(".//h4/text()"))
        page_url = (
            "".join(d.xpath('.//a[contains(text(), "Visit location")]/@href'))
            or "https://www.freshpoint.com/find-your-location/"
        )
        phone = (
            "".join(d.xpath('.//p[@class="address"]/following-sibling::p[1]/a//text()'))
            or "<MISSING>"
        )
        if phone == "() –":
            phone = "<MISSING>"
        street_address = "".join(d.xpath('.//p[@class="address"]/text()[1]'))
        ad = (
            "".join(d.xpath('.//p[@class="address"]/text()[2]'))
            .replace(".", "")
            .replace("Canada", "")
            .replace("B C", "BC")
            .replace("\n", "")
            .strip()
        )
        state = ad.split(",")[1].split()[0].strip()
        postal = " ".join(ad.split(",")[1].split()[1:]).strip()
        country_code = "CA"
        if postal.isdigit():
            country_code = "US"
        city = ad.split(",")[0].strip()
        latitude, longitude = "<MISSING>", "<MISSING>"
        try:
            if page_url != "https://www.freshpoint.com/find-your-location/":
                r = session.get(page_url, headers=headers)
                tree = html.fromstring(r.text)
                google_url = "".join(
                    tree.xpath('//div[@class="wpb_wrapper"]/iframe/@src')
                )
                r = session.get(google_url, headers=headers)
                cleaned = (
                    r.text.replace("\\t", " ")
                    .replace("\t", " ")
                    .replace("\\n]", "]")
                    .replace("\n]", "]")
                    .replace("\\n,", ",")
                    .replace("\\n", "#")
                    .replace('\\"', '"')
                    .replace("\\u003d", "=")
                    .replace("\\u0026", "&")
                    .replace("\\", "")
                    .replace("\xa0", " ")
                )

                locations = json.loads(
                    cleaned.split('var _pageData = "')[1].split('";</script>')[0]
                )[1][6][0][12][0][13][0]
                try:
                    latitude = locations[0][1][0][0][0]
                    longitude = locations[0][1][0][0][1]
                except:
                    latitude, longitude = "<MISSING>", "<MISSING>"
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
            hours_of_operation=SgRecord.MISSING,
            raw_address=f"{street_address} {ad}",
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {SgRecord.Headers.STREET_ADDRESS, SgRecord.Headers.LOCATION_NAME}
            )
        )
    ) as writer:
        fetch_data(writer)
