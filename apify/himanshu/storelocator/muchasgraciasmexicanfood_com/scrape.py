from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def fetch_data():

    url = "https://www.muchasgraciasmexicanfood.com/"
    r = session.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")
    divlist = soup.select_one('li:contains("Locations")').findAll("li")
    linklist = []
    for link in divlist:

        link = link.find("a")["href"]

        if len(link.split("locations/", 1)[1].split("/")) == 3:
            pass
        else:
            continue
        linklist.append(link)
    apiurl = "https://www.muchasgraciasmexicanfood.com/wp-admin/admin-ajax.php?action=asl_load_stores&nonce=dfcff1b55e&lang=&load_all=1&layout=1&stores="
    loclist = session.get(apiurl, headers=headers).json()
    for loc in loclist:

        store = loc["id"]
        title = loc["title"]
        street = loc["street"]
        city = loc["city"]
        state = loc["state"]
        pcode = loc["postal_code"]
        lat = loc["lat"]
        longt = loc["lng"]
        phone = loc["phone"]
        link = ""
        hours = (
            loc["open_hours"]
            .replace("'", "")
            .replace("{", "")
            .replace("[", "")
            .replace('"', "")
            .replace("}", "")
            .replace("]", "")
        )
        for slug in linklist:
            if city.lower() in slug:
                link = slug
                break
        if ",sat:1,sun:1" in hours:
            hours = hours.replace(",sat:1,sun:1", ",sat:24 Hours,sun:24 Hours")
        elif "mon:1,tue:1,wed:1,thu:1,fri:1,sat:1,sun:1" in hours:
            hours = "24 Hours"
        elif "sun:0" in hours:
            hours = hours.replace("sun:0", "sun Closed")
        yield SgRecord(
            locator_domain="https://www.muchasgraciasmexicanfood.com/",
            page_url=link,
            location_name=title,
            street_address=street.strip(),
            city=city.strip(),
            state=state.strip(),
            zip_postal=pcode.strip(),
            country_code="US",
            store_number=str(store),
            phone=phone.strip(),
            location_type=SgRecord.MISSING,
            latitude=str(lat),
            longitude=str(longt),
            hours_of_operation=hours,
        )


def scrape():

    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.StoreNumberId)
    ) as writer:

        results = fetch_data()
        for rec in results:
            writer.write_row(rec)


scrape()
