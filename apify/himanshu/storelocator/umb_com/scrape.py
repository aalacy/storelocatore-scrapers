import json
from bs4 import BeautifulSoup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests

session = SgRequests()


def fetch_data(sgw: SgWriter):
    header = {
        "User-agent": "Mozilla/5.0 (Windows; U; Windows NT 5.1; de; rv:1.9.1.5) Gecko/20091102 Firefox/3.5.5"
    }

    base_url = "https://locations.umb.com/"
    r = session.get(base_url, headers=header)
    soup = BeautifulSoup(r.text, "lxml")
    href = soup.find("div", {"class": "region-map-list"}).find_all(
        "div", {"class": "map-list-item"}
    )
    location_urls = []
    for target_list in href:
        href = target_list.find("a")["href"]
        vr = session.get(href, headers=header)
        soup = BeautifulSoup(vr.text, "lxml")
        vk = (
            soup.find("div", {"class": "col-maplist"})
            .find("div", {"class": "map-list-wrap"})
            .find("ul", {"class": "map-list"})
            .find_all("li", {"class": "map-list-item-wrap"})
        )
        for target_list in vk:
            link = target_list.find("a", {"class": "ga-link"})["href"]
            vr = session.get(link, headers=header)
            soup = BeautifulSoup(vr.text, "lxml")
            for location in soup.find("div", {"class": "map-list-tall"}).find_all(
                "span", {"class": "location-name"}
            ):
                location_url = location.parent["href"]
                if location_url in location_urls:
                    continue
                location_urls.append(location_url)
                location_request = session.get(location_url, headers=header)
                soup = BeautifulSoup(location_request.text, "lxml")

                locator_domain = "https://www.umb.com/"
                location_name = location.text.strip()
                fb = soup.find("div", {"class": "address"}).find_all("div")
                street_address = " ".join(list(fb[0].stripped_strings))
                temp = " ".join(list(fb[1].stripped_strings)).split(",")
                city = temp[0]
                state = temp[1].strip().split(" ")[0]
                zip = temp[1].strip().split(" ")[1]
                store_number = "<MISSING>"
                phone = soup.find("a", {"class": "phone"}).text
                country_code = "US"
                location_type = "<MISSING>"
                geo_location = json.loads(
                    soup.find(id="map-data-wrapper")
                    .find("script")
                    .contents[0]
                    .split("defaultData = ")[1]
                    .split("};")[0]
                    + "}"
                )["markerData"][0]
                latitude = geo_location["lat"]
                longitude = geo_location["lng"]
                if soup.find("div", {"class": "hours-col"}):
                    hours_soup = soup.find("div", {"class": "hours-col"})
                    [s.extract() for s in hours_soup("script")]
                    hours_of_operation = " ".join(list(hours_soup.stripped_strings))
                else:
                    hours_of_operation = "<MISSING>"
                hours_of_operation = hours_of_operation.split("Drive")[0].strip()

                sgw.write_row(
                    SgRecord(
                        locator_domain=locator_domain,
                        page_url=location_url,
                        location_name=location_name,
                        street_address=street_address,
                        city=city,
                        state=state,
                        zip_postal=zip,
                        country_code=country_code,
                        store_number=store_number,
                        phone=phone,
                        location_type=location_type,
                        latitude=latitude,
                        longitude=longitude,
                        hours_of_operation=hours_of_operation,
                    )
                )


with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
    fetch_data(writer)
