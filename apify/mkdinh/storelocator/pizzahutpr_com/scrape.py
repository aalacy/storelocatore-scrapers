import tabula as tb  # noqa
from io import BytesIO

from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

logger = SgLogSetup().get_logger("pizzahutpr_com")


def write_output(data):
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PhoneNumberId)) as writer:
        for row in data:
            writer.write_row(row)


MISSING = "<MISSING>"


def fetch_pdf():
    with SgRequests() as session:
        response = session.get(
            "https://static.phdvasia.com/pr/pdf/locations_v2.pdf",
            headers={"User-Agent": "PostmanRuntime/7.19.0"},
        )
        file = BytesIO(response.content)

        dfs = tb.read_pdf(
            file,
            pages=1,
        )

    return dfs[0]


def fetch_data():
    df = fetch_pdf()
    df.rename(columns={"PUEBLO": "location_name", "Unnamed: 0": "phone"}, inplace=True)

    locations = []
    current_city = None
    for idx, row in df.iterrows():
        name = row.location_name
        phone = row.phone

        if name.isupper():
            current_city = name
            if phone:
                locations.append(SgRecord(city=current_city, phone=phone))
        else:
            location_name = name
            locations.append(
                SgRecord(city=current_city, phone=phone, location_name=location_name)
            )

    yield from locations


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
