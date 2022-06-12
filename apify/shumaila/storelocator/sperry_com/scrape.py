from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def settime(timenow, flag):
    endt = "00"
    if timenow == "0":
        return " Closed"
    if len(timenow) == 3:
        st = (int)(timenow[0:1])
        endt = timenow[1:3]
    elif len(timenow) == 4:
        st = (int)(timenow[0:2])
        endt = timenow[2:4]
    if st > 12:
        st = st - 12
    zone = " AM - "
    if flag == 2:
        zone = " PM "
    return str(st) + ":" + endt + zone


def fetch_data():

    titlelist = []
    weeklist = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]

    urllist = [
        "https://sperry.locally.com/stores/conversion_data?has_data=true&company_id=1566&store_mode=&style=&color=&upc=&category=&inline=1&show_links_in_list=&parent_domain=&map_center_lat=39.75307668395031&map_center_lng=-105.27049999999929&map_distance_diag=2901.674064426807&sort_by=proximity&no_variants=0&only_retailer_id=&dealers_company_id=&only_store_id=false&uses_alt_coords=false&q=boulder&zoom_level=4&forced_coords=1",
        "https://sperry.locally.com/stores/conversion_data?has_data=true&company_id=1566&store_mode=&style=&color=&upc=&category=&inline=1&show_links_in_list=&parent_domain=&map_center_lat=21.255013345566596&map_center_lng=-157.7963900000007&map_distance_diag=1027.55394920827&sort_by=proximity&no_variants=0&only_retailer_id=&dealers_company_id=&only_store_id=false&uses_alt_coords=false&q=+HI+96753&zoom_level=6&forced_coords=1",
    ]
    for url in urllist:
        loclist = session.get(url, headers=headers)
        loclist = loclist.json()["markers"]

        for loc in loclist:

            store = loc["id"]
            title = loc["name"]
            city = loc["city"]
            state = loc["state"]
            street = loc["address"]
            lat = loc["lat"]
            longt = loc["lng"]
            phone = loc["phone"]
            ccode = loc["country"]
            pcode = loc["zip"]
            if store in titlelist:
                continue
            titlelist.append(store)
            if "Sperry" in title:
                ltype = "Store"
            else:
                ltype = "Dealer"
            link = "https://sperry.locally.com/store/" + str(store)
            hours = ""
            try:
                for day in weeklist:

                    start = settime(str(loc[day + "_time_open"]), 1)
                    if "Closed" in start:
                        end = " "
                    else:
                        end = settime(str(loc[day + "_time_close"]), 2)
                    hours = hours + day + " " + start + end
            except:
                hours = "<MISSING>"
            if len(phone) < 3:
                phone = "<MISSING>"
            if "mon  Closed" in hours and "tue  Closed" in hours:
                hours = "Mon-Sun Closed"
            yield SgRecord(
                locator_domain="https://www.sperry.com/",
                page_url=link,
                location_name=title.encode("ascii", "ignore").decode("ascii").strip(),
                street_address=street.encode("ascii", "ignore").decode("ascii").strip(),
                city=city.encode("ascii", "ignore").decode("ascii").strip(),
                state=state.encode("ascii", "ignore").decode("ascii").strip(),
                zip_postal=pcode,
                country_code=ccode.encode("ascii", "ignore").decode("ascii").strip(),
                store_number=str(store),
                phone=phone.encode("ascii", "ignore").decode("ascii").strip(),
                location_type=ltype.encode("ascii", "ignore").decode("ascii").strip(),
                latitude=lat.encode("ascii", "ignore").decode("ascii").strip(),
                longitude=longt.encode("ascii", "ignore").decode("ascii").strip(),
                hours_of_operation=hours.encode("ascii", "ignore")
                .decode("ascii")
                .strip(),
            )


def scrape():

    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.PageUrlId)
    ) as writer:

        results = fetch_data()
        for rec in results:
            writer.write_row(rec)


scrape()
