import tabula as tb  # noqa
from sglogging import SgLogSetup
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

logger = SgLogSetup().get_logger("napaonline_com")


def write_output(data):
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PhoneNumberId)) as writer:
        for row in data:
            writer.write_row(row)


MISSING = "<MISSING>"


def fetch_pdf():
    dfs = tb.read_pdf(
        "https://static.phdvasia.com/pr/pdf/locations_v2.pdf", pages="all"
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
