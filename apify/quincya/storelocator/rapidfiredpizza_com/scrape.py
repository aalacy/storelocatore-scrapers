from bs4 import BeautifulSoup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests


def fetch_data(sgw: SgWriter):

    base_link = "https://rapidfiredpizza.com/location-data/getlocations.php"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
    headers = {"User-Agent": user_agent}

    HEADERS = {
        "authority": "rapidfiredpizza.com",
        "method": "GET",
        "path": "/location-data/getlocations.php",
        "scheme": "https",
        "accept": "text/plain, */*; q=0.01",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "en-US,en;q=0.9",
        "content-length": "15",
        "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
        "cookie": "_ga=GA1.2.697583639.1605159901; _fbp=fb.1.1605159901008.840266221; _gid=GA1.2.1263464095.1605858583",
        "origin": "https://rapidfiredpizza.com",
        "referer": "https://rapidfiredpizza.com/locations",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36",
        "x-requested-with": "XMLHttpRequest",
    }

    session = SgRequests()

    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    items = base.find_all(class_="location-details location-small col-sm-4")
    locator_domain = "rapidfiredpizza.com"

    for item in items:
        if "coming soon" in str(item).lower():
            continue
        link = item.a["href"]
        location_name = item.a.text.strip()

        raw_address = list(item.p.find_all("a")[1].stripped_strings)
        street_address = " ".join(raw_address[:-1]).strip()
        city_line = raw_address[-1].strip().split(",")
        city = city_line[0].strip()
        state = city_line[-1].strip().split()[0].strip()
        zip_code = city_line[-1].strip().split()[1].strip()
        country_code = "US"
        location_type = "<MISSING>"
        phone = item.p.a.text.strip()

        req = session.get(link, headers=headers)
        base = BeautifulSoup(req.text, "lxml")

        store_number = base.find(id="landhere").div["id"].split("store")[1]
        payload = {"id": "store" + store_number}

        post_link = (
            "https://rapidfiredpizza.com/location-data/locations-landing/landing.php"
        )
        req = session.post(post_link, headers=HEADERS, data=payload)
        base = BeautifulSoup(req.text, "lxml")

        try:
            days = list(base.find(class_="col-md-3 col-xs-4").stripped_strings)
            hours = list(base.find(class_="col-md-9 col-xs-7").stripped_strings)

            hours_of_operation = " "
            for i, day in enumerate(days):
                hours_of_operation = (
                    hours_of_operation + " " + day + " " + hours[i]
                ).strip()
        except:
            hours_of_operation = ""

        try:
            map_link = base.find_all("iframe")[-1]["src"]
            lat_pos = map_link.rfind("!3d")
            latitude = map_link[lat_pos + 3 : map_link.find("!", lat_pos + 5)].strip()
            lng_pos = map_link.find("!2d")
            longitude = map_link[lng_pos + 3 : map_link.find("!", lng_pos + 5)].strip()
        except:
            latitude = "<MISSING>"
            longitude = "<MISSING>"

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
