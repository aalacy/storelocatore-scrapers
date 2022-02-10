from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}
days = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]


def format_hours(hours_dict):
    formatted = [
        f'{day}: {hours_dict[day.lower()]["open"]} - {hours_dict[day.lower()]["close"]}'
        for day in days
    ]
    return ", ".join(formatted)


def get_hours_all_closed():
    hours = [f"{day}: Closed" for day in days]
    return ", ".join(hours)


def get_hours(hours, status):
    hours_str = ""

    if status == "unavailable" or len(hours) == 0:
        hours_str = get_hours_all_closed()
    else:
        store_hours = next((item for item in hours if item["type"] == "Standard"), None)
        if store_hours:
            hours_str = f"Restaurant: {format_hours(store_hours)}"

        drive_thru_hours = next(
            (item for item in hours if item["type"] == "Drivethru"), None
        )
        if drive_thru_hours:
            hours_str += ". " if len(hours_str) > 0 else ""
            hours_str += f"Drive Thru: {format_hours(drive_thru_hours)}"

        delivery_hours = next(
            (item for item in hours if item["type"] == "Delivery"), None
        )
        if delivery_hours:
            hours_str += ". " if len(hours_str) > 0 else ""
            hours_str += f"Delivery: {format_hours(delivery_hours)}"

    if not hours_str:
        hours_str = "<MISSING>"

    return hours_str


def fetch_data():
    url = "https://www.kfc.co.uk/cms/api/data/restaurants_all"
    r = session.get(url, headers=headers)
    data = r.json()
    for item in data:
        name = item["name"]
        website = "kfc.co.uk"
        typ = "<MISSING>"
        store = item["storeid"]
        hours = ""
        try:
            street = (
                item["street"].replace("\n", " ").replace("\r", "").replace("\t", "")
            )
        except:
            street = "<MISSING>"
        city = item["city"]
        state = "<MISSING>"
        zc = item["postalcode"]
        lat = item["geolocation"]["latitude"]
        lng = item["geolocation"]["longitude"]
        country = item["countryCode"]
        hours = get_hours(item["hours"], item["status"])
        page_url = f'https://{website}{item["link"]}' if item["link"] else "<MISSING>"
        phone = "<MISSING>"
        if ". Deliver" in hours:
            hours = hours.split(". Deliver")[0].strip()
        if ". Drive" in hours:
            hours = hours.split(". Drive")[0].strip()
        hours = hours.replace("Restaurant:", "").replace("Restaurant :", "").strip()
        if lat == "" or lat is None:
            lat = "<MISSING>"
        if lng == "" or lng is None:
            lng = "<MISSING>"
        if zc == "" or zc is None:
            zc = "<MISSING>"
        if state == "" or state is None:
            state = "<MISSING>"
        if city == "" or city is None:
            city = "<MISSING>"
        city = city.replace('"', "").replace("\r", "").replace("\n", "")
        if city == "<MISSING>":
            city = name.split("-")[0].strip()
        if "Norwich Road" not in name:
            yield SgRecord(
                locator_domain=website,
                page_url=page_url,
                location_name=name,
                street_address=street,
                city=city,
                state=state,
                zip_postal=zc,
                country_code=country,
                phone=phone,
                location_type=typ,
                store_number=store,
                latitude=lat,
                longitude=lng,
                hours_of_operation=hours,
            )


def scrape():
    results = fetch_data()
    with SgWriter(
        deduper=SgRecordDeduper(RecommendedRecordIds.StoreNumberId)
    ) as writer:
        for rec in results:
            writer.write_row(rec)


scrape()
