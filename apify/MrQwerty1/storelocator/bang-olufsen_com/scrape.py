from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from concurrent import futures


def get_urls():
    urls = []
    for i in range(50):
        r = session.get(f"https://stores.bang-olufsen.com/sitemap.xml.{i}")
        if r.status_code == 404:
            break
        tree = html.fromstring(r.content)
        check = tree.xpath("//loc")
        links = tree.xpath("//loc[contains(text(), '/en/')]/text()")
        for link in links:
            if "/headphones" in link or "/home-theater" in link:
                continue
            if "united-states" not in link:
                if link.count("/") >= 6:
                    urls.append(link)
            else:
                if link.count("/") > 6:
                    urls.append(link)

        if not check:
            break

    return set(urls)


def get_data(page_url, sgw: SgWriter):
    r = session.get(page_url)
    if r.status_code == 200:
        tree = html.fromstring(r.text)

        location_name = (
            "".join(tree.xpath("//h1[@itemprop='name']/text()")).strip()
            or "Bang & Olufsen"
        )
        if tree.xpath("//div[@class='Directory-content']"):
            return
        street_address = ", ".join(
            tree.xpath("//span[contains(@class, 'c-address-street')]/text()")
        ).strip()
        city = "".join(tree.xpath("//span[@class='c-address-city']/text()")).strip()
        state = "".join(tree.xpath("//span[@class='c-address-state']/text()")).strip()
        postal = "".join(
            tree.xpath("//span[@class='c-address-postal-code']/text()")
        ).strip()
        country = "".join(tree.xpath("//*[@itemprop='addressCountry']/text()")).strip()
        if not country:
            country = (
                page_url.split("/en/")[1].split("/")[0].replace("-", " ").capitalize()
            )

        phone = "".join(
            tree.xpath("//div[contains(@class, 'Core-phone')]/text()")
        ).strip()
        try:
            latitude = tree.xpath("//meta[@itemprop='latitude']/@content")[0]
            longitude = tree.xpath("//meta[@itemprop='longitude']/@content")[0]
        except IndexError:
            latitude, longitude = SgRecord.MISSING, SgRecord.MISSING

        _tmp = []
        hours = tree.xpath("//tr[@itemprop='openingHours']")
        for h in hours:
            day = " ".join("".join(h.xpath("./td[1]//text()")).split())
            inter = " ".join("".join(h.xpath("./td[2]//text()")).split())
            _tmp.append(f"{day}: {inter}")

        hours_of_operation = ";".join(_tmp)

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            latitude=latitude,
            longitude=longitude,
            country_code=country,
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
    locator_domain = "https://bang-olufsen.com/"
    session = SgRequests()

    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
