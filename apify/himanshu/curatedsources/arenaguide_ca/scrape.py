from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgpostal.sgpostal import parse_address_intl
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from bs4 import BeautifulSoup as bs
import re

base_url = "https://arena-guide.com/"
locator_domain = "https://arena-guide.com"


def _p(val):
    if (
        val
        and val.replace("(", "")
        .replace(")", "")
        .replace("+", "")
        .replace("-", "")
        .replace(".", " ")
        .replace("to", "")
        .replace(" ", "")
        .strip()
        .isdigit()
    ):
        return val
    else:
        return ""


ca_provinces_codes = {
    "AB",
    "BC",
    "MB",
    "NB",
    "NL",
    "NS",
    "NT",
    "NU",
    "ON",
    "PE",
    "QC",
    "SK",
    "YT",
}


def fetch_data():
    with SgRequests() as session:
        payload = '------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="action"\r\n\r\nget-items:getHeaderMapMarkers\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="type"\r\n\r\nheaderMap\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="pageType"\r\n\r\nsearch\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="postType"\r\n\r\nait-item\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="globalQueryVars[s]"\r\n\r\n\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="globalQueryVars[error]"\r\n\r\n\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="globalQueryVars[m]"\r\n\r\n\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="globalQueryVars[p]"\r\n\r\n0\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="globalQueryVars[post_parent]"\r\n\r\n\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="globalQueryVars[subpost]"\r\n\r\n\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="globalQueryVars[subpost_id]"\r\n\r\n\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="globalQueryVars[attachment]"\r\n\r\n\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="globalQueryVars[attachment_id]"\r\n\r\n0\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="globalQueryVars[name]"\r\n\r\n\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="globalQueryVars[pagename]"\r\n\r\n\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="globalQueryVars[page_id]"\r\n\r\n0\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="globalQueryVars[second]"\r\n\r\n\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="globalQueryVars[minute]"\r\n\r\n\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="globalQueryVars[hour]"\r\n\r\n\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="globalQueryVars[day]"\r\n\r\n0\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="globalQueryVars[monthnum]"\r\n\r\n0\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="globalQueryVars[year]"\r\n\r\n0\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="globalQueryVars[w]"\r\n\r\n0\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="globalQueryVars[category_name]"\r\n\r\n\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="globalQueryVars[tag]"\r\n\r\n\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="globalQueryVars[cat]"\r\n\r\n\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="globalQueryVars[tag_id]"\r\n\r\n\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="globalQueryVars[author]"\r\n\r\n\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="globalQueryVars[author_name]"\r\n\r\n\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="globalQueryVars[feed]"\r\n\r\n\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="globalQueryVars[tb]"\r\n\r\n\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="globalQueryVars[paged]"\r\n\r\n0\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="globalQueryVars[meta_key]"\r\n\r\n\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="globalQueryVars[meta_value]"\r\n\r\n\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="globalQueryVars[preview]"\r\n\r\n\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="globalQueryVars[sentence]"\r\n\r\n\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="globalQueryVars[title]"\r\n\r\n\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="globalQueryVars[fields]"\r\n\r\n\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="globalQueryVars[menu_order]"\r\n\r\n\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="globalQueryVars[embed]"\r\n\r\n\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="globalQueryVars[posts_per_page]"\r\n\r\n20\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="globalQueryVars[post_type]"\r\n\r\nait-item\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="globalQueryVars[suppress_filters]"\r\n\r\nfalse\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="globalQueryVars[meta_query][featured_clause][key]"\r\n\r\n_ait-item_item-featured\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="globalQueryVars[meta_query][featured_clause][compare]"\r\n\r\nEXISTS\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="globalQueryVars[orderby][featured_clause]"\r\n\r\nDESC\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="globalQueryVars[orderby][title]"\r\n\r\nASC\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="globalQueryVars[ignore_sticky_posts]"\r\n\r\nfalse\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="globalQueryVars[cache_results]"\r\n\r\ntrue\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="globalQueryVars[update_post_term_cache]"\r\n\r\ntrue\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="globalQueryVars[lazy_load_term_meta]"\r\n\r\ntrue\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="globalQueryVars[update_post_meta_cache]"\r\n\r\ntrue\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="globalQueryVars[nopaging]"\r\n\r\nfalse\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="globalQueryVars[comments_per_page]"\r\n\r\n50\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="globalQueryVars[no_found_rows]"\r\n\r\nfalse\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="globalQueryVars[order]"\r\n\r\nDESC\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="query-data[search-filters][selectedCount]"\r\n\r\n20\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="query-data[search-filters][selectedOrderBy]"\r\n\r\ntitle\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="query-data[search-filters][selectedOrder]"\r\n\r\nASC\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="query-data[advanced-filters]"\r\n\r\n\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="query-data[search-params][s]"\r\n\r\n\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="query-data[search-params][category]"\r\n\r\n\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="query-data[search-params][location-address]"\r\n\r\n80261\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="query-data[search-params][lat]"\r\n\r\n\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="query-data[search-params][lon]"\r\n\r\n\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="query-data[search-params][runits]"\r\n\r\nkm\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="query-data[search-params][rad]"\r\n\r\n100\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="query-data[search-params][a]"\r\n\r\ntrue\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="query-data[ajax][limit]"\r\n\r\n5000\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="query-data[ajax][offset]"\r\n\r\n0\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="lang"\r\n\r\nen\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="is_post_preview"\r\n\r\nfalse\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="search-params[s]"\r\n\r\n\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="search-params[category]"\r\n\r\n\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="search-params[location-address]"\r\n\r\n80261\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="search-params[lat]"\r\n\r\n\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="search-params[lon]"\r\n\r\n\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="search-params[runits]"\r\n\r\nkm\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="search-params[rad]"\r\n\r\n100\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="search-params[a]"\r\n\r\ntrue\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="ignorePagination"\r\n\r\ntrue\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="enableTel"\r\n\r\ntrue\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW--'
        headers = {
            "content-type": "multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW",
            "cache-control": "no-cache",
            "postman-token": "7acdbaf7-3eba-6142-3f10-b97f02cb29ec",
        }

        response = session.post(
            "https://arena-guide.com/wp-admin/admin-ajax.php",
            data=payload,
            headers=headers,
        ).json()["data"]["raw_data"]["markers"]

        for name in response:
            soup = bs(name["context"], "lxml")
            raw_address = soup.select_one("span.item-address").text.strip()
            if not raw_address.replace("Canada", "").replace(",", "").strip():
                continue
            if "(" in raw_address:
                raw_address = (
                    raw_address.split("(")[0] + " " + raw_address.split(")")[-1]
                )
            raw_address = (
                raw_address.replace("U.S", "USA")
                .replace("USA, USA", "USA")
                .replace("BCV6C", "BC V6C")
            )
            ca_zip_list = re.findall(
                r"[A-Z]{1}[0-9]{1}[A-Z]{1}\s*[0-9]{1}[A-Z]{1}[0-9]{1}", str(raw_address)
            )
            us_zip_list = re.findall(
                re.compile(r"\b[0-9]{5}(?:-[0-9]{4})?\b"), str(raw_address)
            )

            country_code = ""
            zipp = ""
            if ca_zip_list:
                zipp = ca_zip_list[-1]
                country_code = "Canada"

            elif us_zip_list:
                zipp = us_zip_list[-1]
                country_code = "USA"
            if (
                "Canada" not in raw_address
                and "USA" not in raw_address
                and "United States" not in raw_address
            ):
                raw_address = raw_address + ", " + country_code

            if raw_address.startswith(","):
                raw_address = raw_address[1:]

            addr = parse_address_intl(raw_address)
            street_address = addr.street_address_1 or ""
            if addr.street_address_2:
                street_address += " " + addr.street_address_2

            if street_address and street_address.isdigit():
                street_address = raw_address.split(",")[0].strip()
            city = addr.city
            state = addr.state

            if "T-126" in street_address:
                street_address = "T-126, 100 Ramillies Rd."
                city = "Angus"

            if "604 rue 9e " in street_address:
                street_address = "604 rue 9e (boul. Desrochers)"
                city = "La Pocatière"

            if city == "Port Colborne On L3K5W3":
                city = "Port Colborne"
                state = "On"
            if city == "1V5":
                city = ""
            try:
                phone = (
                    soup.find("a", {"class": "phone"})
                    .text.split("ext")[0]
                    .split("EXT")[0]
                    .split("x")[0]
                    .split("#")[0]
                    .split(",")[0]
                    .replace("(Main)", "")
                    .replace("E", "")
                    .replace("CITY", "")
                    .split("/")[0]
                    .replace("(Arena)", "")
                    .split("X")[0]
                    .strip()
                )
            except:
                phone = "<MISSING>"

            if addr.country:
                country_code = addr.country

            if state in ca_provinces_codes:
                country_code = "Canada"

            if city:
                city = city.split("Sainte-Foy")[0].replace(",", "")
                if "Port Hope On" in city:
                    city = "Port Hope"
                    state = "ON"
            if country_code == "Canada":
                if state and state != "New Brunswick":
                    state = state.split()[0]
                _cc = []
                if city and state:
                    for tt in city.split():
                        if state.lower().strip() == tt.lower().strip():
                            break
                        _cc.append(tt)

                    city = " ".join(_cc)

                if street_address and state:
                    _ss = []
                    for tt in street_address.split():
                        if state.lower().strip() == tt.lower().strip():
                            break
                        _ss.append(tt)
                    street_address = " ".join(_ss)

            yield SgRecord(
                page_url=soup.find("a")["href"],
                location_name=name["title"],
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zipp,
                country_code=country_code,
                phone=_p(phone),
                latitude=name["lat"],
                longitude=name["lng"],
                locator_domain=locator_domain,
                raw_address=raw_address,
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
