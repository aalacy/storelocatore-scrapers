import re
from io import BytesIO
import tabula as tb  # noqa

from sgrequests import SgRequests
from sgscrape.sgpostal import USA_Best_Parser, parse_address
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


DOMAIN = "anderinger.com"
pdf_url = "https://www.anderinger.com/wp-content/uploads/2021/03/Deringer-locations-page-3-23-21.pdf"


def write_output(data):
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.LOCATION_NAME}))
    ) as writer:
        for row in data:
            writer.write_row(row)


def read_pdf():
    table_column_boundaries = [150, 300, 430, 580]
    area = [0.0, 0.0, 800.0, 600.0]
    with SgRequests() as session:
        response = session.get(pdf_url, headers={"User-Agent": "PostmanRuntime/7.19.0"})
        file = BytesIO(response.content)

        dataframes = tb.read_pdf(
            file,
            pages="all",
            area=area,
            lattice=True,
            columns=table_column_boundaries,
        )

    data = []
    df = dataframes[0]
    for column in range(0, len(df.columns)):
        if not isinstance(df.iloc[0, column], str):
            data.append(
                df.columns[column]
            )  # data parsed out as column name in pd dataframe
        else:
            data.append(df.iloc[0, column])

    unformatted = "\n".join(data)
    return re.sub("\r", "\n", unformatted)


def group_by_state(data):
    lines = data.split("\n")

    buckets = {}
    current = None
    for line in lines:
        if line.isupper() and "PO BOX" not in line:
            buckets[line] = []
            current = buckets[line]
            continue

        current.append(line)

    return buckets


def group_by_city(states):
    cities = {}
    current_state = None
    current_city = None
    current_city_data = None

    for state, lines in states.items():
        current_state = state
        for idx, line in enumerate(lines):
            if "–" in line or idx == 0:
                if current_city_data:
                    cities[current_city] = current_city_data

                current_city = line
                current_city_data = []
                current_city_data.append(current_state)
                current_city_data.append(line)

            else:
                current_city_data.append(line)

            if idx == len(lines) - 1:
                cities[current_city] = current_city_data

    return cities


def get_phone(data):
    for line in data:
        if re.search(r"tel\s*:\s*", line, re.IGNORECASE):
            return re.sub(r"tel\s*:\s*|\s*\|\s*.*", "", line, flags=re.IGNORECASE)


def get_store_number(name):
    if "–" in name:
        parsed = name.split(" – ")
        return parsed[1]

    return MISSING


def get_location_type(data):
    if re.search("headquarter", data[0], flags=re.IGNORECASE):
        return "CORPORATE HEADQUARTERS"

    return MISSING


def get_address(data):
    address = ",".join(data[2:4])

    if "PO BOX" in address:
        address = ",".join(data[4:6])

    if re.search(r"tel\s*:\s*", address, flags=re.IGNORECASE):
        address = ""

    return address


MISSING = "<MISSING>"


def extract(name, data):
    address = get_address(data)
    if address is None:
        return None

    parsed_address = parse_address(USA_Best_Parser(), address)

    locator_domain = "anderinger.com"
    page_url = pdf_url
    location_name = name
    street_address = parsed_address.street_address_1
    city = parsed_address.city
    state = parsed_address.state
    postal = parsed_address.postcode
    country_code = parsed_address.country
    store_number = get_store_number(name)
    phone = get_phone(data)
    location_type = get_location_type(data)
    latitude = MISSING
    longitude = MISSING
    hours_of_operation = MISSING

    return SgRecord(
        locator_domain=locator_domain,
        page_url=page_url,
        location_name=location_name,
        street_address=street_address,
        city=city,
        state=state,
        zip_postal=postal,
        country_code=country_code,
        store_number=store_number,
        phone=phone,
        location_type=location_type,
        latitude=latitude,
        longitude=longitude,
        hours_of_operation=hours_of_operation,
    )


def fetch_data():
    data = read_pdf()
    states = group_by_state(data)
    locations = group_by_city(states)

    for name, data in locations.items():
        poi = extract(name, data)
        if poi:
            yield poi


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
