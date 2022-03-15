from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import USA_Best_Parser, parse_address


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

        slug = "".join(d.xpath(".//@href")).split("/")[-2]
        page_url = f"https://www.rockymountainflatbread.ca/locations/{slug}/"
        location_name = "".join(d.xpath(".//text()"))
        country_code = "CA"

        session = SgRequests()
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)
        ad = "".join(
            tree.xpath(
                f'//p[contains(text(), "{location_name}")]/following-sibling::*[1]/text()'
            )
        )
        a = parse_address(USA_Best_Parser(), ad)
        street_address = f"{a.street_address_1} {a.street_address_2}".replace(
            "None", ""
        ).strip()
        city = a.city or "<MISSING>"
        state = a.state or "<MISSING>"
        postal = "<MISSING>"
        map_link = "".join(tree.xpath("//iframe/@src"))
        try:
            latitude = map_link.split("!3d")[1].strip().split("!")[0].strip()
            longitude = map_link.split("!2d")[1].strip().split("!")[0].strip()
        except:
            latitude, longitude = "<MISSING>", "<MISSING>"
        phone = "<MISSING>"
        if page_url.find("canmore") != -1:
            phone = "".join(tree.xpath('//a[./span[contains(text(), "CALL")]]/@href'))
            postal = "T1W 2A7"
        if page_url.find("main-street") != -1:
            phone = "".join(tree.xpath("//div/h2[2]//text()"))
            postal = "V5V 3Y7"
        if page_url.find("kitsilano") != -1:
            phone = "".join(
                tree.xpath(
                    '//*[@style="font-size: 54px;color: #ffffff;text-align: center;font-family:Josefin Sans;font-weight:700;font-style:normal"]/following-sibling::*[2]//text()'
                )
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
        ) or "<MISSING>"
        if hours_of_operation == "<MISSING>":
            hours_of_operation = (
                " ".join(tree.xpath("//h4/following-sibling::p//text()"))
                .replace("\n", "")
                .strip()
            )
        if hours_of_operation.find("A very delicious ") != -1:
            hours_of_operation = hours_of_operation.split("A very delicious ")[
                0
            ].strip()

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
            raw_address=f"{street_address} {city}, {state} {postal}",
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    locator_domain = "https://www.rockymountainflatbread.ca"
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
