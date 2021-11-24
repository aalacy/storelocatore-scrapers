import csv
import re

from bs4 import BeautifulSoup

from sgrequests import SgRequests


def write_output(data):
    with open("data.csv", mode="w") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )

        # Header
        writer.writerow(
            [
                "locator_domain",
                "location_name",
                "street_address",
                "city",
                "state",
                "zip",
                "country_code",
                "store_number",
                "phone",
                "location_type",
                "latitude",
                "longitude",
                "hours_of_operation",
                "page_url",
            ]
        )
        # Body
        for row in data:
            writer.writerow(row)


# helper for getting address
def addy_extractor(src):
    arr = src.split(",")
    city = arr[0]
    prov_zip = arr[1].split(" ")
    if len(prov_zip) == 3:
        state = prov_zip[1]
        zip_code = prov_zip[2]

    return city, state, zip_code


# helper for difficult case
def addy_extractor_hard_case(src):
    arr = src.split(",")
    # special case
    if len(arr) > 2:
        city = ""
        for a in arr[:-1]:
            city += a + " "
        city = city.strip()
    else:
        city = arr[0].strip()

    # deal with state and zip
    state_zip = arr[-1].split(" ")
    # normal case
    if len(state_zip) == 3:
        state = state_zip[1].strip()
        zip_code = state_zip[2].strip()
        if zip_code == "":
            zip_code = "<MISSING>"
    # probably len of 2
    else:
        state = state_zip[1].strip()
        zip_code = "<MISSING>"

    return city, state, zip_code


