import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("freemanhealth_com")

session = SgRequests()


def write_output(data):
    with open("data.csv", mode="w", newline="") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )

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

        for row in data:
            writer.writerow(row)


def fetch_data():
    url = "https://freemanhealth.com/views/ajax?_wrapper_format=drupal_ajax"
    headers = {
        "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
        "x-requested-with": "XMLHttpRequest",
    }

    for i in range(0, 16):
        payload = (
            "view_name=search&view_display_id=all_locations&view_args=&view_path=%2Fall-locations&view_base_path=all-locations&view_dom_id=5abc1973ed92f465bd3348d1553f285062bcbd15d48df5925f165e94cfa92544&pager_element=0&sort_bef_combine=title_ASC&sort_by=title&sort_order=ASC&page="
            + str(i)
            + "&_drupal_ajax=1&ajax_page_state%5Btheme%5D=whiterhino&ajax_page_state%5Btheme_token%5D=&ajax_page_state%5Blibraries%5D=better_exposed_filters%2Fauto_submit%2Cbetter_exposed_filters%2Fgeneral%2Ccohesion%2Fcoh-module%2Ccohesion%2Fcoh-theme%2Ccohesion%2Felement_templates.accordion-tabs-container%2Ccohesion%2Felement_templates.drupal-menu%2Ccohesion%2Felement_templates.drupal-view%2Ccohesion%2Felement_templates.image%2Ccohesion%2Felement_templates.link%2Ccohesion%2Felement_templates.row-for-columns%2Ccohesion%2Felement_templates.slider-container%2Ccohesion%2Fglobal_libraries.cohMatchHeights%2Ccohesion%2Fglobal_libraries.parallax_scrolling%2Ccohesion%2Fglobal_libraries.windowscroll%2Ccohesion_theme%2Fglobal-styling%2Ccore%2Fhtml5shiv%2Cfacets%2Fdrupal.facets.checkbox-widget%2Cfacets%2Fdrupal.facets.views-ajax%2Csystem%2Fbase%2Cviews%2Fviews.ajax%2Cviews%2Fviews.module%2Cwhiterhino%2Fglobal-scripts%2Cwhiterhino%2Fglobal-styling%2Cwhiterhino%2Fsearch-location-scripts"
        )

        r = session.post(url, headers=headers, data=payload)
        json_data = r.json()
        page = json_data[2]["data"]

        soup = BeautifulSoup(page, "lxml")
        pagedata = soup.find_all("article")

        for k in pagedata:

            soup1 = BeautifulSoup(session.get(k.find("a")["href"]).text, "lxml")

            location_name = soup1.find("meta", {"name": "type"})["content"].strip()
            street_address = soup1.find("meta", {"name": "streetAddress"})[
                "content"
            ].strip()
            city = soup1.find("meta", {"name": "addressLocality"})["content"].strip()
            state = soup1.find("meta", {"name": "addressRegion"})["content"].strip()
            zip_code = soup1.find("meta", {"name": "postalCode"})["content"].strip()

            try:
                phone = (
                    soup1.find("meta", {"name": "telephone"})["content"]
                    .strip()
                    .replace(".", "")
                )
            except:
                phone = "<MISSING>"
            hours_of_operation = "<MISSING>"
            page_url = k.find("a")["href"]

            soup2 = BeautifulSoup(session.get(page_url).text, "lxml")

            hours = ""
            try:
                hours = list(
                    soup2.find(
                        "h5", text=" Hours of Operation "
                    ).next_element.next_element.next_element.stripped_strings
                )
            except:
                try:
                    hours = list(
                        soup2.find(
                            "h5", text=" Hours "
                        ).next_element.next_element.next_element.stripped_strings
                    )
                except:
                    try:
                        hours = list(
                            soup2.find(
                                "h2", text="Hours"
                            ).next_element.next_element.next_element.stripped_strings
                        )
                    except:
                        hours = "<MISSING>"

            if hours == "<MISSING>":
                pass
            else:
                hours_of_operation = " ".join(hours)

            store = []
            store.append("https://www.freemanhealth.com")
            store.append(location_name)
            store.append(street_address if street_address else "<MISSING>")
            store.append(city if city else "<MISSING>")
            store.append(state if state else "<MISSING>")
            store.append(zip_code if zip_code else "<MISSING>")
            store.append("US")
            store.append("<MISSING>")
            store.append(phone if phone else "<MISSING>")
            store.append("<MISSING>")
            store.append("<MISSING>")
            store.append("<MISSING>")
            store.append(hours_of_operation)
            store.append(page_url)
            store = [x.replace("–", "-") if type(x) == str else x for x in store]
            yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
