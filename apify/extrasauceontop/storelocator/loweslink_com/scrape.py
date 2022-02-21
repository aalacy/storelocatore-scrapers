import PyPDF2  # noqa
from sgrequests import SgRequests
import unidecode
from sgscrape import simple_scraper_pipeline as sp

session = SgRequests()


def parse_pdf(pdf_url, x):
    pdf_response = session.get(pdf_url)
    my_raw_data = pdf_response.content

    with open("my_pdf.pdf", "wb") as my_data:
        my_data.write(my_raw_data)

    open_pdf_file = open("my_pdf.pdf", "rb")
    read_pdf = PyPDF2.PdfFileReader(open_pdf_file)

    final_text = (
        unidecode.unidecode(read_pdf.getPage(x).extractText())
        .replace("\n-", "-")
        .replace("\t", "")
        .replace("(tm)", "'")
        .replace("  Lowe's", "   Lowe's")
    )

    return final_text


def parse_into_lines(pdf_text):
    while "    " in pdf_text:
        pdf_text = pdf_text.replace("    ", "   ")

    pdf_text = pdf_text.replace("   ", "---")

    while "  " in pdf_text:
        pdf_text = pdf_text.replace("  ", " ")

    final_lines = []
    for line in pdf_text.split("\n"):
        if line == "---Lowe's Mid-Atlantic RDC - #14":
            line = "---Lowe's Mid-Atlantic RDC - #1420"
        line = line.replace(":---", ": ")
        if line[:3] == "---":
            line = "last-+-" + line[3:]
        for part in line.split("---"):
            if (
                "Lowe's Franklin County, TX SDC #983 Lowe's Internet Fulfillment Center - #907"
                in part
            ):
                final_lines.append("Lowe's Franklin County, TX SDC #983")
                final_lines.append("Lowe's Internet Fulfillment Center - #907")
            elif len(part) > 2:
                final_lines.append(part.strip())

    return final_lines


def is_name_line(line):
    if "#" in line:
        check = line.split("#")[1]
        x = 0
        for character in check:
            if character.isnumeric() is True:
                x = x + 1
                if x == 3:
                    return True

            else:
                x = 0

    return False


def parse_location_section(location_list):
    grouped_lists = []

    x = 0
    if len(location_list) % 2 == 0 and len(location_list) > 6:
        list_1 = []
        list_2 = []
        for item in location_list:

            if x % 2 == 0:
                list_1.append(item)

            else:
                list_2.append(item)

            x = x + 1

        grouped_lists.append(list_1)
        grouped_lists.append(list_2)

    elif len(location_list) < 7:
        grouped_lists.append(location_list)

    elif len(location_list) % 2 == 1:
        list_1 = []
        list_2 = []
        for item in location_list[:-1]:

            if x % 2 == 0:
                list_1.append(item)

            else:
                list_2.append(item)

            x = x + 1
        grouped_lists.append(list_1)
        grouped_lists.append(list_2)

        if "last-+-" in location_list[-1]:
            list_2.append(location_list[-1])

        else:
            list_1.append(location_list[-1])

        grouped_lists.append(list_1)
        grouped_lists.append(list_2)

    else:
        raise Exception

    locs = []
    for location in grouped_lists:
        locator_domain = "loweslink.com"
        page_url = "https://www.loweslink.com/llmain/pubdocuments/distribution%20center%20information.pdf"
        location_name = location[0]
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        store_number = location[0].split("#")[1].strip()
        location_type = "<MISSING>"
        hours = "<MISSING>"

        address_parts = location[1:-1]

        if len(address_parts) == 2:
            address = address_parts[0]

        if len(address_parts) == 3:
            address = address_parts[0] + " " + address_parts[1]

        city = location[-2].split(",")[0].replace("th Street", "")
        state = location[-2].split(", ")[1].split(" ")[0]
        zipp = location[-2].split(", ")[1].split(" ")[1]

        phone = (
            location[-1].lower().replace("phone", "").replace(" ", "").replace(":", "")
        )
        country_code = "US"
        locs.append(
            {
                "locator_domain": locator_domain,
                "page_url": page_url,
                "location_name": location_name,
                "latitude": latitude,
                "longitude": longitude,
                "city": city,
                "store_number": store_number,
                "street_address": address,
                "state": state,
                "zip": zipp,
                "phone": phone,
                "location_type": location_type,
                "hours": hours,
                "country_code": country_code,
            }
        )

    return locs


