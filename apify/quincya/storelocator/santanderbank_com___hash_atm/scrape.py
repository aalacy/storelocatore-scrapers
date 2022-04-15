import json

from bs4 import BeautifulSoup

from lxml import etree

from sglogging import SgLogSetup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests

logger = SgLogSetup().get_logger("santanderbank_com")

base_url = "https://www.santanderbank.com"


def fetch_data(sgw: SgWriter):

    url = "https://locations.santanderbank.com/"
    session = SgRequests()
    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    request = session.get(url, headers=headers)
    response = etree.HTML(request.text)
    state_list = response.xpath('//a[@class="ga-link"]/@href')
    for state_link in state_list:
        logger.info(state_link)
        response = session.get(state_link, headers=headers).text
        state_response = etree.HTML(response)
        if state_response is not None:
            city_list = state_response.xpath('//a[@class="ga-link capitalize"]/@href')
            for city_link in city_list:
                response = session.get(city_link, headers=headers).text
                city_response = etree.HTML(response)
                store_list = city_response.xpath(
                    '//a[@class="location-name ga-link ft-18"]/@href'
                )
                if len(store_list) > 0:
                    for store_link in store_list:
                        req = session.get(store_link, headers=headers)
                        base = BeautifulSoup(req.text, "lxml")

                        location_name = base.find(class_="location-name").text.strip()

                        script = base.find(
                            "script", attrs={"type": "application/ld+json"}
                        ).contents[0]
                        store = json.loads(script)[0]

                        try:
                            street_address = store["address"]["streetAddress"]
                        except:
                            store = json.loads(script)
                            street_address = store["address"]["streetAddress"]
                        city = store["address"]["addressLocality"]
                        state = store["address"]["addressRegion"]
                        zip_code = store["address"]["postalCode"]
                        country_code = "US"
                        store_number = (
                            base.find(class_="location-type")
                            .text.split(":")[-1]
                            .strip()
                        )
                        location_type = "<MISSING>"
                        phone = store["address"]["telephone"]
                        latitude = store["geo"]["latitude"]
                        longitude = store["geo"]["longitude"]
                        if "branch" in location_name.lower():
                            location_type = "ATM, Branch"
                        elif "atm" in location_name.lower():
                            location_type = "ATM"
                        else:
                            location_type = ""

                        if (
                            "ATM"
                            not in base.find(class_="location-info-wrap").text.upper()
                        ):
                            logger.info("Not ATM..")
                            continue
                        try:
                            hours_of_operation = " ".join(
                                list(base.find(id="atm-hours").stripped_strings)
                            )
                        except:
                            try:
                                hours_of_operation = " ".join(
                                    list(base.find(class_="hours").stripped_strings)
                                )
                            except:
                                hours_of_operation = ""

                        sgw.write_row(
                            SgRecord(
                                locator_domain=base_url,
                                page_url=store_link,
                                location_name=location_name,
                                street_address=street_address,
                                city=city,
                                state=state,
                                zip_postal=zip_code,
                                country_code=country_code,
                                store_number=store_number,
                                phone=phone,
                                location_type=location_type,
                                latitude=latitude,
                                longitude=longitude,
                                hours_of_operation=hours_of_operation,
                            )
                        )


with SgWriter(
    SgRecordDeduper(
        SgRecordID(
            {
                SgRecord.Headers.STREET_ADDRESS,
                SgRecord.Headers.CITY,
                SgRecord.Headers.LOCATION_TYPE,
            }
        )
    )
) as writer:
    fetch_data(writer)
