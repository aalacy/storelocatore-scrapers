from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from concurrent import futures


def generate_links():
    session = SgRequests()
    r = session.get("https://agents.mutualofomaha.com/district-offices.json")
    js = r.json()["directoryHierarchy"]

    urls = list(get_urls(js))
    return urls


def get_urls(states):
    for state in states.values():
        children = state["children"]
        if children is None:
            yield f"https://agents.mutualofomaha.com/{state['url']}"
        else:
            yield from get_urls(children)


def get_data(url, sgw: SgWriter):
    session = SgRequests()
    r = session.get(url)
    tree = html.fromstring(r.text)

    locator_domain = "https://www.mutualofomaha.com/"
    page_url = url

    street_address = (
        "".join(
            tree.xpath('//div[@class="Core"]//meta[@itemprop="streetAddress"]/@content')
        )
        .replace("\n", "")
        .strip()
    )
    city = (
        "".join(
            tree.xpath('//div[@class="Core"]//span[@class="c-address-city"]/text()')
        ).strip()
        or "<MISSING>"
    )
    state = (
        "".join(
            tree.xpath('//div[@class="Core"]//abbr[@class="c-address-state"]/text()')
        ).strip()
        or "<MISSING>"
    )
    postal = (
        "".join(
            tree.xpath(
                '//div[@class="Core"]//span[@class="c-address-postal-code"]/text()'
            )
        ).strip()
        or "<MISSING>"
    )
    country_code = (
        "".join(tree.xpath('//div[@class="Core"]//address/@data-country')).strip()
        or "<MISSING>"
    )
    location_name = "".join(tree.xpath('//meta[@property="og:title"]/@content'))
    phone = (
        "".join(
            tree.xpath('//div[@class="Core"]//div[@itemprop="telephone"]/text()')
        ).strip()
        or "<MISSING>"
    )
    latitude = (
        "".join(tree.xpath('//div[@class="Core"]//meta[@itemprop="latitude"]/@content'))
        .replace("\n", "")
        .strip()
    )
    longitude = (
        "".join(
            tree.xpath('//div[@class="Core"]//meta[@itemprop="longitude"]/@content')
        )
        .replace("\n", "")
        .strip()
    )
    hours_of_operation = (
        " ".join(tree.xpath('//table[@class="c-hours-details"]//tr//td//text()'))
        .replace("\n", "")
        .strip()
    )
    hours_of_operation = " ".join(hours_of_operation.split())

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


def fetch_data(sgw: SgWriter):

    ids = generate_links()
    with futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(get_data, _id, sgw): _id for _id in ids}
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        fetch_data(writer)
