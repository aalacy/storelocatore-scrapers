import json
from lxml import html
from sgscrape.sgpostal import International_Parser, parse_address
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


def get_hours(hours) -> str:
    tmp = []
    for h in hours:
        days = h.get("dayOfWeek")
        if type(days) == list:
            days = " ".join(days)
        opens = h.get("opens")
        closes = h.get("closes")
        line = f"{days} {opens} - {closes}"
        tmp.append(line)

    return ";".join(tmp)


def fetch_data(sgw: SgWriter):
    r = session.get("https://houseofair.com/locations/", headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//a[text()="Home"]')

    for d in div:
        page_url = "".join(d.xpath(".//@href"))
        if page_url.startswith("/"):
            page_url = f"https://houseofair.com{page_url}"

        if ".pl" in page_url:
            page_url = "http://www.houseofair.pl/kontakt"

        location_name = "".join(
            d.xpath('.//preceding::h3[@class="topspace0"][1]/a/text()')
        ).strip()
        ad = (
            " ".join(
                d.xpath(
                    './/preceding::h3[@class="topspace0"][1]/following-sibling::p[1]/text()'
                )
            )
            .replace("\n", "")
            .strip()
        )
        a = parse_address(International_Parser(), ad)
        street_address = f"{a.street_address_1} {a.street_address_2}".replace(
            "None", ""
        ).strip()

        city = a.city
        state = a.state
        postal = a.postcode
        country_code = "US"
        if ad.find("Poland") != -1:
            country_code = "PL"

        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)

        jsBlock = "".join(tree.xpath('//script[@type="application/ld+json"]/text()'))
        map_link = "".join(tree.xpath("//iframe/@src"))
        try:
            latitude = map_link.split("!3d")[1].strip().split("!")[0].strip()
            longitude = map_link.split("!2d")[1].strip().split("!")[0].strip()
        except:
            latitude = "<MISSING>"
            longitude = "<MISSING>"
        phone = "".join(
            tree.xpath('//div[@class="contact-text"]//a[contains(@href, "tel")]/text()')
        )

        hours_of_operation = (
            " ".join(
                tree.xpath(
                    '//h3[contains(text(), "Park Access Hours")]/following-sibling::ul/li//text() | //h2[text()=" Hours of Operation"]/following-sibling::ul/li//text() | //div[@class="hours-right"]/p/text()'
                )
            )
            .replace("\n", "")
            .strip()
            or "<MISSING>"
        )
        if "Phone" in hours_of_operation:
            hours_of_operation = hours_of_operation.split("Phone")[0].strip()

        hours_of_operation = " ".join(hours_of_operation.split())
        if jsBlock:
            js = json.loads(jsBlock)
            phone = js.get("telephone")
            latitude = js.get("geo").get("latitude")
            longitude = js.get("geo").get("longitude")
            hours = js.get("openingHoursSpecification")
            hours_of_operation = get_hours(hours)

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
    locator_domain = "https://houseofair.com"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }

    with SgRequests() as session:
        with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
            fetch_data(writer)
