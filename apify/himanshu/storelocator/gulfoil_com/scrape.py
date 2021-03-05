import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("gulfoil_com")


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
    base_url = "http://gulfoil.com"

    headers = {"Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"}
    page = 0
    while True:
        payload = (
            "view_name=station_locator_block&view_display_id=block&view_args=&view_path=node%2F21&view_base_path=&view_dom_id=e0e9feaa193ed156dcbcc31660bcaae6&pager_element=0&field_geofield_distance%5Bdistance%5D=90000&field_geofield_distance%5Bunit%5D=3959&field_geofield_distance%5Borigin%5D=21216&page="
            + str(page)
            + "&ajax_html_ids%5B%5D=custom-bootstrap-menu&ajax_html_ids%5B%5D=block-views-station-locator-block-block&ajax_html_ids%5B%5D=views-exposed-form-station-locator-block-block&ajax_html_ids%5B%5D=edit-field-geofield-distance-wrapper&ajax_html_ids%5B%5D=edit-field-geofield-distance&ajax_html_ids%5B%5D=edit-field-geofield-distance-distance&ajax_html_ids%5B%5D=edit-field-geofield-distance-unit&ajax_html_ids%5B%5D=edit-field-geofield-distance-origin&ajax_html_ids%5B%5D=edit-submit-station-locator-block&ajax_html_ids%5B%5D=&ajax_html_ids%5B%5D=&ajax_html_ids%5B%5D=mm_sync_back_ground&ajax_page_state%5Btheme%5D=bootstrap_subtheme&ajax_page_state%5Btheme_token%5D=vRawBFWIOhvyWfJhDyfS3_x7X0PN7hvhkbt_QPtua8M&ajax_page_state%5Bcss%5D%5Bmodules%2Fsystem%2Fsystem.base.css%5D=1&ajax_page_state%5Bcss%5D%5Bmodules%2Ffield%2Ftheme%2Ffield.css%5D=1&ajax_page_state%5Bcss%5D%5Bmodules%2Fnode%2Fnode.css%5D=1&ajax_page_state%5Bcss%5D%5Bsites%2Fall%2Fmodules%2Fviews%2Fcss%2Fviews.css%5D=1&ajax_page_state%5Bcss%5D%5Bsites%2Fall%2Fmodules%2Fckeditor%2Fcss%2Fckeditor.css%5D=1&ajax_page_state%5Bcss%5D%5Bsites%2Fall%2Fmodules%2Fctools%2Fcss%2Fctools.css%5D=1&ajax_page_state%5Bcss%5D%5Bmodules%2Fgeofield%2Fcss%2Fproximity-element.css%5D=1&ajax_page_state%5Bcss%5D%5Bsites%2Fall%2Fmodules%2Fwebform%2Fcss%2Fwebform.css%5D=1&ajax_page_state%5Bcss%5D%5B%2F%2Fcdn.jsdelivr.net%2Fbootstrap%2F3.3.7%2Fcss%2Fbootstrap.css%5D=1&ajax_page_state%5Bcss%5D%5Bsites%2Fall%2Fthemes%2Fbootstrap%2Fcss%2F3.3.7%2Foverrides.min.css%5D=1&ajax_page_state%5Bcss%5D%5Bsites%2Fall%2Fthemes%2Fbootstrap_subtheme%2Fcss%2Fstyle.css%5D=1&ajax_page_state%5Bjs%5D%5B0%5D=1&ajax_page_state%5Bjs%5D%5B1%5D=1&ajax_page_state%5Bjs%5D%5B2%5D=1&ajax_page_state%5Bjs%5D%5Bhttps%3A%2F%2Fwww.google.com%2Frecaptcha%2Fapi.js%3Fonload%3Dgoogle_recaptcha_onload%26render%3Dexplicit%26hl%3Den%5D=1&ajax_page_state%5Bjs%5D%5Bsites%2Fall%2Fthemes%2Fbootstrap%2Fjs%2Fbootstrap.js%5D=1&ajax_page_state%5Bjs%5D%5B%2F%2Fajax.googleapis.com%2Fajax%2Flibs%2Fjquery%2F1.10.2%2Fjquery.min.js%5D=1&ajax_page_state%5Bjs%5D%5Bmisc%2Fjquery-extend-3.4.0.js%5D=1&ajax_page_state%5Bjs%5D%5Bmisc%2Fjquery-html-prefilter-3.5.0-backport.js%5D=1&ajax_page_state%5Bjs%5D%5Bmisc%2Fjquery.once.js%5D=1&ajax_page_state%5Bjs%5D%5Bmisc%2Fdrupal.js%5D=1&ajax_page_state%5Bjs%5D%5Bsites%2Fall%2Fmodules%2Fjquery_update%2Freplace%2Fui%2Fexternal%2Fjquery.cookie.js%5D=1&ajax_page_state%5Bjs%5D%5Bsites%2Fall%2Fmodules%2Fjquery_update%2Freplace%2Fmisc%2Fjquery.form.min.js%5D=1&ajax_page_state%5Bjs%5D%5Bmisc%2Fajax.js%5D=1&ajax_page_state%5Bjs%5D%5Bsites%2Fall%2Fmodules%2Fjquery_update%2Fjs%2Fjquery_update.js%5D=1&ajax_page_state%5Bjs%5D%5B%2F%2Fcdn.jsdelivr.net%2Fbootstrap%2F3.3.7%2Fjs%2Fbootstrap.js%5D=1&ajax_page_state%5Bjs%5D%5Bsites%2Fall%2Fmodules%2Fviews%2Fjs%2Fbase.js%5D=1&ajax_page_state%5Bjs%5D%5Bsites%2Fall%2Fthemes%2Fbootstrap%2Fjs%2Fmisc%2F_progress.js%5D=1&ajax_page_state%5Bjs%5D%5Bsites%2Fall%2Fmodules%2Fwebform%2Fjs%2Fwebform.js%5D=1&ajax_page_state%5Bjs%5D%5Bsites%2Fall%2Fmodules%2Fviews%2Fjs%2Fajax_view.js%5D=1&ajax_page_state%5Bjs%5D%5Bsites%2Fall%2Fmodules%2Fgoogle_analytics%2Fgoogleanalytics.js%5D=1&ajax_page_state%5Bjs%5D%5Bsites%2Fall%2Fthemes%2Fbootstrap%2Fjs%2Fmodules%2Fviews%2Fjs%2Fajax_view.js%5D=1&ajax_page_state%5Bjs%5D%5Bsites%2Fall%2Fthemes%2Fbootstrap%2Fjs%2Fmisc%2Fajax.js%5D=1&ajax_page_state%5Bjquery_version%5D=1.10"
        )
        json_data = session.post(
            "https://www.gulfoil.com/views/ajax", data=payload, headers=headers
        ).json()

        loc = json_data[-1]
        soup = BeautifulSoup(loc["data"], "lxml")
        if soup.find("div", {"class": "view-empty"}):
            break
        table = soup.find_all("table", {"class": "table"})
        for i in range(len(table)):
            phone = ""
            location_name = table[i].find("span").text
            address_tage = table[i].find("p")
            phone_list = re.findall(
                re.compile(r".?(\(?\d{3}\D{0,3}\d{3}\D{0,3}\d{4}).?"), str(table[i])
            )
            if phone_list:
                phone = phone_list[-1]
            us_zip_list = re.findall(
                re.compile(r"\b[0-9]{5}(?:-[0-9]{4})?\b"), str(address_tage.text)
            )
            if us_zip_list:
                zipp = us_zip_list[-1]
                country_code = "US"
            state_list = re.findall(r" ([A-Z]{2})", str(address_tage.text))
            if state_list:
                state = state_list[-1]
            full_address = list(address_tage.stripped_strings)
            city = (
                full_address[-1]
                .replace(state, "")
                .replace(zipp, "")
                .replace(",", "")
                .strip()
                .replace("CARR #123  33.2 Adjuntas Adjuntas Municipio", "Adjuntas")
            )
            street_address = " ".join(full_address[:-1]).replace(
                "BO SALTILLO", "BO SALTILLO CARR #123"
            )
            if state in ["KM"]:
                continue

            hours_of_operation = table[i].find("p", text=re.compile("Hours:"))
            if hours_of_operation is None:
                hours_of_operation = "<MISSING>"
            else:
                hours_of_operation = (
                    str(hours_of_operation.text)
                    .replace("Hours:-", "<MISSING>")
                    .replace("Hours:", "")
                )

            store = []
            locator_domain = base_url
            store.append(locator_domain if locator_domain else "<MISSING>")
            store.append(location_name if location_name else "<MISSING>")
            store.append(street_address if street_address else "<MISSING>")
            store.append(city if city else "<MISSING>")
            store.append(state if state else "<MISSING>")
            store.append(zipp if zipp else "<MISSING>")
            store.append(country_code if country_code else "<MISSING>")
            store.append("<MISSING>")
            store.append(phone if phone else "<MISSING>")
            store.append("<MISSING>")
            store.append("<MISSING>")
            store.append("<MISSING>")
            store.append(hours_of_operation)
            store.append("http://gulfoil.com/station-locator")
            yield store
        page += 1


def scrape():
    data = fetch_data()

    write_output(data)


scrape()
