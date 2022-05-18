from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def get_cookies():
    cook = dict()
    out = dict()
    r = session.post("https://www.lagallega.com.ar/Login.asp", headers=headers)
    for k, v in r.cookies.items():
        cook[k] = v

    req = session.get(
        "https://www.lagallega.com.ar/index.asp", headers=headers, cookies=cook
    )
    for k, v in req.cookies.items():
        out[k] = v

    return out


def fetch_data(sgw: SgWriter):
    r = session.get(page_url, headers=headers, cookies=cookies)
    tree = html.fromstring(r.text)
    divs = tree.xpath("//div[@class='BoxSuc']")

    for d in divs:
        location_name = "".join(
            d.xpath(".//div[@class='NosText']/preceding-sibling::div[1]/text()")
        ).strip()
        street_address = "".join(
            d.xpath(".//b[contains(text(), 'Dirección')]/following-sibling::text()[2]")
        ).strip()
        city = location_name.replace("Sucursal", "").strip()
        if "(" in city:
            city = city.split("(")[-1].replace(")", "").strip()
        country_code = "AR"
        phone = (
            "".join(
                d.xpath(
                    ".//b[contains(text(), 'Teléfono')]/following-sibling::text()[2]"
                )
            )
            .replace("- ", "-")
            .strip()
        )
        if "/" in phone:
            phone = phone.split("/")[0].strip()
        if " " in phone:
            phone = phone.split()[0]
        hours_of_operation = (
            "".join(
                d.xpath(
                    ".//b[contains(text(), 'Horarios')]/following-sibling::text()[2]"
                )
            )
            .replace(" | ", ";")
            .strip()
        )

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            country_code=country_code,
            phone=phone,
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    locator_domain = "https://www.lagallega.com.ar/"
    page_url = "https://www.lagallega.com.ar/Sucursales.asp"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:98.0) Gecko/20100101 Firefox/98.0",
    }

    cookies = get_cookies()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PhoneNumberId)) as writer:
        fetch_data(writer)
