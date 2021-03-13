from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
import re


def _headers():
    return {
        "referer": "https://www.calranch.com/storelocator/",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36",
        "accept": "application/json, text/javascript, */*; q=0.01",
        "accept-language": "en-US,en;q=0.9,ko;q=0.8",
    }


def _valid1(val):
    if val:
        return (
            val.strip()
            .replace("–", "-")
            .encode("unicode-escape")
            .decode("utf8")
            .replace("\\xa0", "")
            .replace("\\xa0\\xa", "")
            .replace("\\xae", "")
        )
    else:
        return ""


def fetch_data():
    with SgRequests() as session:
        locator_domain = "https://www.calranch.com/"
        base_url = "https://www.calranch.com/rest/V1/storelocator/search/?searchCriteria%5Bfilter_groups%5D%5B0%5D%5Bfilters%5D%5B0%5D%5Bfield%5D=lat&searchCriteria%5Bfilter_groups%5D%5B0%5D%5Bfilters%5D%5B0%5D%5Bvalue%5D=&searchCriteria%5Bfilter_groups%5D%5B0%5D%5Bfilters%5D%5B0%5D%5Bcondition_type%5D=eq&searchCriteria%5Bfilter_groups%5D%5B0%5D%5Bfilters%5D%5B1%5D%5Bfield%5D=lng&searchCriteria%5Bfilter_groups%5D%5B0%5D%5Bfilters%5D%5B1%5D%5Bvalue%5D=&searchCriteria%5Bfilter_groups%5D%5B0%5D%5Bfilters%5D%5B1%5D%5Bcondition_type%5D=eq&searchCriteria%5Bfilter_groups%5D%5B0%5D%5Bfilters%5D%5B2%5D%5Bfield%5D=country_id&searchCriteria%5Bfilter_groups%5D%5B0%5D%5Bfilters%5D%5B2%5D%5Bcondition_type%5D=eq&searchCriteria%5Bfilter_groups%5D%5B0%5D%5Bfilters%5D%5B3%5D%5Bfield%5D=region_id&searchCriteria%5Bfilter_groups%5D%5B0%5D%5Bfilters%5D%5B3%5D%5Bcondition_type%5D=eq&searchCriteria%5Bfilter_groups%5D%5B0%5D%5Bfilters%5D%5B4%5D%5Bfield%5D=region&searchCriteria%5Bfilter_groups%5D%5B0%5D%5Bfilters%5D%5B4%5D%5Bvalue%5D=&searchCriteria%5Bfilter_groups%5D%5B0%5D%5Bfilters%5D%5B4%5D%5Bcondition_type%5D=eq&searchCriteria%5Bfilter_groups%5D%5B0%5D%5Bfilters%5D%5B5%5D%5Bfield%5D=distance&searchCriteria%5Bfilter_groups%5D%5B0%5D%5Bfilters%5D%5B5%5D%5Bvalue%5D=10000&searchCriteria%5Bfilter_groups%5D%5B0%5D%5Bfilters%5D%5B5%5D%5Bcondition_type%5D=eq&searchCriteria%5Bfilter_groups%5D%5B0%5D%5Bfilters%5D%5B6%5D%5Bfield%5D=onlyLocation&searchCriteria%5Bfilter_groups%5D%5B0%5D%5Bfilters%5D%5B6%5D%5Bvalue%5D=0&searchCriteria%5Bfilter_groups%5D%5B0%5D%5Bfilters%5D%5B6%5D%5Bcondition_type%5D=eq&searchCriteria%5Bcurrent_page%5D=1&searchCriteria%5Bpage_size%5D=30&_=1611872083049"
        r = session.get(base_url, headers=_headers())
        locations = r.json()["items"]
        for location in locations:
            page_url = location["website"]
            location_name = location["name"]
            street_address = location["street"]
            city = location["city"]
            state = location["region"]
            zip = location["postal_code"]
            country_code = location["country_id"]
            phone = location["phone"]
            latitude = location["lat"]
            longitude = location["lng"]
            r1 = session.get(page_url, headers=_headers())
            soup1 = bs(r1.text, "lxml")
            hours_block = soup1.find(
                "p", string=re.compile(r"Hours of operation", re.IGNORECASE)
            )
            hours_of_operation = ""
            if hours_block and hours_block.next_sibling.next_sibling:
                hours_of_operation = hours_block.next_sibling.next_sibling.text.replace(
                    "|", ";"
                )

            yield SgRecord(
                page_url=page_url,
                store_number=location["region_id"],
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zip,
                country_code=country_code,
                phone=phone,
                latitude=latitude,
                longitude=longitude,
                locator_domain=locator_domain,
                hours_of_operation=_valid1(hours_of_operation),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
