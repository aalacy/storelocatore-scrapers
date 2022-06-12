from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from concurrent import futures


def get_urls():
    r = session.get("https://www.timbuk2.com/pages/stores")
    tree = html.fromstring(r.text)

    return tree.xpath("//a[@class='store-locations__button button button--left']/@href")


def get_data(slug, sgw: SgWriter):
    page_url = f"https://www.timbuk2.com{slug}"
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)

    location_name = " ".join(
        tree.xpath(
            "//h2[@class='large-title']/text()|//h3[@class='store-details__subtitle']/text()"
        )
    ).strip()
    line = tree.xpath(
        "//h6[text()='Contact']/following-sibling::div[@class='store-detais__foot_note_body']/p/text()"
    )

    phone = line[-1]
    street_address = ", ".join(line[:-2]).strip()
    line = line[-2]
    city = line.split(",")[0].strip()
    try:
        line = line.split(",")[1].strip()
    except:
        return
    state = line.split()[0]
    postal = line.replace(state, "").strip()
    country_code = "US"
    if len(postal) > 5:
        country_code = "CA"

    hours_of_operation = ";".join(
        tree.xpath(
            "//h6[text()='Hours']/following-sibling::div[@class='store-detais__foot_note_body']/p/text()"
        )
    )

    row = SgRecord(
        page_url=page_url,
        location_name=location_name,
        street_address=street_address,
        city=city,
        state=state,
        zip_postal=postal,
        country_code=country_code,
        phone=phone,
        locator_domain=locator_domain,
        hours_of_operation=hours_of_operation,
    )

    sgw.write_row(row)


def fetch_data(sgw: SgWriter):
    urls = get_urls()

    with futures.ThreadPoolExecutor(max_workers=3) as executor:
        future_to_url = {executor.submit(get_data, url, sgw): url for url in urls}
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":
    locator_domain = "https://www.timbuk2.com/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0"
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
