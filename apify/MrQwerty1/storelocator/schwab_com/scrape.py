from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from concurrent import futures
from sglogging import sglog


def get_urls():
    urls = []
    start = [
        "https://client.schwab.com/Public/BranchLocator/ViewAllBranches_abc.aspx?",
        "https://client.schwab.com/Public/BranchLocator/ViewAllBranches_defghil.aspx?",
        "https://client.schwab.com/Public/BranchLocator/ViewAllBranches_mn.aspx?",
        "https://client.schwab.com/Public/BranchLocator/ViewAllBranches_opqrstuvw.aspx?",
    ]

    for s in start:
        r = session.get(s, headers=headers)
        tree = html.fromstring(r.content)
        links = tree.xpath("//a[@class='popup']/@href")
        urls += links

    return urls


def get_data(page_url, sgw: SgWriter):
    r = session.get(page_url, headers=headers)
    logger.info(f"{page_url}: {r.status_code}")

    if r.status_code != 200:
        return
    tree = html.fromstring(r.text)
    location_name = "".join(
        tree.xpath(
            "//h2[@id='ctl00_wpMngr_BranchDetail_BranchDetails_dynPageTitle']/text()"
        )
    ).strip()
    line = tree.xpath(
        "//p[@id='ctl00_wpMngr_BranchDetail_BranchDetails_brAddress']/text()"
    )
    line = list(filter(None, [l.strip() for l in line]))
    if not line:
        logger.info(f"{page_url} is broken")
        return

    street_address = line.pop(0)
    csz = line.pop()
    city = csz.split(",")[0].strip()
    csz = csz.split(",")[1].strip()
    state, postal = csz.split()
    store_number = page_url.split("=")[-1]
    phone = tree.xpath("//span[@data-active='mobile']/text()")[0].strip()
    location_type = "Branch"
    latitude, longitude = SgRecord.MISSING, SgRecord.MISSING

    _tmp = []
    tr = tree.xpath("//div[@id='hours-furl-content']/table[@class='hours']//tr")
    for t in tr:
        _tmp.append(" ".join(t.xpath("./td/text()")).strip())

    hours_of_operation = ";".join(_tmp)
    isclosed = tree.xpath("//p[contains(text(), 'temporarily closed')]")
    if isclosed:
        hours_of_operation = "Temporarily Closed"

    iscoming = tree.xpath("//p[contains(text(), 'Coming soon')]")
    if iscoming:
        hours_of_operation = "Coming Soon"

    row = SgRecord(
        page_url=page_url,
        location_name=location_name,
        street_address=street_address,
        city=city,
        state=state,
        zip_postal=postal,
        country_code="US",
        store_number=store_number,
        location_type=location_type,
        latitude=latitude,
        longitude=longitude,
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
    locator_domain = "https://www.schwab.com/"
    logger = sglog.SgLogSetup().get_logger(logger_name="schwab.com")

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0"
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
