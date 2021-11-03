from bs4 import BeautifulSoup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests


def fetch_data(sgw: SgWriter):

    session = SgRequests()

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
    headers = {"User-Agent": user_agent}

    locator_domain = "johnstonesupply.com"

    base_links = [
        "https://johnstonesupply.com/rest/js-store/lookupStoreBy?country=us",
        "https://johnstonesupply.com/rest/js-store/lookupStoreBy?country=ca",
        "https://johnstonesupply.com/rest/js-store/lookupStoreBy?state=gu",
    ]
    for base_link in base_links:
        stores = session.get(base_link, headers=headers).json()

        for store in stores:
            store_number = store["storeCode"]
            location_name = store["storeShortName"]
            if not store_number:
                link = ""
                store_number = location_name.split("#")[-1]
                hours_of_operation = "<MISSING>"
            else:
                link = "https://www.johnstonesupply.com/store%s/contact-us" % (
                    store_number
                )
            street_address = store["streetAddress"].strip()
            if "coming soon" in street_address.lower():
                continue
            if street_address == "Inc.":
                street_address = city = ""
            try:
                city = store["city"]
            except:
                city = location_name.split("-")[0].strip()
            try:
                state = store["state"]
            except:
                state = ""
            try:
                zip_code = store["zipCode"]
            except:
                zip_code = ""
            country_code = "US"
            if "=ca" in base_link:
                country_code = "CA"
            location_type = "<MISSING>"
            phone = store["phoneNumber"].split("<")[0].split(" (")[0].strip()
            latitude = "<MISSING>"
            longitude = "<MISSING>"

            if link:
                req = session.get(link, headers=headers)
                base = BeautifulSoup(req.text, "lxml")
                if req.status_code == 404:
                    link = ""
                got_res = False
                hours_of_operation = "<MISSING>"
                results = base.find_all(class_="col-7 col-md-9 col-lg-8")
                if results:
                    for res in results:
                        if "#" in res.p.text:
                            if "#" + store_number in res.p.text:
                                got_res = True
                                break
                        elif (
                            location_name.split("-")[0].strip()
                            in res.p.text.replace("nio - Bro", "nio Bro").strip()
                        ):
                            got_res = True
                            break
                        else:
                            if street_address in res.find(class_="d-block").text:
                                got_res = True
                                break
                    if got_res:
                        try:
                            hours_of_operation = (
                                " ".join(
                                    list(
                                        res.find(class_="text-875rem").stripped_strings
                                    )
                                )
                                .replace("\r\n", " ")
                                .replace("  ", " ")
                                .strip()
                            )
                        except:
                            pass
                else:
                    results = base.find_all(class_="card h-100")
                    if results:
                        for res in results:
                            if "#" in res.find(class_="card-title mb-0").text:
                                if (
                                    store_number
                                    == res.find(class_="card-title mb-0").text.split(
                                        "#"
                                    )[-1]
                                ):
                                    got_res = True
                                    break
                        if got_res:
                            try:
                                hours_of_operation = (
                                    " ".join(
                                        list(
                                            res.find(
                                                class_="text-darkblue"
                                            ).stripped_strings
                                        )
                                    )
                                    .replace("\r\n", " ")
                                    .replace("  ", " ")
                                    .strip()
                                )
                            except:
                                pass
                        try:
                            map_link = res.iframe["src"]
                            lat_pos = map_link.rfind("!3d")
                            latitude = map_link[
                                lat_pos + 3 : map_link.find("!", lat_pos + 5)
                            ].strip()
                            lng_pos = map_link.find("!2d")
                            longitude = map_link[
                                lng_pos + 3 : map_link.find("!", lng_pos + 5)
                            ].strip()
                        except:
                            pass
                hours_of_operation = (
                    hours_of_operation.split("After Hours")[0]
                    .split("24 Hour Emergency")[0]
                    .split("Emergency")[0]
                    .split("(Saturday)")[0]
                    .replace("—", "-")
                    .replace("Hours:", "")
                    .strip()
                )

            sgw.write_row(
                SgRecord(
                    locator_domain=locator_domain,
                    page_url=link,
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


with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
    fetch_data(writer)
