from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import USA_Fast_Parser, parse_address


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.wellstreet.com/"
    api_url = "https://www.wellstreet.com/region/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//a[./div[@class="map"]]')
    for d in div:
        slug_sub_url = "".join(d.xpath(".//@href"))
        sub_url = f"https://www.wellstreet.com{slug_sub_url}"
        location_type = "<MISSING>"
        if sub_url.find("atlanta") != -1:
            location_type = "Piedmont Urgent Care"
        if sub_url.find("detroit") != -1:
            location_type = "Beaumont Urgent Care"
        state = "".join(d.xpath('.//div[@class="bar"]//text()'))
        r = session.get(sub_url, headers=headers)
        tree = html.fromstring(r.text)
        div = tree.xpath('//div[@class="map-list-item"]')
        for d in div:

            page_url = "".join(d.xpath('.//a[contains(text(), "Location Info")]/@href'))
            location_name = "".join(d.xpath('.//a[@class="title"]/text()'))
            street_address = (
                "".join(d.xpath('.//div[@class="address-line"]//text()'))
                .replace("\n", "")
                .strip()
            )
            country_code = "US"
            store_number = (
                "".join(d.xpath('.//a[text()="Book Ahead"]/@href'))
                .split("=")[-1]
                .strip()
            )
            phone = (
                "".join(d.xpath('.//div[@class="phone-line"]//text()'))
                .replace("\n", "")
                .strip()
            )
            hours_of_operation = (
                " ".join(d.xpath('.//div[@class="more-hours mt-2"]//text()'))
                .replace("\n", "")
                .strip()
            )
            hours_of_operation = " ".join(hours_of_operation.split())
            try:
                r = session.get(page_url, headers=headers)
                tree = html.fromstring(r.text)
                ad = (
                    " ".join(
                        tree.xpath(
                            '//div[./span[@class="fas fa-map-marker-alt"]]/following-sibling::div[1]/*[1]//text()'
                        )
                    )
                    .replace("\n", "")
                    .strip()
                )
                ad = " ".join(ad.split())
                a = parse_address(USA_Fast_Parser(), ad)
                postal = a.postcode or "<MISSING>"
                country_code = "US"
                city = a.city or "<MISSING>"
                latitude = (
                    "".join(tree.xpath('//script[contains(text(), "LatLng")]/text()'))
                    .split("LatLng(")[1]
                    .split(",")[0]
                    .strip()
                )
                longitude = (
                    "".join(tree.xpath('//script[contains(text(), "LatLng")]/text()'))
                    .split("LatLng(")[1]
                    .split(",")[1]
                    .split(")")[0]
                    .strip()
                )
            except:
                city = "<MISSING>"
                latitude = "<MISSING>"
                longitude = "<MISSING>"
                postal = "<MISSING>"
            if city == "<MISSING>":
                city = location_name

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
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        fetch_data(writer)
