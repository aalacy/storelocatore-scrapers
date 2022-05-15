from sglogging import sglog
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from bs4 import BeautifulSoup
from sgscrape import sgpostal as parser
import re


session = SgRequests()
website = "multicare_org"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()

headers = {
    "authority": "www.multicare.org",
    "method": "GET",
    "scheme": "https",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "accept-encoding": "identity",
    "accept-language": "en-US,en;q=0.9",
    "cookie": "_gcl_au=1.1.327728800.1633174484; nmstat=bdec21ab-2e1d-e199-071c-6de386320ce3; _hjid=8a276a42-9809-4add-a9c9-dc91bd9adff4; _fbp=fb.1.1633174488955.1897730601; _mkto_trk=id:512-OWW-241&token:_mch-multicare.org-1633174488998-42476; _gid=GA1.2.2038359169.1633536584; www._km_id=tNbyFVLn9cuZFnVgKDmS0RVuQvYrQjDO; www._km_user_name=Zealous Orca; www._km_lead_collection=false; _ga_95Z1PX6SEZ=GS1.1.1633615387.13.1.1633615391.0; _ga=GA1.2.1660038917.1633174485; _gat_UA-4300991-1=1; _tq_id.TV-8154818163-1.389f=69205b1954d4f79c.1633174488.0.1633615405..; _hjIncludedInPageviewSample=1; _hjAbsoluteSessionInProgress=1; _hjIncludedInSessionSample=0",
    "referer": "https://www.multicare.org/find-a-location/?query=&searchloc=&coordinates=&locationType=15&sortBy=&radius=30",
    "sec-ch-ua": '"Chromium";v="94", "Google Chrome";v="94", ";Not A Brand";v="99"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "same-origin",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.71 Safari/537.36",
}

DOMAIN = "https://www.multicare.org/"
MISSING = SgRecord.MISSING


