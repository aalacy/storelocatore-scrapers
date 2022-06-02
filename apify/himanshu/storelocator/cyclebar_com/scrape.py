import json

from bs4 import BeautifulSoup
from datetime import datetime

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests

session = SgRequests()


def fetch_data(sgw: SgWriter):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36",
    }

    base_url = "https://members.cyclebar.com/api/brands/cyclebar/locations?open_status=external&geoip="
    locator_domain = "https://www.cyclebar.com/"
    r_locations = session.get(base_url, headers=headers).json()
    json_data = r_locations["locations"]
    for location in json_data:
        coming_soon = location["coming_soon"]
        if str(coming_soon) == "True":
            pass
        else:
            location_name = location["name"]
            address2 = location["address2"]
            street_address = (
                location["address"] + " " + str(address2).replace("None", "")
            )
            city = location["city"]
            state = location["state"]
            zipp = location["zip"]
            country_code = location["country_code"]
            phone = location["phone"]
            latitude = location["lat"]
            longitude = location["lng"]
            location_url = location["site_url"]
            store_number = location["seq"]
            location_type = ""
            hours_of_operation = ""
            if location_url:
                location_url = location_url.replace("unversity", "university")
                r = session.get(location_url, headers=headers)
                soup = BeautifulSoup(r.text, "lxml")
                hours = soup.find("span", {"class": "location-info-map__info"})
                if hours:
                    try:
                        hours1 = hours["data-hours"]
                        json_data1 = json.loads(hours1)
                        hours_of_operation = ""
                        for data in json_data1:

                            if len(json_data1[data]) == 1:
                                hours_of = (
                                    data,
                                    json_data1[data][0][0],
                                    json_data1[data][0][1],
                                )
                                d = datetime.strptime(hours_of[1], "%H:%M")
                                t = d.strftime("%I:%M %p")
                                d1 = datetime.strptime(hours_of[2], "%H:%M")
                                t1 = d1.strftime("%I:%M %p")
                                hours_of_operation = (
                                    hours_of_operation
                                    + " "
                                    + hours_of[0]
                                    + " "
                                    + t
                                    + " "
                                    + t1
                                )
                            else:
                                hours_of_1 = (
                                    data,
                                    json_data1[data][0][0],
                                    json_data1[data][0][1],
                                    json_data1[data][1][0],
                                    json_data1[data][1][1],
                                )
                                d2 = datetime.strptime(hours_of_1[1], "%H:%M")
                                t2 = d2.strftime("%I:%M %p")
                                d3 = datetime.strptime(hours_of_1[2], "%H:%M")
                                t3 = d3.strftime("%I:%M %p")
                                d4 = datetime.strptime(hours_of_1[3], "%H:%M")
                                t4 = d4.strftime("%I:%M %p")
                                d5 = datetime.strptime(hours_of_1[4], "%H:%M")
                                t5 = d5.strftime("%I:%M %p")
                                hours_of_operation = (
                                    hours_of_operation
                                    + " "
                                    + hours_of_1[0]
                                    + " "
                                    + t2
                                    + " "
                                    + t3
                                    + " "
                                    + t4
                                    + " "
                                    + t5
                                )
                    except:
                        hours_of_operation = "<MISSING>"
            else:
                location_url = "https://www.cyclebar.com/location-search"
                hours_of_operation = "<MISSING>"

            sgw.write_row(
                SgRecord(
                    locator_domain=locator_domain,
                    page_url=location_url,
                    location_name=location_name,
                    street_address=street_address,
                    city=city,
                    state=state,
                    zip_postal=zipp,
                    country_code=country_code,
                    store_number=store_number,
                    phone=phone,
                    location_type=location_type,
                    latitude=latitude,
                    longitude=longitude,
                    hours_of_operation=hours_of_operation,
                )
            )


with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
    fetch_data(writer)
