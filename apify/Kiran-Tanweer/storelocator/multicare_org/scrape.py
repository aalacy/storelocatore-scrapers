from sglogging import sglog
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from bs4 import BeautifulSoup
from sgscrape import sgpostal as parser
import os

os.environ["PROXY_URL"] = "http://groups-BUYPROXIES94952:{}@proxy.apify.com:8000/"
os.environ["PROXY_PASSWORD"] = "apify_proxy_4j1h689adHSx69RtQ9p5ZbfmGA3kw12p0N2q"

session = SgRequests()
website = "multicare_org"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers2 = {"Cookie": "PHPSESSID=ke2qqbtfeur9d308jlm16mdhj6"}

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


headers3 = {
    "authority": "www.multicare.org",
    "method": "GET",
    "scheme": "https",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "accept-encoding": "identity",
    "accept-language": "en-US,en;q=0.9",
    "cache-control": "max-age=0",
    "cookie": "_gcl_au=1.1.977307351.1635524123; _ga_95Z1PX6SEZ=GS1.1.1635524123.1.0.1635524123.0; _tq_id.TV-8154818163-1.389f=cd00533e3cf6dae2.1635524128.0.1635524128..; _ga=GA1.2.1786571781.1635524127; _gid=GA1.2.171897333.1635524128; nmstat=9ad47ff6-3a35-39f3-dc21-204628dd0f71; _hjid=3683150a-eb8b-4dc0-bd42-4278ed4fa480; _hjFirstSeen=1; _mkto_trk=id:512-OWW-241&token:_mch-multicare.org-1635524127906-56452; _fbp=fb.1.1635524128181.2021748016; _hjIncludedInPageviewSample=1; _hjAbsoluteSessionInProgress=1; _hjIncludedInSessionSample=0; www._km_id=85EajWMyPipxe33HdqBkLfsu646e2Za2; www._km_user_name=Suave Eel; www._km_lead_collection=false",
    "if-modified-since": "Thu, 28 Oct 2021 19:09:33 GMT",
    "sec-ch-ua": '"Google Chrome";v="95", "Chromium";v="95", ";Not A Brand";v="99"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "none",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.54 Safari/537.36",
}

DOMAIN = "https://www.multicare.org/"
MISSING = SgRecord.MISSING

location_type = {
    "Emergency Department",
    "Hospital",
    "Laboratory Services",
    "Occupational Medicine",
    "Primary Care Clinic",
    "Urgent Care",
}


def fetch_data():
    if True:
        rawlinks = []
        links = []
        titles = []
        streets = []
        citys = []
        states = []
        pcodes = []
        phones = []
        lats = []
        lngs = []
        storeids = []
        loc_types = []
        hoo = []
        for j in location_type:
            for i in range(1, 11):
                weburl = (
                    "https://www.multicare.org/find-a-location/?query="
                    + j
                    + "&searchloc=&coordinates=&locationType=&sortBy=&radius=1000&page_num="
                    + str(i)
                )
                session = SgRequests()
                r = session.get(weburl, headers=headers)
                soup = BeautifulSoup(r.text, "html.parser")
                locations = soup.findAll("div", {"class": "location-list-card"})
                for loc in locations:
                    title = loc.find("h2", {"class": "title"}).text
                    link = loc.find("h2", {"class": "title"}).find("a")["href"]
                    storeid = loc["data-mcid"]
                    loc_type = loc.find("div", {"class": "note"}).text
                    address = loc.find("div", {"class": "details"}).text
                    address = address.split("\n")[1]
                    coords = loc.find(
                        "div", {"class": "note distance js-distance-calc"}
                    )
                    lat = coords["data-latitude"]
                    lng = coords["data-longitude"]
                    phone = loc.find("a", {"class": "btn btn--solid"})["href"].lstrip(
                        "tel:"
                    )
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

                    if link.find("indigo") != -1:
                        link = link.split("indigo-")[1]
                        link = "https://www.indigourgentcare.com/locations/" + link
                        link = link.rstrip("/")
                    if link.find("indigo") == -1:
                        req = session.get(link, headers=headers3)
                        bs = BeautifulSoup(req.text, "html.parser")
                        hours = bs.find("div", {"class": "hours-content"})
                        if hours is None:
                            hours = "<MISSING>"
                            hoo.append(hours)
                        elif hours.text.strip() == "":
                            hours = "<MISSING>"
                            hoo.append(hours)
                        else:
                            hours = hours.text.strip()
                            hours = hours.replace("\n", " ").strip()
                            hours = hours.replace(
                                "Open 7 days a week", "Mon-Sun"
                            ).strip()
                            hours = hours.lstrip("Hours ").strip()
                            hoo.append(hours)
                    else:
                        try:
                            request = session.get(link, headers=headers2)
                            hours = BeautifulSoup(request.text, "html.parser")
                            hours = hours.findAll(
                                "div", {"class": "col-lg-6 col-md-6 col-xs-12"}
                            )[2]
                            hours = hours.text
                            hours = hours.replace("\n", " ").strip()
                            hours = hours.replace(
                                "Open 7 days a week", "Mon-Sun"
                            ).strip()
                            hours = hours.lstrip("Hours ").strip()
                            hoo.append(hours)
                        except AttributeError:
                            hours = "<MISSING>"
                            hoo.append(hours)
                    hours = hours.replace("By appointment", "<MISSING>")
                    titles.append(title)
                    streets.append(street)
                    citys.append(city)
                    states.append(state)
                    pcodes.append(pcode)
                    lats.append(lat)
                    lngs.append(lng)
                    storeids.append(storeid)
                    loc_types.append(loc_type)
                    rawlinks.append(link)
                    phones.append(phone)
    for url in rawlinks:
        if url.find("indigo") != -1:
            links.append(url)
        else:
            links.append(url)

    for i in range(0, len(titles)):
        yield SgRecord(
            locator_domain=DOMAIN,
            page_url=links[i],
            location_name=titles[i],
            street_address=streets[i].strip(),
            city=citys[i].strip(),
            state=states[i].strip(),
            zip_postal=pcodes[i],
            country_code="US",
            store_number=storeids[i],
            phone=phones[i],
            location_type=loc_types[i],
            latitude=lats[i],
            longitude=lngs[i],
            hours_of_operation=hoo[i].strip(),
        )
        i = i + 1


def scrape():
    log.info("Started")
    count = 0
    deduper = SgRecordDeduper(
        SgRecordID(
            {SgRecord.Headers.STREET_ADDRESS, SgRecord.Headers.HOURS_OF_OPERATION}
        )
    )
    with SgWriter(deduper) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1
    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
