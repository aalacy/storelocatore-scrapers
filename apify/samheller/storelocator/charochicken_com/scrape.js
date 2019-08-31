const Apify = require('apify');
const axios = require('axios');
const jsdom = require("jsdom");
const { JSDOM } = jsdom;

Apify.main(async () => {
  const data = await scrape();
  await Apify.pushData(data);
});

async function scrape() {
  return await axios({
    method: 'GET',
    url: 'http://charochicken.com/mainLocate.html'
  }).then((resp) => {
    dom = new JSDOM(resp.data);
    document = dom.window.document;
    stores = document.querySelectorAll('td');
    data = [];
    for (let store of stores){
      store = store.textContent.split("\n");
      area = store[2].trim().split(",")
      city = area.shift();
      area = area.join("").split(" ");
      zip = area.pop();
      state = area.join(" ");
      data.push({
        locator_domain: 'charochicken.com',
        location_name: store[0],
        street_address: store[1].trim(),
        city: city,
        state: state,
        zip: zip,
        country_code: 'US',
        store_number: '<MISSING>',
        phone: store[3].replace("Phone", "").trim(),
        location_type: '<MISSING>',
        latitude: '<MISSING>',
        longitude: '<MISSING>',
        hours_of_operation: '<MISSING>',
      })
    }
    return data;
  })
}
