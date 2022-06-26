from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def get_hoo(page_url):
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)

    _tmp = []
    hours = tree.xpath("//div[contains(@id, 'hours')]//li")
    for h in hours:
        day = "".join(h.xpath("./span[1]//text()")).strip()
        inter = "".join(h.xpath("./span[2]//text()")).strip()
        _tmp.append(f"{day}: {inter}")

    return ";".join(_tmp)


def fetch_data(sgw: SgWriter):
    api = "https://www.hertzcarsales.com/locations/index.htm"
    r = session.get(api, headers=headers)
    tree = html.fromstring(r.text)
    divs = tree.xpath("//li[contains(@class, ' info-window')]")

    for d in divs:
        location_name = "".join(d.xpath(".//a[@class='url']/span/text()")).strip()
        page_url = "".join(d.xpath(".//a[@class='url']/@href")).replace("////", "//")
        street_address = ", ".join(
            d.xpath(".//span[@class='street-address']/text()")
        ).strip()
        city = "".join(d.xpath(".//span[@class='locality']/text()")).strip()
        state = "".join(d.xpath(".//span[@class='region']/text()")).strip()
        postal = "".join(d.xpath(".//span[@class='postal-code']/text()")).strip()
        country_code = "US"
        phone = "".join(d.xpath(".//li/@data-click-to-call-phone"))
        if "?" in phone:
            phone = phone.split("?")[0].strip()
        latitude = "".join(d.xpath(".//span[@class='latitude']/text()")).strip()
        longitude = "".join(d.xpath(".//span[@class='longitude']/text()")).strip()
        hours_of_operation = get_hoo(page_url)

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code=country_code,
            latitude=latitude,
            longitude=longitude,
            phone=phone,
            hours_of_operation=hours_of_operation,
            locator_domain=locator_domain,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.hertzcarsales.com/"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:97.0) Gecko/20100101 Firefox/97.0",
    }
    with SgRequests() as session:
        with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
            fetch_data(writer)
