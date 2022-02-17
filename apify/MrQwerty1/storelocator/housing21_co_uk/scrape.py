from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgpostal import parse_address, International_Parser


def get_international(line):
    _zip = line.split(", ")[-1]
    adr = parse_address(International_Parser(), line, postcode=_zip)
    street_address = f"{adr.street_address_1} {adr.street_address_2 or ''}".replace(
        "None", ""
    ).strip()
    city = adr.city or ""
    if not city:
        city = line.split(",")[-2].strip()
    postal = adr.postcode

    return street_address, city, postal


def get_token():
    api = "https://www.housing21.org.uk/our-properties/search-our-properties/"
    r = session.get(api, headers=headers)
    tree = html.fromstring(r.text)

    return "".join(tree.xpath("//input[@name='__RequestVerificationToken']/@value"))


def get_phone(page_url):
    phone = SgRecord.MISSING
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    xpath = "//a[contains(@href, 'tel:')]/text()"
    phones = set(tree.xpath(xpath))
    if len(phones) > 1:
        for p in phones:
            if p.endswith("4000") or p[0].isalpha():
                continue
            phone = p
            break
    else:
        phone = next(iter(phones))

    return phone


def fetch_data(sgw: SgWriter):
    token = get_token()
    _types = ["210", "209"]

    for _type in _types:
        data = {
            "PurchaseType": _type,
            "Location": "",
            "Longitude": "0",
            "Latitude": "0",
            "SalePriceRange": "",
            "RentPriceRange": "",
            "BedroomsMin": "",
            "BedroomsMax": "",
            "ufprt": "/umbraco/Surface/DevelopmentSearchSurface/AjaxSearch",
            "BuildingType": "0",
            "HousingType": "0",
            "Radius": "40",
            "AvailabilityStatus": "",
            "__RequestVerificationToken": token,
            "orderby": "4",
            "page": "NaN",
        }

        api = "https://www.housing21.org.uk/umbraco/Surface/DevelopmentSearchSurface/AjaxSearch"
        r = session.post(api, headers=headers, data=data)
        js = r.json()["MapJson"]

        for j in js:
            latitude = j.get("Latitude")
            longitude = j.get("Longitude")
            store_number = j.get("Id")
            source = j.get("PopupContent") or "<html></html>"
            if _type == "209":
                location_type = "Rent"
            else:
                location_type = "Buy"

            tree = html.fromstring(source)
            location_name = "".join(
                tree.xpath("//span[@class='m-map_content__heading']/text()")
            ).strip()
            slug = "".join(tree.xpath("//a[@class='e-btn']/@href"))
            page_url = f"https://www.housing21.org.uk{slug}"

            raw_address = " ".join(
                "".join(
                    tree.xpath(
                        "//span[@class='m-map_content__heading']/following-sibling::p[1]/text()"
                    )
                ).split()
            )
            street_address, city, postal = get_international(raw_address)
            try:
                phone = get_phone(page_url)
            except:
                phone = SgRecord.MISSING

            row = SgRecord(
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                zip_postal=postal,
                country_code="GB",
                location_type=location_type,
                store_number=store_number,
                phone=phone,
                latitude=latitude,
                longitude=longitude,
                locator_domain=locator_domain,
                raw_address=raw_address,
            )

            sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.housing21.org.uk/"

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:95.0) Gecko/20100101 Firefox/95.0",
        "Accept": "*/*",
        "Accept-Language": "ru,en-US;q=0.7,en;q=0.3",
        "Accept-Encoding": "gzip, deflate, br",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "X-Requested-With": "XMLHttpRequest",
        "Origin": "https://www.housing21.org.uk",
        "Connection": "keep-alive",
        "Referer": "https://www.housing21.org.uk/our-properties/search-our-properties/",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        fetch_data(writer)
