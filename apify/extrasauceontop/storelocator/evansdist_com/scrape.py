from sgrequests import SgRequests
import PyPDF2  # noqa
import unidecode
from bs4 import BeautifulSoup as bs
from sgscrape import simple_scraper_pipeline as sp


def get_data():
    requests = SgRequests()
    url = "https://www.evansdist.com/detroit-warehousing/"
    response = requests.get(url).text
    soup = bs(response, "html.parser")

    buttons = soup.find_all("div", attrs={"class": "elementor-button-wrapper"})
    names = soup.find_all("h3", attrs={"class": "elementor-image-box-title"})

    x = 0
    for button in buttons:
        if (
            "upload" in button.find("a")["href"]
            and "Company-Overview" not in button.find("a")["href"]
        ):
            x = x + 1
            location_name = names[x - 1].text.strip()
            link = button.find("a")["href"]

            pdf_response = requests.get(link)
            my_raw_data = pdf_response.content

            with open("my_pdf.pdf", "wb") as my_data:
                my_data.write(my_raw_data)

            open_pdf_file = open("my_pdf.pdf", "rb")
            read_pdf = PyPDF2.PdfFileReader(open_pdf_file)

            final_text = unidecode.unidecode(read_pdf.getPage(0).extractText())

            if "PROGRESSIVE DISTRIBUTION CENTERS" in final_text:
                address_parts = [
                    item.strip()
                    for item in final_text.split("PROGRESSIVE DISTRIBUTION CENTERS")[
                        1
                    ].split("\n")
                    if item != ""
                ]

            else:
                address_parts = [
                    item.strip()
                    for item in final_text.split("CENTRAL DETROIT WAREHOUSE")[1].split(
                        "\n"
                    )
                    if item != ""
                ]

            address = address_parts[0]
            city = address_parts[1].split(",")[0]
            state = address_parts[1].split(", ")[1].split(" ")[0]
            zipp = address_parts[1].split(", ")[1].split(" ")[1]
            country_code = "US"

            store_number = "<MISSING>"
            phone = address_parts[2].strip().replace(".", "-")
            location_type = "<MISSING>"
            latitude = "<MISSING>"
            longitude = "<MISSING>"
            hours = "<MISSING>"

            yield {
                "locator_domain": "evansdist.com",
                "page_url": link,
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


def scrape():
    field_defs = sp.SimpleScraperPipeline.field_definitions(
        locator_domain=sp.MappingField(mapping=["locator_domain"]),
        page_url=sp.MappingField(mapping=["page_url"]),
        location_name=sp.MappingField(
            mapping=["location_name"], part_of_record_identity=True
        ),
        latitude=sp.MappingField(mapping=["latitude"], part_of_record_identity=True),
        longitude=sp.MappingField(mapping=["longitude"], part_of_record_identity=True),
        street_address=sp.MultiMappingField(
            mapping=["street_address"], is_required=False, part_of_record_identity=True
        ),
        city=sp.MappingField(mapping=["city"], part_of_record_identity=True),
        state=sp.MappingField(mapping=["state"], is_required=False),
        zipcode=sp.MultiMappingField(mapping=["zip"], is_required=False),
        country_code=sp.MappingField(mapping=["country_code"]),
        phone=sp.MappingField(mapping=["phone"], is_required=False),
        store_number=sp.MappingField(mapping=["store_number"]),
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
