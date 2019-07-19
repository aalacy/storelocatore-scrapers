const Apify = require('apify');
const axios = require('axios');
const jsdom = require('jsdom');
const { JSDOM } = jsdom


Apify.main(async () => {
  const data = await scrape();
  // await Apify.pushData(data);
});

async function scrape() {
  return await axios({
    method: "GET",
    url: 'https://www.instyprints.com/locations.html'
  }).then(async (resp) => {
    document = new JSDOM(resp.data).window.document;
    returnData = [];
    for (let entry of document.querySelectorAll('.location')){
      locationName = entry.querySelector('.name').textContent;
      phone = entry.querySelector('.phone').textContent;
      addr = [];
      for (let a of entry.querySelector('.address').querySelectorAll('span')){
        addr.push(a.textContent)
      }

      hours = await getHours(entry.querySelector('a.btn').getAttribute('href'));
      console.log(hours);
      latlon= latLonFromLink(entry.querySelector('a.dir-link').getAttribute('href'));
      returnData.push({
        locator_domain: 'instyprints.com',
        location_name: locationName,
        street_address: addr[0],
        city: addr[1],
        state: addr[2],
        zip: addr[3],
        country_code: 'US',
        store_number: '<MISSING>',
        phone: phone,
        location_type: '<MISSING>',
        latitude: latlon.lat,
        longitude: latlon.lon,
        hours_of_operation: hours
      })
      
    }
  });
	// Begin scraper
// document = new JSDOM(htmlContent).window.document;
	// End scraper

}

async function getHours(href){
  return await axios({
    method: 'GET',
    url: href
  }).then((resp) => {
    hoursDoc = new JSDOM(resp.data).window.document;
    return [
      `Monday: ${hoursDoc.querySelector('td.Monday').textContent}`,
      `Tuesday: ${hoursDoc.querySelector('td.Monday').textContent}`,
      `Wednesday: ${hoursDoc.querySelector('td.Monday').textContent}`,
      `Thursday: ${hoursDoc.querySelector('td.Monday').textContent}`,
      `Friday: ${hoursDoc.querySelector('td.Monday').textContent}`,
      `Saturday: ${hoursDoc.querySelector('td.Monday').textContent}`,
      `Sunday: ${hoursDoc.querySelector('td.Monday').textContent}`,
    ].join(', ')
  });
}

function latLonFromLink(href){
  [lat, lon] = href
    .replace(/^.*\@/, '') //strip everything up to latlong string
    .replace(/\/.*/, '') // strip everything after latlong string
    .split(','); //split on comma
  return {lat: lat, lon: lon}
}