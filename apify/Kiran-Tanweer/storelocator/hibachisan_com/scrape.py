import tabula as tb  # noqa
from io import BytesIO
from math import isnan

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def write_output(data):
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.LOCATION_NAME}))
    ) as writer:
        for row in data:
            writer.write_row(row)


def fetch_locations():
    url = "https://hibachisanwebsite.s3.amazonaws.com/Hibachi+San+Locations.pdf"
    with SgRequests() as session:
        response = session.get(url)
        file = BytesIO(response.content)

        dfs = tb.read_pdf(
            file,
            pages="all",
            pandas_options={
                "columns": [
                    "location_name",
                    "street_address",
                    "city",
                    "state",
                    "zip_postal",
                    "phone",
                ]
            },
        )

        return dfs[0]


def get_phone(row):
    if isinstance(row.phone, float) and isnan(row.phone):
        return SgRecord.MISSING
    return row.phone


def fetch_data():
    df = fetch_locations()

    for _, row in df.iterrows():
        yield SgRecord(
            locator_domain="hibachisan.com",
            location_name=row.location_name,
            street_address=row.street_address,
            city=row.city,
            zip_postal=str(row.zip_postal),
            phone=get_phone(row),
        )


if __name__ == "__main__":
    data = fetch_data()
    write_output(data)
