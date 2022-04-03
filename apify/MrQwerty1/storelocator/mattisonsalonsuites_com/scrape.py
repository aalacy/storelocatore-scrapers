import ssl
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgselenium import SgChrome


def get_urls():
    r = session.get("https://www.mattisonsalonsuites.com/locations/")
    tree = html.fromstring(r.text)

    return tree.xpath(
        "//a[contains(@id,'button-id-') and contains(@href, '/location/')]/@href"
    )


def get_coords(_id):
    api = "https://www.mattisonsalonsuites.com/wp-admin/admin-ajax.php"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:98.0) Gecko/20100101 Firefox/98.0",
        "Accept": "*/*",
        "Accept-Language": "ru,en-US;q=0.7,en;q=0.3",
        "Accept-Encoding": "gzip, deflate, br",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "X-Requested-With": "XMLHttpRequest",
        "Origin": "https://www.mattisonsalonsuites.com",
        "Connection": "keep-alive",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
    }
    data = {"action": "uxi_locations_single_map_data", "id_number": _id, "post_id": ""}
    r = session.post(api, data=data, headers=headers)
    try:
        j = r.json()["locations"][0]["lat_lng"]
    except:
        j = dict()
    lat = j.get("lat")
    lng = j.get("lng")

    return lat, lng


def get_data(page_url, sgw: SgWriter):
    with SgChrome() as fox:
        fox.get(page_url)
        source = fox.page_source
    tree = html.fromstring(source)

    location_name = "".join(
        tree.xpath("//h1[@class='page-header-title inherit']/text()")
    ).strip()
    street_address = (
        "".join(tree.xpath("//*[@class='company-info-address']/span/span[1]/text()"))
        .replace("\n", ", ")
        .strip()
    )
    if "We " in street_address:
        street_address = street_address.split("We ")[0].strip()
    if "Summerfield Crossing North" in street_address:
        street_address = street_address.replace(
            "Summerfield Crossing North", ""
        ).strip()
    city = "".join(
        tree.xpath("//*[@class='company-info-address']/span/span[2]/text()")
    ).strip()
    state = "".join(
        tree.xpath("//*[@class='company-info-address']/span/span[3]/text()")
    ).strip()
    postal = "".join(
        tree.xpath("//*[@class='company-info-address']/span/span[4]/text()")
    ).strip()
    phone = "".join(
        tree.xpath("//*[@class='company-info-phone']/span/a/text()")
    ).strip()
    if not phone:
        phone = "".join(
            tree.xpath(
                "//a[@id='button-id-1']//span[@class='button-sub-text body-font']/text()"
            )
        ).strip()

    _tmp = []
    days = set(
        tree.xpath(
            "//div[@class='locations-single-address']//span[@class='company-info-hours-day']/text()"
        )
    )
    times = set(
        tree.xpath(
            "//div[@class='locations-single-address']//li[@class='company-info-hours-openclose']/text()"
        )
    )

    for d, t in zip(days, times):
        _tmp.append(f"{d.strip()}: {t.strip()}")

    hours_of_operation = ";".join(_tmp)

    store_number = "".join(tree.xpath("//div[@data-id-number]/@data-id-number"))
    latitude, longitude = get_coords(store_number)

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

    for url in urls:
        get_data(url, sgw)


if __name__ == "__main__":
    locator_domain = "https://www.mattisonsalonsuites.com/"
    ssl._create_default_https_context = ssl._create_unverified_context
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
