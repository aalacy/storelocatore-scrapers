from bs4 import BeautifulSoup

from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
headers = {"User-Agent": user_agent}


def fetch_data(sgw: SgWriter):
    url = "https://www.corkyskitchenandbakery.com/locations"

    headers = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36",
        "upgrade-insecure-requests": "1",
    }

    session = SgRequests()

    req = session.get(url, headers=headers)
    base = BeautifulSoup(req.text, "lxml")
    website = "corkyskitchenandbakery.com"
    typ = "<MISSING>"
    country = "US"
    store = "<MISSING>"
    hours = "<MISSING>"
    text = str(base).replace("\r", "").replace("\n", "").replace("\t", "")
    if '"@type":"Restaurant","' in text:
        items = text.split('"@type":"Restaurant","')
        links = text.split('"url":')
        for item in items:
            lat = "<MISSING>"
            lng = "<MISSING>"
            if '"streetAddress":"' in item:
                add = item.split('"streetAddress":"')[1].split('"')[0]
                if "19250 Bear" in add and "19250 Bear" in str(
                    base.find(id="popmenu-apollo-state")
                ):
                    lat = "34.471352"
                    lng = "-117.243407"
                try:
                    phone = item.split('"telephone":"')[1].split('"')[0]
                except:
                    phone = "<MISSING>"
                try:
                    city = item.split('"addressLocality":"')[1].split('"')[0]
                except:
                    city = "<MISSING>"
                try:
                    state = item.split('"addressRegion":"')[1].split('"')[0]
                except:
                    state = "<MISSING>"
                try:
                    hours = (
                        item.split('"openingHours":["')[1]
                        .split("]")[0]
                        .replace('","', "; ")
                        .replace('"', "")
                    )
                except:
                    hours = "<MISSING>"
                try:
                    zc = item.split('"postalCode":"')[1].split('"')[0]
                except:
                    zc = "<MISSING>"
                if "0" not in hours:
                    hours = "<MISSING>"
                name = city
                if "0000" in phone:
                    phone = "<MISSING>"

                for link in links:
                    url = (
                        "https://www.corkyskitchenandbakery.com/"
                        + link.split("/")[1].split('"')[0]
                    )
                    try:
                        if (
                            url.split("/")[-1].split("-")[1]
                            in name.replace(" ", "").lower()
                        ):
                            break
                    except:
                        continue

                store = url.split("/")[-1].split("-")[0]

                if city != "<MISSING>":
                    sgw.write_row(
                        SgRecord(
                            locator_domain=website,
                            page_url=url,
                            location_name=name,
                            street_address=add,
                            city=city,
                            state=state,
                            zip_postal=zc,
                            country_code=country,
                            store_number=store,
                            phone=phone,
                            location_type=typ,
                            latitude=lat,
                            longitude=lng,
                            hours_of_operation=hours,
                        )
                    )


with SgWriter(SgRecordDeduper(RecommendedRecordIds.PhoneNumberId)) as writer:
    fetch_data(writer)
