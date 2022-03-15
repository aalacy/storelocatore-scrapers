from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgpostal import parse_address, International_Parser


def get_international(line):
    adr = parse_address(International_Parser(), line)
    street_address = f"{adr.street_address_1} {adr.street_address_2 or ''}".replace(
        "None", ""
    ).strip()
    city = adr.city or ""
    state = adr.state
    postal = adr.postcode

    return street_address, city, state, postal


def fetch_data(sgw: SgWriter):
    page_url = "https://breatheoutdoors.ca/contact"
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)

    _tmp = []
    hours = tree.xpath("//h4[contains(text(), 'Holiday')]/preceding-sibling::p/strong")
    for h in hours:
        day = "".join(h.xpath("./text()")).replace("|", "").strip()
        inter = "".join(h.xpath("./following-sibling::text()[1]")).strip()
        _tmp.append(f"{day}: {inter}")
    hours_of_operation = ";".join(_tmp)

    divs = tree.xpath(
        "//p[contains(text(), 'Locations')]/following-sibling::div[1]/div"
    )
    for d in divs:
        location_name = "".join(d.xpath(".//h3/text()")).strip()
        text = "".join(d.xpath(".//a/@href"))
        raw_address = text.split("/@")[0].split("/")[-1].replace("+", " ")
        street_address, city, state, postal = get_international(raw_address)
        phones = d.xpath(
            ".//strong[contains(text(), 'Local')]/following-sibling::text()"
        )
        phones = list(filter(None, [p.strip() for p in phones]))
        phone = phones.pop(0)
        latitude, longitude = text.split("/@")[1].split(",")[:2]

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code="CA",
            latitude=latitude,
            longitude=longitude,
            phone=phone,
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
            raw_address=raw_address,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://breatheoutdoors.ca/"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:96.0) Gecko/20100101 Firefox/96.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Cache-Control": "max-age=0",
        "TE": "trailers",
    }

    cookies = {
        "PHPSESSID": "8codpatg8k8gkn2ev945arsvkr",
        "mage-translation-storage": "%7B%7D",
        "mage-translation-file-version": "%7B%7D",
        "mage-cache-storage": "%7B%7D",
        "mage-cache-storage-section-invalidation": "%7B%7D",
        "_ga": "GA1.2.402640478.1642594791",
        "_gid": "GA1.2.1476887003.1642594791",
        "_gat_gtag_UA_23413564_1": "1",
        "_fbp": "fb.1.1642594791646.1105014571",
        "fastest-popup": "true",
        "customer-data-setting": "%7B%22sectionLoadUrl%22%3A%22https%3A%2F%2Fbreatheoutdoors.ca%2Fcustomer%2Fsection%2Fload%2F%22%2C%22expirableSectionLifetime%22%3A60%2C%22expirableSectionNames%22%3A%5B%22cart%22%2C%22persistent%22%5D%2C%22cookieLifeTime%22%3A%223600%22%2C%22updateSessionUrl%22%3A%22https%3A%2F%2Fbreatheoutdoors.ca%2Fcustomer%2Faccount%2FupdateSession%2F%22%7D",
        "mage-cache-sessid": "true",
        "form_key": "pW82zuBdDfb2m6X9",
        "_gat": "1",
        "mage-messages": "",
        "searchsuiteautocomplete": "%7B%7D",
        "recently_viewed_product": "%7B%7D",
        "recently_viewed_product_previous": "%7B%7D",
        "recently_compared_product": "%7B%7D",
        "recently_compared_product_previous": "%7B%7D",
        "product_data_storage": "%7B%7D",
    }
    session = SgRequests(proxy_country="ca")
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PhoneNumberId)) as writer:
        fetch_data(writer)
