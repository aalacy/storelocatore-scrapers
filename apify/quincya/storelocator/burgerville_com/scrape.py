from sgrequests import SgRequests

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()

    locator_domain = "burgerville.com"

    base_link = "https://liveapi.yext.com/v2/accounts/me/entities/geosearch?radius=50&location=Vancouver,%20WA&limit=50&api_key=4e2607cc584571532d64e96cde56412e&v=20181201&resolvePlaceholders=true&entityTypes=location"
    stores = session.get(base_link, headers=headers).json()["response"]["entities"]

    for store in stores:
        try:
            location_name = store["geomodifier"].replace("\xa0", " ")
        except:
            location_name = store["name"].replace("\xa0", " ")
        if "- CLOSED" in location_name.upper():
            continue
        street_address = store["address"]["line1"]
        city = store["address"]["city"]
        state = store["address"]["region"]
        zip_code = store["address"]["postalCode"]
        country_code = store["address"]["countryCode"]
        store_number = store["meta"]["id"]
        if "-" in store_number or len(store_number) > 5:
            store_number = ""
        try:
            phone = store["mainPhone"]
        except:
            phone = ""
        location_type = ""
        try:
            raw_hours = store["hours"]
            hours_of_operation = ""
            for raw_hour in raw_hours:
                try:
                    end = raw_hours[raw_hour]["openIntervals"][0]["end"]
                    start = raw_hours[raw_hour]["openIntervals"][0]["start"]
                    hours_of_operation = (
                        hours_of_operation + " " + raw_hour + " " + start + "-" + end
                    ).strip()
                except:
                    hours_of_operation = (
                        hours_of_operation + " " + raw_hour + " Closed"
                    ).strip()
        except:
            hours_of_operation = "<MISSING>"

        try:
            geo = store["geocodedCoordinate"]
        except:
            geo = store["yextDisplayCoordinate"]
        latitude = geo["latitude"]
        longitude = geo["longitude"]
        link = store["landingPageUrl"]

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


with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
    fetch_data(writer)
