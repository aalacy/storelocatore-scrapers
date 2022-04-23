from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.adventhealth.com/"
    api_url = "https://www.adventhealth.com/find-a-location"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//li[@class="pager__item pager__item--last"]/a')
    for d in div:
        last_page = "".join(d.xpath(".//@href")).split("=")[-1].strip()
        for i in range(0, int(last_page) + 1):
            r = session.get(
                f"https://www.adventhealth.com/find-a-location?facility=&name=&geolocation_geocoder_google_geocoding_api=&geolocation_geocoder_google_geocoding_api_state=1&latlng%5Bdistance%5D%5Bfrom%5D=-&latlng%5Bvalue%5D=&latlng%5Bcity%5D=&latlng%5Bstate%5D=&latlng%5Bprecision%5D=&service=&page={i}"
            )
            tree = html.fromstring(r.text)
            div = tree.xpath('//li[@class="facility-search-block__item"]')
            for d in div:

                slug = "".join(d.xpath(".//h3/a/@href"))
                page_url = f"https://www.adventhealth.com{slug}".strip()
                if page_url.find("?") != -1:
                    page_url = page_url.split("?")[0].strip()
                if page_url == "https://www.adventhealth.com":
                    page_url = "https://www.adventhealth.com/find-a-location"
                location_name = (
                    "".join(
                        d.xpath('.//div[@class="location-block__headline"]/h3/a/text()')
                    )
                    .replace("\n", "")
                    .strip()
                    or "<MISSING>"
                )
                if location_name == "<MISSING>":
                    location_name = (
                        "".join(
                            d.xpath(
                                './/div[@class="location-block__headline"]/h3/text()'
                            )
                        )
                        .replace("\n", "")
                        .strip()
                        or "<MISSING>"
                    )
                street_address = (
                    "".join(d.xpath('.//span[@property="streetAddress"]/text()'))
                    .replace("\n", "")
                    .replace("\r", "")
                    .strip()
                    or "<MISSING>"
                )
                state = (
                    "".join(d.xpath('.//span[@property="addressRegion"]/text()'))
                    .replace("\n", "")
                    .strip()
                    or "<MISSING>"
                )
                postal = (
                    "".join(d.xpath('.//span[@property="postalCode"]/text()'))
                    .replace("\n", "")
                    .strip()
                    or "<MISSING>"
                )
                country_code = "US"
                city = (
                    "".join(d.xpath('.//span[@property="addressLocality"]/text()'))
                    .replace("\n", "")
                    .strip()
                    or "<MISSING>"
                )
                latitude = "".join(d.xpath(".//*/@data-lat")) or "<MISSING>"
                longitude = "".join(d.xpath(".//*/@data-lng")) or "<MISSING>"
                phone = (
                    "".join(d.xpath('.//a[@class="telephone"]/text()'))
                    .replace("\n", "")
                    .strip()
                    or "<MISSING>"
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
                    store_number=SgRecord.MISSING,
                    phone=phone,
                    location_type=SgRecord.MISSING,
                    latitude=latitude,
                    longitude=longitude,
                    hours_of_operation=SgRecord.MISSING,
                )

                sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.STREET_ADDRESS,
                    SgRecord.Headers.LOCATION_NAME,
                    SgRecord.Headers.PAGE_URL,
                    SgRecord.Headers.LATITUDE,
                    SgRecord.Headers.PHONE,
                }
            )
        )
    ) as writer:
        fetch_data(writer)
