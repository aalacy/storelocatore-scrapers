from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgpostal import parse_address, International_Parser


def get_international(line):
    p = line.split()[-1]
    adr = parse_address(International_Parser(), line, postcode=p)
    street_address = (
        f"{adr.street_address_1} {adr.street_address_2 or ''}".replace("None", "")
        .replace(p, "")
        .strip()
    )
    city = adr.city or ""
    state = adr.state
    postal = adr.postcode

    return street_address, city, state, postal


def get_hoo(page_url):
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    text = tree.xpath("//div[@class='details']/text()")
    if len(text) > 1:
        return text[-1].strip()

    return ""


def fetch_data(sgw: SgWriter):
    api = "http://www.mosburger.com.sg/mos_outlets.php"
    r = session.get(api, headers=headers)
    tree = html.fromstring(r.text)

    divs = tree.xpath("//tr[./td[@class='shopname']]")
    for d in divs:
        location_name = "".join(d.xpath("./td[@class='shopname']/text()")).strip()
        raw_address = " ".join(
            " ".join(
                d.xpath("./td[@class='shopname']/following-sibling::td[1]/text()")
            ).split()
        )
        street_address, city, state, postal = get_international(raw_address)
        phone = "".join(d.xpath("./td[@class='telephone']/text()")).strip()

        text = "".join(d.xpath("./td[@class='shopmaplink']/a/@onclick"))
        store_number = text.split("(")[1].split(")")[0]
        page_url = f"http://www.mosburger.com.sg/fetchbranch.php?id={store_number}"
        hours_of_operation = get_hoo(page_url)

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=SgRecord.MISSING,
            state=state,
            zip_postal=postal,
            country_code="SG",
            phone=phone,
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
            raw_address=raw_address,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "http://www.mosburger.com.sg/"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:94.0) Gecko/20100101 Firefox/94.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "ru,en-US;q=0.7,en;q=0.3",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
