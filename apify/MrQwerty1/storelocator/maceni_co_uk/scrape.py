from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgzip.dynamic import SearchableCountries, DynamicZipSearch


def get_phones(page_url):
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)

    return tree.xpath("//span[contains(text(), 'Telephone')]/following-sibling::text()")


def fetch_data(sgw: SgWriter):
    search = DynamicZipSearch(
        country_codes=[SearchableCountries.BRITAIN], expected_search_radius_miles=20
    )
    for _zip in search:
        api = f"http://www.maceni.co.uk/stores/markers/{_zip}/2000/"
        page_url = f"http://www.maceni.co.uk/stores/results/{_zip}/2000/"
        r = session.get(api, headers=headers)
        if r.status_code != 200:
            search.found_nothing()
            continue

        tree = html.fromstring(r.content)
        divs = tree.xpath("//marker")
        if not divs:
            search.found_nothing()
            continue

        phones = get_phones(page_url)
        for d, phone in zip(divs, phones):
            street_address = "".join(d.xpath("./@address1"))
            city = "".join(d.xpath("./@city"))
            postal = "".join(d.xpath("./@postcode"))
            country_code = "GB"
            location_name = "".join(d.xpath("./@name"))
            latitude = "".join(d.xpath("./@lat"))
            longitude = "".join(d.xpath("./@lng"))
            search.found_location_at(latitude, longitude)

            row = SgRecord(
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                zip_postal=postal,
                country_code=country_code,
                latitude=latitude,
                longitude=longitude,
                phone=phone,
                locator_domain=locator_domain,
            )

            sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "http://www.maceni.co.uk/"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:97.0) Gecko/20100101 Firefox/97.0",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
