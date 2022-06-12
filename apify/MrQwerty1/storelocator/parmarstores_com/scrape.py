import tabula as tb  # noqa
from io import BytesIO
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


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
            street_address = row.street_address
            city = row.city
            state = row.state
            postal = str(row.zip_postal)
            phone = row.phone
            hoo = row.hoo
            location_type = row.Brand
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
    locator_domain = "http://www.parmarstores.com/"
    page_url = (
        "http://www.parmarstores.com/wp-content/uploads/2022/03/Par-Mar-Stores.pdf"
    )
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        fetch_data(writer)
