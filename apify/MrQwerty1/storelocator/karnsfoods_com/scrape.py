import ssl
import time
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgselenium import SgChrome


def fetch_data(sgw: SgWriter):
    page_url = "https://www.karnsfoods.com/store-locator/"
    coords = []

    with SgChrome() as fox:
        fox.get(page_url)
        time.sleep(10)
        source = fox.page_source
        iframes = fox.find_elements_by_xpath("//iframe")
        for iframe in iframes:
            fox.switch_to.frame(iframe)
            root = html.fromstring(fox.page_source)
            try:
                text = "".join(
                    root.xpath("//script[contains(text(), 'initEmbed')]/text()")
                )
                lat, lng = text.split("],0,1]")[0].split("[null,null,")[-1].split(",")
            except:
                lat, lng = SgRecord.MISSING, SgRecord.MISSING
            coords.append((lat, lng))
            fox.switch_to.default_content()

    tree = html.fromstring(source)
    divs = tree.xpath("//div[@class='panel panel-default']")

    for d in divs:
        location_name = "".join(d.xpath("./div[1]/h3/text()")).strip()
        if "office" in location_name.lower():
            continue
        line = d.xpath(".//p[./a[@class='btn btn-sm btn-default']]/text()")
        line = list(filter(None, [l.strip() for l in line]))

        street_address = line[0]
        line = line[-1]
        city = line.split(",")[0].strip()
        line = line.split(",")[1].strip()
        state = line.split()[0]
        postal = line.split()[-1]

        try:
            phone = d.xpath(".//a[@class='tel']/text()")[0].strip()
        except IndexError:
            phone = "".join(d.xpath(".//p[./i[@class='fa fa-phone']]/text()")).strip()

        latitude, longitude = coords.pop(0)
        try:
            hours_of_operation = d.xpath(
                ".//p[./strong[text()='Store Hours:']]/text()"
            )[0].strip()
        except IndexError:
            hours_of_operation = SgRecord.MISSING

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code="US",
            phone=phone,
            latitude=latitude,
            longitude=longitude,
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.karnsfoods.com/"
    ssl._create_default_https_context = ssl._create_unverified_context
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PhoneNumberId)) as writer:
        fetch_data(writer)
