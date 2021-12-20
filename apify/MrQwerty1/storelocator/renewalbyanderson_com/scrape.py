from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from concurrent import futures


def get_urls():
    r = session.get(
        "https://www.renewalbyandersen.com/about/renewal-by-andersen-showrooms"
    )
    tree = html.fromstring(r.text)

    return set(
        tree.xpath(
            "//div[@class='row component column-splitter ']//a[contains(@href, 'window-company')]/@href"
        )
    )


def get_data(page_url, sgw: SgWriter):
    store_number = page_url.split("/")[-2].split("-")[0]
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    divs = tree.xpath("//div[contains(@class, 'micrositeshowroom micrositeshowroom')]")
    for d in divs:
        location_name = "".join(d.xpath("./h2/text()")).strip()
        line = d.xpath(".//address/text()")
        line = list(filter(None, [l.strip() for l in line]))
        street_address = ", ".join(line[:-1])
        line = line[-1]
        city = line.split(",")[0].strip()
        line = line.split(",")[1].strip()
        state = line.split()[0]
        postal = line.replace(state, "").strip()
        country_code = "US"
        if len(postal) > 5:
            country_code = "CA"
        phone = "".join(d.xpath(".//a/text()")).strip()

        _tmp = []
        hours = d.xpath(
            ".//h3[contains(text(), 'STORE HOURS')]/following-sibling::ul/li"
        )
        for h in hours:
            day = "".join(h.xpath("./span/text()")).strip()
            inter = "".join(h.xpath("./text()")).strip()
            _tmp.append(f"{day} {inter}")
        hours_of_operation = ";".join(_tmp)

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code=country_code,
            store_number=store_number,
            phone=phone,
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


def fetch_data(sgw: SgWriter):
    urls = get_urls()

    with futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(get_data, url, sgw): url for url in urls}
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":
    locator_domain = "https://www.renewalbyandersen.com/"
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
