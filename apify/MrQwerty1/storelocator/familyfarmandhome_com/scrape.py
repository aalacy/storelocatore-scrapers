from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID


def get_hours():
    r = session.get(
        "https://www.familyfarmandhome.com/static/version1645427362/frontend/FamilyFarmAndHome/default/en_US/Upbott_StoreLocator/js/templates/result.html"
    )
    tree = html.fromstring(r.text)

    return " ".join(
        "".join(tree.xpath("//div[@class='store-hours']/span[@class='data']/text()"))
        .strip()
        .replace("\n", ";")
        .split()
    )


def fetch_data(sgw: SgWriter):
    api = "https://www.familyfarmandhome.com/rest/V1/storelocator/search/?searchCriteria%5Bfilter_groups%5D%5B0%5D%5Bfilters%5D%5B0%5D%5Bfield%5D=lat&searchCriteria%5Bfilter_groups%5D%5B0%5D%5Bfilters%5D%5B0%5D%5Bvalue%5D=&searchCriteria%5Bfilter_groups%5D%5B0%5D%5Bfilters%5D%5B0%5D%5Bcondition_type%5D=eq&searchCriteria%5Bfilter_groups%5D%5B0%5D%5Bfilters%5D%5B1%5D%5Bfield%5D=lng&searchCriteria%5Bfilter_groups%5D%5B0%5D%5Bfilters%5D%5B1%5D%5Bvalue%5D=&searchCriteria%5Bfilter_groups%5D%5B0%5D%5Bfilters%5D%5B1%5D%5Bcondition_type%5D=eq&searchCriteria%5Bfilter_groups%5D%5B0%5D%5Bfilters%5D%5B2%5D%5Bfield%5D=store_id&searchCriteria%5Bfilter_groups%5D%5B0%5D%5Bfilters%5D%5B2%5D%5Bvalue%5D=1&searchCriteria%5Bfilter_groups%5D%5B0%5D%5Bfilters%5D%5B2%5D%5Bcondition_type%5D=eq&searchCriteria%5Bfilter_groups%5D%5B0%5D%5Bfilters%5D%5B3%5D%5Bfield%5D=region_id&searchCriteria%5Bfilter_groups%5D%5B0%5D%5Bfilters%5D%5B3%5D%5Bcondition_type%5D=eq&searchCriteria%5Bfilter_groups%5D%5B0%5D%5Bfilters%5D%5B4%5D%5Bfield%5D=search&searchCriteria%5Bfilter_groups%5D%5B0%5D%5Bfilters%5D%5B4%5D%5Bvalue%5D=49440&searchCriteria%5Bfilter_groups%5D%5B0%5D%5Bfilters%5D%5B4%5D%5Bcondition_type%5D=eq&searchCriteria%5Bfilter_groups%5D%5B0%5D%5Bfilters%5D%5B5%5D%5Bfield%5D=distance&searchCriteria%5Bfilter_groups%5D%5B0%5D%5Bfilters%5D%5B5%5D%5Bvalue%5D=3959&searchCriteria%5Bfilter_groups%5D%5B0%5D%5Bfilters%5D%5B5%5D%5Bcondition_type%5D=eq&searchCriteria%5Bfilter_groups%5D%5B0%5D%5Bfilters%5D%5B6%5D%5Bfield%5D=onlyLocation&searchCriteria%5Bfilter_groups%5D%5B0%5D%5Bfilters%5D%5B6%5D%5Bvalue%5D=0&searchCriteria%5Bfilter_groups%5D%5B0%5D%5Bfilters%5D%5B6%5D%5Bcondition_type%5D=eq&searchCriteria%5Bfilter_groups%5D%5B0%5D%5Bfilters%5D%5B7%5D%5Bfield%5D=allLocations&searchCriteria%5Bfilter_groups%5D%5B0%5D%5Bfilters%5D%5B7%5D%5Bvalue%5D=1&searchCriteria%5Bfilter_groups%5D%5B0%5D%5Bfilters%5D%5B7%5D%5Bcondition_type%5D=eq&searchCriteria%5Bfilter_groups%5D%5B0%5D%5Bfilters%5D%5B8%5D%5Bfield%5D=current_store&searchCriteria%5Bfilter_groups%5D%5B0%5D%5Bfilters%5D%5B8%5D%5Bvalue%5D=&searchCriteria%5Bfilter_groups%5D%5B0%5D%5Bfilters%5D%5B8%5D%5Bcondition_type%5D=eq&searchCriteria%5Bcurrent_page%5D=1&searchCriteria%5Bpage_size%5D=100"
    r = session.get(api)
    js = r.json()["items"]

    hours_of_operation = get_hours()

    for j in js:
        street_address = j.get("street") or ""
        city = j.get("city") or ""
        if f", {city}" in street_address:
            street_address = street_address.split(f", {city}")[0].strip()
        state = j.get("region")
        postal = j.get("postal_code")
        country_code = j.get("country_id")
        location_name = j.get("name")
        phone = j.get("phone")
        latitude = j.get("lat")
        longitude = j.get("lng")

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code=country_code,
            phone=phone,
            latitude=latitude,
            longitude=longitude,
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.familyfarmandhome.com/"
    page_url = "https://www.familyfarmandhome.com/locations/"
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.LOCATION_NAME}))
    ) as writer:
        fetch_data(writer)
