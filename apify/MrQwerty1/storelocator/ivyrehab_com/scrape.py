from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from concurrent import futures


def get_urls():
    r = session.get("https://www.ivyrehab.com/locations/", headers=headers)
    tree = html.fromstring(r.text)

    return tree.xpath("//div[@class='fwpl-item el-i1ybmv button smallest']/a/@href")


def get_hours(_id):
    api = f"https://knowledgetags.yextpages.net/embed?key=EwOOPFqqshYCRf_I0uRL3od4NjOoYC58Pot0yJLo_w5uAVTrvk-XLy9Y53ilVGut&account_id=1341034&location_id={_id}"
    r = session.get(api, headers=headers)

    try:
        text = r.text.split('"hours":')[1].split("]")[0] + "]"
        hours = ";".join(eval(text))
    except:
        hours = SgRecord.MISSING

    return hours


def get_data(page_url, sgw: SgWriter):
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)

    location_name = "".join(tree.xpath("//h1/text()")).strip()
    line = tree.xpath("//h4[@class='h4 ff-ProximaNova-Regular']/text()")
    line = list(filter(None, [l.strip() for l in line]))

    street_address = line[0]
    line = line[-1]
    city = line.split(",")[0].strip()
    line = line.split(",")[1].strip()
    state = line.split()[0]
    postal = line.split()[1]
    store_number = "".join(
        tree.xpath("//script[contains(@src, 'location_id=')]/@src")
    ).split("=")[-1]
    phone = "".join(tree.xpath("//h2[@class='phone-number']/text()")).strip()
    latitude = "".join(tree.xpath("//div[@data-lat]/@data-lat"))
    longitude = "".join(tree.xpath("//div[@data-lat]/@data-lng"))
    if store_number:
        hours_of_operation = get_hours(store_number)
    else:
        _tmp = []
        divs = tree.xpath("//div[@class='lh-day']")
        for d in divs:
            day = "".join(d.xpath("./div[1]//text()")).strip()
            time = "".join(d.xpath("./div[2]//text()")).strip()
            _tmp.append(f"{day}: {time}")

        hours_of_operation = " ".join(";".join(_tmp).split())

    row = SgRecord(
        page_url=page_url,
        location_name=location_name,
        street_address=street_address,
        city=city,
        state=state,
        zip_postal=postal,
        country_code="US",
        store_number=store_number,
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
    locator_domain = "https://www.ivyrehab.com/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0"
    }
    with SgRequests() as session:
        with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
            fetch_data(writer)
