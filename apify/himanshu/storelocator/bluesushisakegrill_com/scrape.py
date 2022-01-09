from bs4 import BeautifulSoup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests

session = SgRequests()


def fetch_data(sgw: SgWriter):
    domain = "https://bluesushisakegrill.com"
    get_url = "https://bluesushisakegrill.com/locations"
    r = session.get(get_url)
    soup = BeautifulSoup(r.text, "html.parser")
    main = soup.find_all("h3", {"class": "locations-item-title"})
    for i in main:
        title = i.find("a").text
        link = i.find("a")["href"]
        r1 = session.get(link)
        soup1 = BeautifulSoup(r1.text, "html.parser")
        if "coming soon" in soup1.h1.text.lower():
            continue
        main1 = soup1.find("div", {"class": "location_details-address"})
        data = list(main1.stripped_strings)
        address = data[2]
        street = address
        locality = data[-1]
        locality = locality.split(",")
        city = locality[0].strip()
        locality = locality[1].strip()
        locality = locality.split(" ")
        if len(locality) == 2:
            pcode = locality[1]
            state = locality[0]
        else:
            state = locality[0]
            pcode = "<MISSING>"
        phone = soup1.find("p", {"class": "location_details-phone"}).text.strip()
        hour_tmp = soup1.find("div", {"class": "location_details-hours"})
        hour = " ".join(list(hour_tmp.stripped_strings))
        cords = soup1.find(
            "a",
            {
                "class": "location_details-address-directions button button--primary button--solid"
            },
        )["href"].split("@")
        if len(cords) == 2:

            lat = (
                soup1.find(
                    "a",
                    {
                        "class": "location_details-address-directions button button--primary button--solid"
                    },
                )["href"]
                .split("@")[1]
                .split(",")[0]
            )
            lng = (
                soup1.find(
                    "a",
                    {
                        "class": "location_details-address-directions button button--primary button--solid"
                    },
                )["href"]
                .split("@")[1]
                .split(",")[1]
            )
        elif len(cords) == 1:
            lat = (
                soup1.find(
                    "a",
                    {
                        "class": "location_details-address-directions button button--primary button--solid"
                    },
                )["href"]
                .split("=")[-1]
                .split("+")[0]
            )
            lng = (
                soup1.find(
                    "a",
                    {
                        "class": "location_details-address-directions button button--primary button--solid"
                    },
                )["href"]
                .split("=")[-1]
                .split("+")[1]
            )
        if phone == "":
            phone = "<MISSING>"
        hour = hour.rstrip(":").replace("NOW OPEN!", "").strip()

        store_number = ""
        location_type = ""

        store = list()
        store.append(link)
        store.append(title)
        store.append(street)
        store.append(city)
        store.append(state)
        store.append(pcode)
        store.append("US")
        store.append("<MISSING>")
        store.append(phone)
        store.append("<MISSING>")
        store.append(lat)
        store.append(lng)
        store.append(hour)

        sgw.write_row(
            SgRecord(
                locator_domain=domain,
                page_url=link,
                location_name=title,
                street_address=street,
                city=city,
                state=state,
                zip_postal=pcode,
                country_code="US",
                store_number=store_number,
                phone=phone,
                location_type=location_type,
                latitude=lat,
                longitude=lng,
                hours_of_operation=hour,
            )
        )


with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
    fetch_data(writer)
