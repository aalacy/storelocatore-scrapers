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

    urllist = [
        "https://merrell.locally.com/stores/conversion_data?has_data=true&company_id=62&store_mode=&style=&color=&upc=&category=&inline=1&show_links_in_list=&parent_domain=&map_center_lat=39.27451781299348&map_center_lng=-76.81424000000064&map_distance_diag=2894.9778656173057&sort_by=proximity&no_variants=0&only_retailer_id=&dealers_company_id=&only_store_id=false&uses_alt_coords=false&q=false&zoom_level=4",
        "https://merrell.locally.com/stores/conversion_data?has_data=true&company_id=62&store_mode=&style=&color=&upc=&category=&inline=1&show_links_in_list=&parent_domain=&map_center_lat=60.946062671857504&map_center_lng=-149.89490000000052&map_distance_diag=1823.6235546997798&sort_by=proximity&no_variants=0&only_retailer_id=&dealers_company_id=&only_store_id=false&uses_alt_coords=false&q=anchorage&zoom_level=4&forced_coords=1",
        "https://merrell.locally.com/stores/conversion_data?has_data=true&company_id=62&store_mode=&style=&color=&upc=&category=&inline=1&show_links_in_list=&parent_domain=&map_center_lat=20.88015885416428&map_center_lng=-156.50000000000045&map_distance_diag=893.2380425349288&sort_by=proximity&no_variants=0&only_retailer_id=&dealers_company_id=&only_store_id=false&uses_alt_coords=false&q=HI96793&zoom_level=6&forced_coords=1",
    ]
    for url in urllist:
        data_list = session.get(url, headers=headers).json()["markers"]
        weeklist = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
        for store in data_list:
            ccode = store["country"]
            street = store["address"]
            city = store["city"]
            state = store["state"]
            pcode = store["zip"]
            tel = store["phone"]
            lat = store["lat"]
            longt = store["lng"]
            storeid = store["id"]
            link = "https://merrell.locally.com/store/" + str(storeid)
            ltype = "Dealer"
            if store["company_id"] == 62:
                ltype = "Outlet"
            phone = tel.lstrip("+1")
            title = store["name"]
            hours = ""
            try:
                if store["mon_time_open"] > 0:
                    for day in weeklist:
                        closestr = str(store[day + "_time_close"])
                        openstr = str(store[day + "_time_open"])
                        if len(openstr) == 3:
                            openstr = "0" + openstr
                        if len(closestr) == 3:
                            closestr = "0" + closestr
                        if int(closestr[0:2]) < 12:
                            closestr = closestr[0:2] + ":" + closestr[2:4] + " PM "
                        else:
                            check = int(closestr[0:2]) - 12
                            closestr = str(check) + ":" + closestr[2:4] + " PM "
                        openstr = openstr[0:2] + ":" + openstr[2:4] + " AM "

                        hours = hours + day + " " + openstr + closestr
                else:
                    hours = "<MISSING>"
            except:
                hours = "<MISSING>"
            yield SgRecord(
                locator_domain="https://www.merrell.com/",
                page_url=link,
                location_name=title,
                street_address=street.strip(),
                city=city.strip(),
                state=state.strip(),
                zip_postal=pcode.strip(),
                country_code=ccode,
                store_number=str(storeid),
                phone=phone.strip(),
                location_type=ltype,
                latitude=str(lat),
                longitude=str(longt),
                hours_of_operation=hours,
            )


def scrape():

    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.PageUrlId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)


scrape()
