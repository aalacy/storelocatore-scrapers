const Apify = require('apify');
const jsdom = require('jsdom');
const { JSDOM } = jsdom;
const axios = require('axios');

Apify.main(async () => {
  let regions = await getRegions();
  for (let region of regions){
    targets = await getTargets(region);
    for (let target of targets){
      data = await scrape(target);
      if (data.hours_of_operation.startsWith('Opening')) continue;
      await Apify.pushData([data]);
    } 
  }
});

async function getRegions(){
  return await axios({
    method: 'GET',
    url: 'https://www.chezcora.com/en/breakfast-restaurants'
  }).then(async (resp) => {
    document = new JSDOM(resp.data).window.document;
    const regions = [];
    for (let r of document.querySelectorAll('nav.sidebnav > ul > li > a')){
      regions.push(r.getAttribute('href'));
    }
    return regions;
  })
}

async function getTargets(region) {
  return await axios({
    method: 'GET',
    url: 'https://www.chezcora.com' + region
  }).then(async (resp) => {
      document = new JSDOM(resp.data).window.document;
      rows = document.querySelectorAll('.resto-contact');
      const links = [];
      for (let row of rows){
        links.push('https://www.chezcora.com' + row.querySelector('div.btn-plus > a').getAttribute('href'));
      }
      return links;
  })
}

async function scrape(target){
  return await axios({
    method: 'GET',
    url: target
  }).then( async (resp) => {
    document = new JSDOM(resp.data).window.document;
    addr = document.querySelector('.sous-contenu > p').innerHTML
      .replace(/\n|\t/g, "")
      .replace(/<!--.*/g, '')
      .split('<br>');
    street = addr[0].replace(',', '');
    loc = addr[1].split(',');
    phone = document.querySelector('p.telephone').innerHTML;
    name = document.querySelector('.resto-contact-seul > h2').innerHTML.replace('Cora -', '');
    restaurants_bounds = [{lat: '<MISSING>', lon: '<MISSING>'}];
    latLon = document.querySelectorAll('script');
    for (let l of latLon){
      if (l.innerHTML.includes('restaurants_bounds.push')){
        eval(l.innerHTML);
      }
    }
    hours = document.querySelector('.tabHoraire')
      .textContent
      .replace(/\n|\t/g, " ")
      .replace(/Holiday.*/g, "");
    data =  {
      locator_domain: 'chezcora.com',
      page_url: target,
      location_name: sanitize(name),
      street_address: sanitize(street),
      city: sanitize(loc[0]),
      state: sanitize(loc[1]),
      zip: sanitize(loc[2]),
      country_code: 'CA',
      store_number: '<MISSING>',
      phone: sanitize(phone),
      location_type: '<MISSING>',
      latitude: restaurants_bounds[0].lat.toString(),
      longitude: restaurants_bounds[0].lon.toString(),
      hours_of_operation: sanitize(hours),
    };
    return data;
  })
  .catch(e => {
    console.log(e);
  });
}

function sanitize(str){
  try {
    if (!str instanceof String) return '<MISSING>';
    if (!str.trim()) return '<MISSING>';
    return str.trim();
  } catch (e){
    return '<MISSING>';
  }
  
}