def fetch_data():
    urls = []
    for num in range(1, 4):
        url1 = (
            "https://www.multicare.org/find-a-location/?queryl=&locationType=15&sortBy=alphabetical&page_num="
            + str(num)
        )
        urls.append(url1)
        url2 = (
            "https://www.multicare.org/find-a-location/?locationType=23&sortBy=alphabetical&page_num="
            + str(num)
        )
        urls.append(url2)
    for num in range(1, 5):
        url = (
            "https://www.multicare.org/find-a-location/?locationType=27&sortBy=alphabetical&page_num="
            + str(num)
        )
        urls.append(url)
    for num in range(1, 9):
        url = (
            "https://www.multicare.org/find-a-location/?locationType=13&sortBy=alphabetical&page_num="
            + str(num)
        )
        urls.append(url)
    for num in range(1, 62):
        url = (
            "https://www.multicare.org/find-a-location/?query=multicare&page_num="
            + str(num)
        )
        urls.append(url)
    for url in urls:
        r = session.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        loc_card = soup.findAll("div", {"class": "location-list-card__content"})
        for loc in loc_card:
            title = loc.find("h2", {"class": "title"}).find("a").text
            store_url = loc.find("h2", {"class": "title"}).find("a")["href"]
            store_type = loc.find("div", {"class": "note"}).find("b").text
            address = loc.find("div", {"class": "details"}).find("a").text
            coords = loc.find("div", {"class": "details"}).find("div")
            lat = coords["data-latitude"]
            lng = coords["data-longitude"]
            try:
                phone = loc.find("div", {"class": "contact"}).find("a").text
            except AttributeError:
                phone = MISSING
            try:
                req = session.get(store_url, headers=headers)
                bs = BeautifulSoup(req.text, "html.parser")
            except AttributeError:
                hours = MISSING
            try:
                hours = bs.find("div", {"class": "hours-content"}).text
                hours = hours.strip()
                if hours == "":
                    hours = MISSING
            except AttributeError:
                hours = "Open 24 hours"
            if hours.find("1/3/22:") != -1:
                hours = "Temporarily Closed"
            if hours.find("appointment") != -1:
                hours = MISSING
            if hours.find("Call") != -1:
                hours = MISSING
            address = address.replace(",", "")
            address = address.strip()
            parsed = parser.parse_address_usa(address)
            street1 = (
                parsed.street_address_1 if parsed.street_address_1 else "<MISSING>"
            )
            street = (
                (street1 + ", " + parsed.street_address_2)
                if parsed.street_address_2
                else street1
            )
            city = parsed.city if parsed.city else "<MISSING>"
            state = parsed.state if parsed.state else "<MISSING>"
            pcode = parsed.postcode if parsed.postcode else "<MISSING>"

            yield SgRecord(
                locator_domain=DOMAIN,
                page_url=store_url,
                location_name=title,
                street_address=street,
                city=city,
                state=state,
                zip_postal=pcode,
                country_code="US",
                store_number=MISSING,
                phone=phone,
                location_type=store_type,
                latitude=lat,
                longitude=lng,
                hours_of_operation=hours.strip(),
                raw_address=address,
            )

    pulse = []
    indigo = []
    url = "https://www.multicare.org/find-a-location/rockwood-clinic/locations/"
    r = session.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")
    locations = soup.findAll("div", {"class": "link-list-box__content"})
    for locs in locations:
        ref = locs.findAll("a")
        for loc in ref:
            store_url = loc["href"]
            title = loc.text.strip()
            if title != "":
                if store_url.find("pulse") != -1:
                    pulse.append("store_url")
                elif store_url.find("indigo") != -1:
                    indigo.append("store_url")
                else:
                    try:
                        r = session.get(store_url, headers=headers)
                        soup = BeautifulSoup(r.text, "html.parser")
                    except AttributeError:
                        store_type = MISSING
                        address = MISSING
                        lat = MISSING
                        lng = MISSING
                        phone = MISSING
                        hours = MISSING
                    try:
                        store_type = soup.find("div", {"class": "note"}).find("b").text
                        address = soup.find("div", {"class": "address"}).find("a").text
                        coords = soup.find("div", {"class": "address"}).find("div")
                        lat = coords["data-latitude"]
                        lng = coords["data-longitude"]
                        phone = soup.find(
                            "div", {"class": "contact flex-row"}
                        ).text.strip()
                        phone = phone.split("\n")[0].split("Phone: ")[1].strip()
                        hours = soup.find("div", {"class": "hours-content"}).text
                        hours = hours.replace("\n", " ").strip()
                    except AttributeError:
                        try:
                            store_type = soup.find(
                                "div", {"class": "details-box__title"}
                            ).text.strip()
                        except AttributeError:
                            if (
                                store_url
                                == "https://www.multicare.org/provider/lora-jasman/"
                            ):
                                address = (
                                    soup.find("div", {"class": "location"})
                                    .find("a")
                                    .text
                                )
                                phone = soup.find("h3", {"class": "phone"}).text.strip()
                            else:
                                store_type = MISSING
                                address = MISSING
                                lat = MISSING
                                lng = MISSING
                                phone = MISSING
                                hours = MISSING
                    if (
                        store_url
                        == "https://www.multicare.org/location/multicare-rockwood-main-clinic/"
                    ):
                        store_type = "Clinic"
                    address = address.replace(",", "")
                    address = address.strip()
                    parsed = parser.parse_address_usa(address)
                    street1 = (
                        parsed.street_address_1
                        if parsed.street_address_1
                        else "<MISSING>"
                    )
                    street = (
                        (street1 + ", " + parsed.street_address_2)
                        if parsed.street_address_2
                        else street1
                    )
                    city = parsed.city if parsed.city else "<MISSING>"
                    state = parsed.state if parsed.state else "<MISSING>"
                    pcode = parsed.postcode if parsed.postcode else "<MISSING>"

                    yield SgRecord(
                        locator_domain=DOMAIN,
                        page_url=store_url,
                        location_name=title,
                        street_address=street,
                        city=city,
                        state=state,
                        zip_postal=pcode,
                        country_code="US",
                        store_number=MISSING,
                        phone=phone,
                        location_type=store_type,
                        latitude=lat,
                        longitude=lng,
                        hours_of_operation=hours.strip(),
                        raw_address=address,
                    )

    url = "https://www.pulseheartinstitute.org/locations/"
    r = session.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")
    main = soup.findAll("section", {"class": "container mx1800"})[0].findAll(
        "div", {"class": "flex-row"}
    )
    for loc in main:
        store_url = (
            "https://www.pulseheartinstitute.org"
            + loc.find("div", {"class": "col-side"}).find("a")["href"]
        )
        address = loc.find("div", {"class": "address"}).text.strip()
        title = loc.find("h2", {"class": "name"}).text.strip()
        phone = loc.find("div", {"class": "phone"}).find("a").text.strip()
        address = address.split("\n")[0].strip()
        hours = MISSING
        lat = MISSING
        lng = MISSING
        store_type = "Clinic"
        address = address.replace(",", "")
        address = address.strip()
        parsed = parser.parse_address_usa(address)
        street1 = parsed.street_address_1 if parsed.street_address_1 else "<MISSING>"
        street = (
            (street1 + ", " + parsed.street_address_2)
            if parsed.street_address_2
            else street1
        )
        city = parsed.city if parsed.city else "<MISSING>"
        state = parsed.state if parsed.state else "<MISSING>"
        pcode = parsed.postcode if parsed.postcode else "<MISSING>"

        yield SgRecord(
            locator_domain=DOMAIN,
            page_url=store_url,
            location_name=title,
            street_address=street,
            city=city,
            state=state,
            zip_postal=pcode,
            country_code="US",
            store_number=MISSING,
            phone=phone,
            location_type=store_type,
            latitude=lat,
            longitude=lng,
            hours_of_operation=hours.strip(),
            raw_address=address,
        )

    pattern = re.compile(r"\s\s+")
    cleanr = re.compile(r"<[^>]+>")
    url = "https://www.marybridge.org/locations/"
    r = session.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")
    locs = soup.findAll("a", {"class": "caret orange btn shadow"})
    for loc in locs:
        store_url = "https://www.marybridge.org" + loc["href"]
        req = session.get(store_url, headers=headers)
        bs = BeautifulSoup(req.text, "html.parser")
        title = bs.find("h1", {"class": "loc-main-title"}).text
        details = bs.find("div", {"class": "loc-details"}).text.strip()
        details = re.sub(pattern, "", details)
        details = re.sub(cleanr, "", details)
        details = details.replace("Contact", "")
        details = details.replace("Address", "")
        details = details.replace("Hours", "")
        details = details.replace("Get Directions", "")
        details = details.replace('"Specialty services vary by days of the week', "")
        details = details.replace("Parking Information", "")
        details = details.replace(
            "Appointments are scheduled through Mary Bridge Children's.", ""
        )
        details = details.replace("By appointment", "")
        details = details.replace(", by appointment", "")
        details = details.replace("Hours", "")
        details = details.replace("Hours", "")
        details = details.strip()
        lat = MISSING
        lng = MISSING
        store_type = "Clinic"
        details = details.split("\n")
        while "" in details:
            details.remove("")
        if len(details) == 2:
            address = details[0].strip()
            phone = details[1].strip()
            if phone.find("only") != -1:
                phone = address.split("P.")[1].strip()
        if len(details) == 3:
            address = details[0].strip()
            phone = details[1].strip()
            hours = details[2].strip()
            if hours.find("only") != -1:
                hours = MISSING
        if len(details) == 4:
            address = details[0].strip()
            phone = details[1].strip()
            hours = details[2].strip()
            if hours.find("open 24/7") != -1:
                hours = "Mon-Sun 24-hours"
            phone = phone.rstrip("Specialty clinics vary by days of the week.")
        if len(details) == 5:
            address = details[0].strip()
            phone = details[1].strip()
            hours = details[2] + " " + details[3] + " " + details[4]
        if len(details) == 7:
            address = details[0].strip()
            phone = details[1].strip()
            hours = details[2] + " " + details[3]
            hours = hours.split("Our")[0]
        phone = phone.split("F")[0].strip()
        phone = phone.replace("P. ", "").strip()
        phone = phone.replace("(Specialties)", "").strip()
        hours = hours.replace(
            ".  Specialties or Therapy Services (253-697-5200) to schedule.Reserve appointment for Urgent Care online.",
            "<MISSING>",
        )
        hours = hours.replace("Specialty services vary by days of the week, ", "")
        hours = hours.replace(
            "Varies by each specialty service and by appointment.Facility open ", ""
        )
        hours = hours.replace("Suite 200 - Specialty clinics, Lab & X-ray: ", "")
        hours = hours.replace(
            "Pediatric Specialty Care vary by days of the week. Appointments scheduled through Mary Bridge Children's.",
            "<MISSING>",
        )

        address = address.replace(",", "")
        address = address.strip()
        parsed = parser.parse_address_usa(address)
        street1 = parsed.street_address_1 if parsed.street_address_1 else "<MISSING>"
        street = (
            (street1 + ", " + parsed.street_address_2)
            if parsed.street_address_2
            else street1
        )
        city = parsed.city if parsed.city else "<MISSING>"
        state = parsed.state if parsed.state else "<MISSING>"
        pcode = parsed.postcode if parsed.postcode else "<MISSING>"

        yield SgRecord(
            locator_domain=DOMAIN,
            page_url=store_url,
            location_name=title,
            street_address=street,
            city=city,
            state=state,
            zip_postal=pcode,
            country_code="US",
            store_number=MISSING,
            phone=phone,
            location_type=store_type,
            latitude=lat,
            longitude=lng,
            hours_of_operation=hours.strip(),
            raw_address=address,
        )

    url = "https://www.multicare.org/find-a-location/womens-specialty-care-locations/"
    r = session.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")
    locs = soup.findAll("div", {"class": "rtecontent"})[1].findAll("a")
    for loc in locs:
        store_url = loc["href"]
        if store_url.find("/location/") != -1:
            title = loc.text.strip()
            r = session.get(store_url, headers=headers)
            soup = BeautifulSoup(r.text, "html.parser")
            try:
                store_type = soup.find("div", {"class": "note"}).text
            except AttributeError:
                store_type = MISSING
                address = MISSING
                lat = MISSING
                lng = MISSING
                phone = MISSING
                hours = MISSING
                city = MISSING
                state = MISSING
                street = MISSING
                pcode = MISSING
                continue
            address = soup.find("div", {"class": "address"}).find("a").text
            coords = soup.find("div", {"class": "address"}).find("div")
            lat = coords["data-latitude"]
            lng = coords["data-longitude"]
            phone = soup.find("div", {"class": "contact flex-row"}).text.strip()
            phone = phone.split("\n")[0].split("Phone: ")[1].strip()
            hours = soup.find("div", {"class": "hours-content"}).text
            hours = hours.replace("\n", " ").strip()

            address = address.replace(",", "")
            address = address.strip()
            parsed = parser.parse_address_usa(address)
            street1 = (
                parsed.street_address_1 if parsed.street_address_1 else "<MISSING>"
            )
            street = (
                (street1 + ", " + parsed.street_address_2)
                if parsed.street_address_2
                else street1
            )
            city = parsed.city if parsed.city else "<MISSING>"
            state = parsed.state if parsed.state else "<MISSING>"
            pcode = parsed.postcode if parsed.postcode else "<MISSING>"

            yield SgRecord(
                locator_domain=DOMAIN,
                page_url=store_url,
                location_name=title,
                street_address=street,
                city=city,
                state=state,
                zip_postal=pcode,
                country_code="US",
                store_number=MISSING,
                phone=phone,
                location_type=store_type,
                latitude=lat,
                longitude=lng,
                hours_of_operation=hours.strip(),
                raw_address=address,
            )


def scrape():
    log.info("Started")
    count = 0
    deduper = SgRecordDeduper(SgRecordID({SgRecord.Headers.LOCATION_NAME}))
    with SgWriter(deduper) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1
    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
