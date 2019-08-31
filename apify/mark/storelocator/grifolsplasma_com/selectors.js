const locationHrefSelector = 'div.nearby-center-detail > a';
const locationNameSelector = 'div.center-address > h2';
const streetAddressSelector = 'div.center-address > p:nth-child(2)';
const cityStateZipSelector = 'div.center-address > p:nth-child(3)';
const phoneSelector = 'div.center-address > p.telephone.desktop';
const geoUrlSelector = '#map_canvas > div > div > div:nth-child(3) > a';
const hourSelector = 'p.hours';

module.exports = {
  locationHrefSelector,
  locationNameSelector,
  streetAddressSelector,
  cityStateZipSelector,
  phoneSelector,
  geoUrlSelector,
  hourSelector,
};
