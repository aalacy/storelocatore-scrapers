from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


def get_urls():
    r = session.get(
        "https://www.pathwayslearningacademy.com/child-care-centers/find-a-school/",
        headers=headers,
    )
    tree = html.fromstring(r.text)

    return tree.xpath("//map/area/@href")


def fetch_data(api, sgw: SgWriter):
    r = session.get(api, headers=headers)
    tree = html.fromstring(r.text)
    divs = tree.xpath("//div[@class='locationCard']")

    for d in divs:
        page_url = api
        location_name = "".join(d.xpath(".//h2[@class='school']//text()")).strip()
        slug = "".join(d.xpath(".//a[@class='schoolNameLink']/@href")) or ""
        if slug.startswith("http"):
            continue
        if slug:
            page_url = f"https://www.pathwayslearningacademy.com{slug}"

        street_address = "".join(
            d.xpath(".//div[@class='addrMapDetails']//span[@class='street']/text()")
        ).strip()
        line = (
            "".join(
                d.xpath(
                    ".//div[@class='addrMapDetails']//span[@class='cityState']/text()"
                )
            ).strip()
            or "<MISSING>, <MISSING> <MISSING>"
        )
        city = line.split(",")[0].strip()
        line = line.split(",")[1].strip()
        state = line.split()[0]
        postal = line.split()[1]
        store_number = "".join(d.xpath("./@data-school-id"))
        phone = "".join(d.xpath(".//span[@class='tel']/text()")).strip()
        latitude = "".join(
            d.xpath(
                ".//div[@class='addrMapDetails']//span[@data-latitude]/@data-latitude"
            )
        )
        longitude = "".join(
            d.xpath(
                ".//div[@class='addrMapDetails']//span[@data-longitude]/@data-longitude"
            )
        )
        location_type = SgRecord.MISSING
        if d.xpath(".//div[@class='schoolFeature']"):
            location_type = "Coming Soon"
        hours_of_operation = (
            "".join(d.xpath(".//p[@class='hours']/text()")).strip() or "<MISSING>"
        )
        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code="US",
            store_number=store_number,
            phone=phone,
            location_type=location_type,
            latitude=latitude,
            longitude=longitude,
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    locator_domain = "https://www.pathwayslearningacademy.com/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0"
    }

    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        for url in get_urls():
            ap = f"https://www.pathwayslearningacademy.com{url}"
            fetch_data(ap, writer)
