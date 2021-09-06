from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgpostal import International_Parser, parse_address


def fetch_data(sgw: SgWriter):

    api_url = "https://www.rockymountainflatbread.ca/locations/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath("//h1/a")
    for d in div:

        page_url = "".join(d.xpath(".//@href"))
        if page_url.find("surrey") != -1:
            continue

        location_name = "".join(d.xpath(".//text()"))
        country_code = "CA"

        session = SgRequests()
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)
        ad = (
            "".join(
                tree.xpath(
                    '//div[@class="wpb_gmaps_widget wpb_content_element vc_map_responsive"]/following-sibling::div//p[1]/text()'
                )
            )
            or "<MISSING>"
        )
        if page_url.find("banff") != -1 and ad == "<MISSING>":
            continue
        a = parse_address(International_Parser(), ad)
        street_address = f"{a.street_address_1} {a.street_address_2}".replace(
            "None", ""
        ).strip()
        city = a.city or "<MISSING>"
        state = a.state or "<MISSING>"
        postal = "<MISSING>"
        map_link = "".join(tree.xpath("//iframe/@src"))
        latitude = map_link.split("!3d")[1].strip().split("!")[0].strip()
        longitude = map_link.split("!2d")[1].strip().split("!")[0].strip()
        phone = "<MISSING>"
        if page_url.find("canmore") != -1:
            phone = "".join(tree.xpath('//a[./span[contains(text(), "CALL")]]/@href'))
            postal = "T1W 2A7"
        if page_url.find("main-street") != -1:
            phone = "".join(tree.xpath("//div/h2[2]//text()"))
            postal = "V5V 3Y7"
        if page_url.find("kitsilano") != -1:
            phone = "".join(
                tree.xpath('//p[contains(text(), "@")]/preceding-sibling::p[1]/text()')
            )
            postal = "V6J 1G5"
        if page_url.find("calgary") != -1:
            phone = "".join(tree.xpath("//div/h2[2]//text()"))
            postal = "T2Z 0G4"

        phone = phone.replace("Tel:", "").replace("tel:", "").strip()
        hours_of_operation = (
            " ".join(tree.xpath('//div[@class="diamond-content"]//text()'))
            .replace("\n", "")
            .strip()
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
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    locator_domain = "https://www.rockymountainflatbread.ca"
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
