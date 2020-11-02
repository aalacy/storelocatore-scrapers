const Apify = require('apify');
const jsdom = require('jsdom');
const { JSDOM } = jsdom;
const axios = require('axios');
const usLocations = 'https://www.chronictacos.com/us-locations';
const caLocations = 'https://www.chronictacos.com/canada-locations';


Apify.main(async () => {
  let usTargets = await getUsLocations();
  for (let target of usTargets){
    data = await scrape(target);
    if (data.hours_of_operation == 'Coming Soon') continue;
    if (data.location_name == '-') continue;
    await Apify.pushData([data]);
  }
  let caTargets = await getCaLocations();
  for (let target of caTargets){
    data = await scrape(target);
    if (data.hours_of_operation == 'Coming Soon') continue;
    if (data.location_name == '-') continue;
    await Apify.pushData([data]);
  }
});

async function getCaLocations(){
  return await axios({
    method: 'GET', 
    url: caLocations
  }).then(async (resp) => {
    document = new JSDOM(resp.data).window.document;
    rows = document.querySelector('.menu-section').querySelectorAll('a');
    const links = [];
    for (let row of rows){
      links.push('https://www.chronictacos.com/' + row.getAttribute('href'));
    }
    return links;
  }) 
}

async function getUsLocations(){
  return await axios({
    method: 'GET', 
    url: usLocations
  }).then(async (resp) => {
    document = new JSDOM(resp.data).window.document;
    rows = document.querySelectorAll('.l-location');
    const links = [];
    for (let row of rows){
      links.push(row.querySelector('a').getAttribute('href'));
    }
    return links;
  })
}

async function scrape(target) {
  return await axios({
    method: 'GET', 
    url: target
  }).then(async (resp) => {
    document = new JSDOM(resp.data).window.document;
    data = document.querySelector('[type=application\\/ld\\+json]');
    data = JSON.parse(data.innerHTML.replace(/[\r\n\t]/g, ""));
    hours = [];
    for (let d of data.openingHours.split(/\s{20,}/)){
      if (!d.trim()) continue;
      hours.push(d);
    }
    hours = hours.join(" ");
    return {
        locator_domain: 'chronictacos.com',
        page_url: target,
        location_name: sanitize(target.split('/').pop()),
        street_address: sanitize(data.address.streetAddress),
        city: sanitize(data.address.addressLocality),
        state: sanitize(data.address.addressRegion),
        zip: sanitize(data.address.postalCode),
        country_code: sanitize(data.address.addressCountry),
      	store_number: '<MISSING>',
      	phone: sanitize(data.telephone),
      	location_type: '<MISSING>',
        latitude: data.geo.latitude,
        longitude: data.geo.longitude,
      	hours_of_operation: sanitize(hours)
      }
  })
}

function sanitize(str){
  if (!str instanceof String) return '<MISSING>';
  if (!str.trim()) return '<MISSING>';
  return str.trim();
}