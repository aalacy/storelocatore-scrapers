from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
import re
from sgscrape import simple_scraper_pipeline as sp

def get_data():
    session = SgRequests()
    url = "https://vitalitybowls.com/all-locations/"

    response = session.get(url).text
    soup = bs(response, "html.parser")

    loc_urls = [
        a_tag["href"]
        for a_tag in soup.find_all("a", attrs={"class": "locationurl"})
        if "coming soon" not in a_tag.text.strip().lower()
    ]

    for page_url in loc_urls:
        if page_url == "https://vitalitybowls.com/san-jose-brokaw/":
            page_url = "https://vitalitybowls.com/locations/san-jose-brokaw/"
        if page_url == "https://vitalitybowls.com/las-vegas-centennial-hills/":
            page_url = "https://vitalitybowls.com/locations/las-vegas-centennial-hills/"

        response = session.get(page_url).text
        soup = bs(response, "html.parser")
        locator_domain = "vitalitybowls.com"
        location_name = soup.find(
            "h2", attrs={"class": "et_pb_slide_title"}
        ).text.strip()

        if "What Are Our Customers Saying?" in location_name:
            location_name = (
                soup.find("div", attrs={"class": "et_pb_row et_pb_row_0"})
                .text.strip()
                .split("\n")[0]
            )

        print(location_name)
        print(page_url)

        address_sections = str(soup.find_all("div", attrs={"class": "et_pb_text_inner"})[1]).split("\n")
        
        address_parts = []

        begin = "no"
        for section in address_sections:
            
            if begin == "yes":
                address_parts = bs(section, "html.parser")
                break

            if "STORE INFO" in section:
                begin = "yes"

        address_pieces = []
        for part in str(address_parts).split("<br/>"):
            text = bs(part, "html.parser").text.strip()
            address_pieces.append(text)
        print(address_pieces)
        print("")
        print("")


get_data()
