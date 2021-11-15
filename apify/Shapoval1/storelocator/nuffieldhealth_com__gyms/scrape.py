from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.nuffieldhealth.com/"
    api_url = "https://www.nuffieldhealth.com/gyms"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath(
        '//div[@class="location-finder__card location__card--price js-location-finder-card "]'
    )
    for d in div:

        page_url = "".join(d.xpath('.//a[@itemprop="url"]/@href'))
        if page_url.find("http") == -1:
            page_url = f"https://www.nuffieldhealth.com{page_url}"
        location_name = "".join(d.xpath('.//span[@itemprop="name"]/text()'))
        street_address = "".join(d.xpath('.//span[@itemname="streetAddress"]/text()'))
        state = "".join(d.xpath(".//@data-region"))
        postal = "".join(d.xpath('.//span[@itemname="postalCode"]/text()'))
        country_code = "UK"
        city = "".join(d.xpath('.//span[@itemname="addressLocality"]/text()'))
        try:
            latitude = (
                "".join(d.xpath(".//@data-lat-lngs"))
                .split('"lat":')[1]
                .split(",")[0]
                .strip()
            )
            longitude = (
                "".join(d.xpath(".//@data-lat-lngs"))
                .split('"lon":')[1]
                .split("}")[0]
                .strip()
            )
        except:
            latitude, longitude = "<MISSING>", "<MISSING>"
        phone = (
            "".join(d.xpath('.//span[@itemprop="telephone"]//text()'))
            .replace("\n", "")
            .strip()
        )
        if phone.find("Members:") != -1:
            phone = phone.split("Members:")[1].split("/")[0].strip()

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
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.LATITUDE}))) as writer:
        fetch_data(writer)