def get_data():
    pdf_url = "https://www.loweslink.com/llmain/pubdocuments/distribution%20center%20information.pdf"
    x = 0
    all_lines = []
    while True:
        try:
            pdf_text = (
                parse_pdf(pdf_url, x)
                .replace("w\ne", "we")
                .replace("Phone:\n", "Phone: ")
            )
            final_text = parse_into_lines(pdf_text)
            for line in final_text:
                if x != 1:
                    line = line.replace("last-+-", "")
                    if len(line) > 2:
                        all_lines.append(line)
                else:
                    all_lines.append(line)

            x = x + 1
        except Exception:
            break

    index = 0
    end = 0
    all_locations = []
    for line in all_lines:
        if index < end:
            index = index + 1
            continue

        elif is_name_line(line) is True:
            if is_name_line(all_lines[index + 1]):
                last_index = index + 2
                while True:
                    last_index = last_index + 1
                    try:
                        if (
                            is_name_line(all_lines[last_index]) is True
                            or "DC)" in all_lines[last_index]
                            or "Fax:" in all_lines[last_index][:4]
                        ):
                            end = last_index
                            locs = parse_location_section(all_lines[index:last_index])
                            for loc in locs:
                                yield loc
                            break

                    except Exception:
                        locs = parse_location_section(all_lines[index:last_index])
                        for loc in locs:
                            yield loc
                        break

            else:
                last_index = index + 1
                while True:
                    last_index = last_index + 1

                    try:
                        if (
                            is_name_line(all_lines[last_index]) is True
                            or "DC)" in all_lines[last_index]
                            or "Fax:" in all_lines[last_index][:4]
                        ):
                            end = last_index
                            locs = parse_location_section(all_lines[index:last_index])
                            for loc in locs:
                                yield loc
                            break

                    except Exception:
                        locs = parse_location_section(all_lines[index:last_index])
                        for loc in locs:
                            yield loc
                        break
        else:
            pass

        index = index + 1

    for location in all_locations:
        yield location


def scrape():
    field_defs = sp.SimpleScraperPipeline.field_definitions(
        locator_domain=sp.MappingField(mapping=["locator_domain"]),
        page_url=sp.MappingField(mapping=["page_url"], is_required=False),
        location_name=sp.MappingField(
            mapping=["location_name"], part_of_record_identity=True
        ),
        latitude=sp.MappingField(mapping=["latitude"], is_required=False),
        longitude=sp.MappingField(mapping=["longitude"], is_required=False),
        street_address=sp.MultiMappingField(
            mapping=["street_address"], part_of_record_identity=True
        ),
        city=sp.MappingField(
            mapping=["city"],
        ),
        state=sp.MappingField(mapping=["state"], is_required=False),
        zipcode=sp.MultiMappingField(mapping=["zip"], is_required=False),
        country_code=sp.MappingField(mapping=["country_code"]),
        phone=sp.MappingField(mapping=["phone"], is_required=False),
        store_number=sp.MappingField(
            mapping=["store_number"], part_of_record_identity=True
        ),
        hours_of_operation=sp.MappingField(mapping=["hours"], is_required=False),
        location_type=sp.MappingField(mapping=["location_type"], is_required=False),
    )

    pipeline = sp.SimpleScraperPipeline(
        scraper_name="Crawler",
        data_fetcher=get_data,
        field_definitions=field_defs,
        log_stats_interval=15,
    )
    pipeline.run()


scrape()
