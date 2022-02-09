from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup
from sgscrape.sgpostal import parse_address_intl

logger = SgLogSetup().get_logger("arena")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

header1 = {
    "accept": "*/*",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "en-US,en;q=0.9",
    "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://arena-guide.com/"
base_url = "https://arena-guide.com/"
json_url = "https://arena-guide.com/wp-admin/admin-ajax.php"


def _locs(cn, session):
    data = f"action=get-items%3AgetHeaderMapMarkers&type=headerMap&pageType=ait-items&postType=ait-item&globalQueryVars%5Bait-locations%5D={cn}&globalQueryVars%5Berror%5D=&globalQueryVars%5Bm%5D=&globalQueryVars%5Bp%5D=0&globalQueryVars%5Bpost_parent%5D=&globalQueryVars%5Bsubpost%5D=&globalQueryVars%5Bsubpost_id%5D=&globalQueryVars%5Battachment%5D=&globalQueryVars%5Battachment_id%5D=0&globalQueryVars%5Bname%5D=&globalQueryVars%5Bpagename%5D=&globalQueryVars%5Bpage_id%5D=0&globalQueryVars%5Bsecond%5D=&globalQueryVars%5Bminute%5D=&globalQueryVars%5Bhour%5D=&globalQueryVars%5Bday%5D=0&globalQueryVars%5Bmonthnum%5D=0&globalQueryVars%5Byear%5D=0&globalQueryVars%5Bw%5D=0&globalQueryVars%5Bcategory_name%5D=&globalQueryVars%5Btag%5D=&globalQueryVars%5Bcat%5D=&globalQueryVars%5Btag_id%5D=&globalQueryVars%5Bauthor%5D=&globalQueryVars%5Bauthor_name%5D=&globalQueryVars%5Bfeed%5D=&globalQueryVars%5Btb%5D=&globalQueryVars%5Bpaged%5D=0&globalQueryVars%5Bmeta_key%5D=&globalQueryVars%5Bmeta_value%5D=&globalQueryVars%5Bpreview%5D=&globalQueryVars%5Bs%5D=&globalQueryVars%5Bsentence%5D=&globalQueryVars%5Btitle%5D=&globalQueryVars%5Bfields%5D=&globalQueryVars%5Bmenu_order%5D=&globalQueryVars%5Bembed%5D=&globalQueryVars%5Bposts_per_page%5D=20&globalQueryVars%5Bmeta_query%5D%5Bfeatured_clause%5D%5Bkey%5D=_ait-item_item-featured&globalQueryVars%5Bmeta_query%5D%5Bfeatured_clause%5D%5Bcompare%5D=EXISTS&globalQueryVars%5Borderby%5D%5Bfeatured_clause%5D=DESC&globalQueryVars%5Borderby%5D%5Btitle%5D=ASC&globalQueryVars%5Bignore_sticky_posts%5D=false&globalQueryVars%5Bsuppress_filters%5D=false&globalQueryVars%5Bcache_results%5D=true&globalQueryVars%5Bupdate_post_term_cache%5D=true&globalQueryVars%5Blazy_load_term_meta%5D=true&globalQueryVars%5Bupdate_post_meta_cache%5D=true&globalQueryVars%5Bpost_type%5D=&globalQueryVars%5Bnopaging%5D=false&globalQueryVars%5Bcomments_per_page%5D=50&globalQueryVars%5Bno_found_rows%5D=false&globalQueryVars%5Btaxonomy%5D=ait-locations&globalQueryVars%5Bterm%5D={cn}&globalQueryVars%5Border%5D=DESC&query-data%5Bsearch-filters%5D%5BselectedCount%5D=20&query-data%5Bsearch-filters%5D%5BselectedOrderBy%5D=title&query-data%5Bsearch-filters%5D%5BselectedOrder%5D=ASC&query-data%5Badvanced-filters%5D=&query-data%5Bajax%5D%5Blimit%5D=100&query-data%5Bajax%5D%5Boffset%5D=0&lang=en&is_post_preview=false&ignorePagination=true&enableTel=true"
    res = session.post(json_url, headers=header1, data=data)
    if res.status_code != 200:
        logger.warning(f"========= {cn}")
        return []
    return res.json()["data"]["raw_data"]["markers"]


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        temp = soup.select("ul#menu-us-canada li a")
        countries = []
        for link in temp:
            if "/city/" in link["href"]:
                countries.append(link["href"])
        countries = list(set(countries))
        country_code = ""
        for country_url in countries:
            logger.info(country_url)
            country_code = country_url.split("/")[-1]
            if country_code not in ["Canada", "Usa"]:
                country_code = "canada"
            sp1 = bs(session.get(country_url, headers=_headers).text, "lxml")
            cities = [
                ll for ll in sp1.select("li.has-title a") if ll["href"] not in countries
            ]
            for city_url in cities:
                cn = city_url.text.strip()
                locations = _locs(cn, session)
                if not locations:
                    cn = city_url["href"].split("/")[-2]
                    locations = _locs(cn, session)
                logger.info(f"[{country_code}] [{cn}] {len(locations)} found")
                for _ in locations:
                    info = bs(_["context"], "lxml")
                    raw_address = info.select_one("span.item-address").text.strip()
                    addr = parse_address_intl(raw_address)
                    if addr.street_address_1:
                        street_address = addr.street_address_1
                        if addr.street_address_2:
                            street_address += " " + addr.street_address_2
                    else:
                        street_address = raw_address.split(",")[0]
                    state = addr.state
                    zip_postal = addr.postcode
                    city = addr.city
                    if city == "Parkway":
                        _addr = raw_address.split(",")
                        street_address = _addr[0].strip()
                        city = _addr[1].strip()
                    if addr.country and not country_code:
                        country_code = addr.country
                    if country_code == "canada" and not zip_postal and state:
                        _st = state.split()
                        if len(_st) > 1:
                            state = _st[0]
                            zip_postal = _st[1]
                    if zip_postal and "-" in zip_postal and country_code == "canada":
                        zip_postal = ""
                    if not state:
                        state = city_url["href"].split("/")[-2]
                    phone = ""
                    if info.select_one("a.phone"):
                        phone = info.select_one("a.phone").text.strip()
                    yield SgRecord(
                        page_url=info.a["href"],
                        location_name=_["title"],
                        street_address=street_address,
                        city=city,
                        state=state,
                        zip_postal=zip_postal,
                        country_code=country_code,
                        phone=phone,
                        latitude=_["lat"],
                        longitude=_["lng"],
                        locator_domain=locator_domain,
                        raw_address=raw_address,
                    )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
