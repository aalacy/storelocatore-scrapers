from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from concurrent import futures
from sgscrape.sgpostal import parse_address, International_Parser


def get_international(line):
    adr = parse_address(International_Parser(), line)
    street_address = f"{adr.street_address_1} {adr.street_address_2 or ''}".replace(
        "None", ""
    ).strip()
    city = adr.city
    state = adr.state
    postal = adr.postcode

    return street_address, city, state, postal


def get_countries():
    cs = dict()
    r = session.get(
        "https://www.savills.com/_vx/sv-CountryListing.aspx?listingType=Web.Office"
    )
    tree = html.fromstring(r.text)
    elements = tree.xpath("//option")
    for el in elements:
        key = "".join(el.xpath("./@value"))
        value = "".join(el.xpath("./text()"))
        cs[key] = value

    return cs


def get_raw_address(page_url):
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    return " ".join(
        " ".join(
            tree.xpath("//span[@class='sv-contact-header__location']/text()")
        ).split()
    )


def get_data(_id, sgw: SgWriter):
    for i in range(1, 50):
        params = (
            ("page", i),
            ("countrySiteId", _id),
            ("sectorId", ""),
            ("sortOrder", "asc"),
            ("nameSearchValue", ""),
            ("lon", ""),
            ("lat", ""),
            ("location", ""),
        )
        r = session.get(
            "https://www.savills.com/_vx/sv-OfficeListingResults.aspx", params=params
        )
        tree = html.fromstring(r.text)
        divs = tree.xpath("//div[@class='sv-col']")

        for d in divs:
            slug = "".join(d.xpath(".//span[@class='sv-cta-link']/a/@href"))
            page_url = f"https://www.savills.com{slug}"
            location_name = "".join(d.xpath(".//h3/text()")).strip()
            raw_address = get_raw_address(page_url)
            street_address, city, state, postal = get_international(raw_address)
            country_code = countries.get(_id)
            phone = "".join(
                d.xpath(".//p[contains(@class, 'telephone')]//text()")
            ).strip()

            if slug:
                store_number = slug.split("=")[-1]
            else:
                store_number = SgRecord.MISSING

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
                raw_address=raw_address,
            )

            sgw.write_row(row)

        if len(divs) < 12:
            break


def fetch_data(sgw: SgWriter):
    with futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {
            executor.submit(get_data, _id, sgw): _id for _id in countries.keys()
        }
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":
    session = SgRequests()
    countries = get_countries()
    locator_domain = "https://www.savills.com/"
    with SgWriter(
        SgRecordDeduper(
            RecommendedRecordIds.StoreNumberId, duplicate_streak_failure_factor=-1
        )
    ) as writer:
        fetch_data(writer)
