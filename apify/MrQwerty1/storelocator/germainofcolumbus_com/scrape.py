from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def get_hours(page_url):
    _tmp = []
    r = session.get(page_url)
    tree = html.fromstring(r.text)
    li = tree.xpath(
        "//div[@id='hours1-app-root']//li|//div[@data-widget-name='hours-default']//li"
    )
    for l in li:
        day = "".join(l.xpath("./span[1]//text()")).strip()
        time = "".join(l.xpath("./span[2]//text()")).strip()
        _tmp.append(f"{day}: {time}")
        if "Sun" in day:
            break

    return ";".join(_tmp)


def fetch_data(sgw: SgWriter):
    api = "https://www.germainofcolumbus.com/locations/index.htm"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0"
    }
    r = session.get(api, headers=headers)
    tree = html.fromstring(r.text)
    divs = tree.xpath("//ol[@id='proximity-dealer-list']/li")

    for d in divs:
        location_name = "".join(d.xpath(".//a[@class='url']/span/text()")).strip()
        page_url = "".join(d.xpath(".//a[@class='url']/@href")).replace("#", "") or api
        street_address = "".join(
            d.xpath(".//span[@class='street-address']/text()")
        ).strip()
        city = "".join(d.xpath(".//span[@class='locality']/text()")).strip()
        state = "".join(d.xpath(".//span[@class='region']/text()")).strip()
        postal = "".join(d.xpath(".//span[@class='postal-code']/text()")).strip()

        country_code = "US"
        try:
            phone = d.xpath(
                ".//li[@data-click-to-call-phone]/@data-click-to-call-phone"
            )[0].split("?")[0]
        except IndexError:
            phone = SgRecord.MISSING
        latitude = "".join(d.xpath(".//span[@class='latitude']/text()"))
        longitude = "".join(d.xpath(".//span[@class='longitude']/text()"))

        if page_url == api:
            hours_of_operation = SgRecord.MISSING
        else:
            try:
                hours_of_operation = get_hours(page_url)
            except:
                hours_of_operation = SgRecord.MISSING

        row = SgRecord(
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
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    locator_domain = "https://www.germainofcolumbus.com/"
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.LOCATION_NAME}))
    ) as writer:
        fetch_data(writer)
