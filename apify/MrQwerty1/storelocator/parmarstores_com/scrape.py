import tabula as tb  # noqa
from lxml import html
from io import BytesIO
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def get_page_url():
    r = session.get("http://www.parmarstores.com/store-locator")
    tree = html.fromstring(r.text)

    return "".join(tree.xpath("//a[contains(@href, '.pdf')]/@href"))


def fetch_data(sgw: SgWriter):
    r = session.get(page_url)
    file = BytesIO(r.content)
    dfs = tb.read_pdf(
        file,
        pages="all",
        pandas_options={
            "columns": [
                "store_number",
                "street_address",
                "city",
                "state",
                "zip_postal",
                "phone",
                "hoo",
                "Diesel",
                "Rec90",
                "Brand",
            ]
        },
    )
    for ab in dfs:
        for _, row in ab.iterrows():
            store_number = row.store_number
            street_address = " ".join(row.street_address.split())
            city = row.city
            state = row.state
            postal = str(row.zip_postal)
            phone = row.phone
            hoo = " ".join(row.hoo.split())
            location_type = " ".join(row.Brand.split())
            if location_type == "Unbrand" or location_type == "x":
                location_type = SgRecord.MISSING
            country_code = "US"
            location_name = "Par Mar Store"

            row = SgRecord(
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=postal,
                country_code=country_code,
                location_type=location_type,
                phone=phone,
                store_number=store_number,
                locator_domain=locator_domain,
                hours_of_operation=hoo,
            )

            sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    locator_domain = "http://www.parmarstores.com/"
    page_url = get_page_url()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        fetch_data(writer)