def fetch_data():

    headers = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "en-US,en;q=0.9",
        "cache-control": "max-age=0",
        "connection": "keep-alive",
        "cookie": "csbwfs_show_hide_status=in_active; ct_timezone=-4; ct_checkjs=93e4c22829c2c8e8684a46048d109ea4ed60837f40639129ec6598b343f13d12; _ga=GA1.2.185812207.1622256617; _gid=GA1.2.1960819816.1622256617; _fbp=fb.1.1622256617890.898858940; csbwfs_show_hide_status=in_active; apbct_prev_referer=https%3A%2F%2Fwww.pirtekusa.com%2F; apbct_site_landing_ts=1622256793; ct_ps_timestamp=1622256794; wordpress_apbct_antibot=342b68b2638dc091f1d130d9ba6a3cc700382da15c5fcd24d452f26bc9c5d9a5; apbct_visible_fields=%7B%220%22%3A%7B%22visible_fields%22%3A%22search_zip%20search_distance%22%2C%22visible_fields_count%22%3A2%2C%22invisible_fields%22%3A%22%22%2C%22invisible_fields_count%22%3A0%7D%2C%221%22%3A%7B%22visible_fields%22%3A%22contact_name%20contact_phone%20contact_email%20contact_message%22%2C%22visible_fields_count%22%3A4%2C%22invisible_fields%22%3A%22%22%2C%22invisible_fields_count%22%3A0%7D%2C%222%22%3A%7B%22visible_fields%22%3A%22s%22%2C%22visible_fields_count%22%3A1%2C%22invisible_fields%22%3A%22%22%2C%22invisible_fields_count%22%3A0%7D%2C%223%22%3A%7B%22visible_fields%22%3A%22id%20ev%20dl%20rl%20if%20ts%20cd%5BDataLayer%5D%20cd%5BMeta%5D%20cd%5BOpenGraph%5D%20cd%5BSchema.org%5D%20cd%5BJSON-LD%5D%20sw%20sh%20v%20r%20ec%20o%20fbp%20it%20coo%20es%20tm%20exp%20rqm%22%2C%22visible_fields_count%22%3A24%2C%22invisible_fields%22%3A%22%22%2C%22invisible_fields_count%22%3A0%7D%7D; ct_fkp_timestamp=1622256811; ct_pointer_data=%5B%5B295%2C705%2C2181%5D%2C%5B335%2C264%2C3029%5D%2C%5B326%2C252%2C3213%5D%2C%5B375%2C278%2C3303%5D%2C%5B406%2C281%2C3903%5D%2C%5B408%2C284%2C6755%5D%2C%5B408%2C285%2C7094%5D%2C%5B404%2C295%2C8402%5D%2C%5B394%2C312%2C8419%5D%2C%5B257%2C488%2C8560%5D%2C%5B202%2C499%2C8702%5D%2C%5B189%2C499%2C8852%5D%2C%5B149%2C519%2C9003%5D%2C%5B144%2C520%2C9164%5D%2C%5B162%2C513%2C9326%5D%2C%5B156%2C514%2C9452%5D%2C%5B148%2C514%2C10630%5D%2C%5B150%2C514%2C10653%5D%2C%5B179%2C517%2C10804%5D%2C%5B214%2C517%2C10952%5D%2C%5B233%2C517%2C11103%5D%2C%5B256%2C518%2C11253%5D%2C%5B257%2C518%2C11421%5D%2C%5B170%2C545%2C11552%5D%2C%5B164%2C557%2C11702%5D%2C%5B161%2C565%2C12022%5D%2C%5B155%2C562%2C12181%5D%2C%5B148%2C594%2C12303%5D%2C%5B144%2C852%2C12886%5D%2C%5B145%2C851%2C12909%5D%2C%5B149%2C851%2C13053%5D%2C%5B150%2C851%2C13822%5D%2C%5B158%2C757%2C13953%5D%2C%5B231%2C474%2C14102%5D%2C%5B259%2C408%2C14253%5D%2C%5B283%2C420%2C14403%5D%2C%5B297%2C417%2C14574%5D%2C%5B284%2C418%2C14703%5D%2C%5B285%2C413%2C14870%5D%2C%5B272%2C260%2C15003%5D%2C%5B195%2C54%2C15153%5D%2C%5B220%2C0%2C15305%5D%2C%5B307%2C5%2C16133%5D%2C%5B229%2C180%2C16202%5D%2C%5B173%2C308%2C16352%5D%2C%5B97%2C543%2C16503%5D%2C%5B60%2C821%2C16653%5D%2C%5B4%2C844%2C16804%5D%5D; apbct_timestamp=1622257594; apbct_page_hits=2; apbct_cookies_test=%257B%2522cookies_names%2522%253A%255B%2522apbct_timestamp%2522%252C%2522apbct_site_landing_ts%2522%252C%2522apbct_page_hits%2522%255D%252C%2522check_value%2522%253A%252287a89e012609f03a82a5bade67e16db6%2522%257D; apbct_urls=%7B%22www.pirtekusa.com%5C%2Flocations%5C%2F%3Flist_by%3Dregion%22%3A%5B1622256793%5D%2C%22www.pirtekusa.com%5C%2Fwp-content%5C%2Fplugins%5C%2Fwordpress-store-locator%5C%2Fpublic%5C%2Fjs%5C%2Fbootstrap.min.js.map%22%3A%5B1622257594%5D%7D; apbct_site_referer=UNKNOWN",
        "host": "www.pirtekusa.com",
        "referer": "https://www.pirtekusa.com/",
        "sec-fetch-dest": "document",
        "sec-fetch-mode": "navigate",
        "sec-fetch-site": "same-origin",
        "sec-fetch-user": "?1",
        "upgrade-insecure-requests": "1",
        "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36",
    }

    locator_domain = "https://www.pirtekusa.com/"

    ext = "locations/?list_by=region"
    to_scrape = locator_domain + ext

    session = SgRequests()

    page = session.get(to_scrape, headers=headers)
    assert page.status_code == 200

    soup = BeautifulSoup(page.content, "html.parser")
    stores = soup.find_all("div", {"class": "location_wrapper"})
    all_store_data = []

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    for store in stores:
        location_name = store.find("h3").text

        br = store.find("p").find_all("br")
        if br[0].previousSibling.strip() == "Mobile Service Only":
            street_address = "<MISSING>"
            location_type = "mobile service only"
            city, state, zip_code = addy_extractor_hard_case(br[1].previousSibling)
        else:
            street_address = br[0].previousSibling.replace("\n", "").replace("\t", "")
            location_type = "<MISSING>"
            city, state, zip_code = addy_extractor(br[1].previousSibling)

        city = (
            city.replace("County Area", "County")
            .split("Cape Coral")[0]
            .split("Gainesville &")[0]
            .strip()
        )
        phone_number = br[2].previousSibling
        country_code = "US"
        store_number = "<MISSING>"

        link = store.a["href"]
        req = session.get(link, headers=headers)
        base = BeautifulSoup(req.text, "lxml")

        try:
            map_link = base.find(class_="google-map").iframe["src"]
            lat_pos = map_link.rfind("!3d")
            lat = map_link[lat_pos + 3 : map_link.find("!", lat_pos + 5)].strip()
            lng_pos = map_link.find("!2d")
            longit = map_link[lng_pos + 3 : map_link.find("!", lng_pos + 5)].strip()
        except:
            lat = "<MISSING>"
            longit = "<MISSING>"

        hours = "<INACCESSIBLE>"
        trs = base.find(id="location_information").find_all("tr")
        for tr in trs:
            if "Hours:" in tr.text:
                hours = (
                    " ".join(list(tr.stripped_strings))
                    .split("Hours:")[1]
                    .split("After Hours")[0]
                    .strip()
                )
                hours = (re.sub(" +", " ", hours)).strip()

        store_data = [
            locator_domain,
            location_name,
            street_address,
            city.strip(),
            state,
            zip_code,
            country_code,
            store_number,
            phone_number,
            location_type,
            lat,
            longit,
            hours,
            link,
        ]
        all_store_data.append(store_data)

    return all_store_data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
