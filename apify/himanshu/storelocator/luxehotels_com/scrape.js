const Apify = require('apify');
const request=require('request');
const cheerio=require('cheerio');

var url = 'https://www.luxehotels.com/hotels';
 
async function scrape(){

  return new Promise(async (resolve,reject)=>{
request(url,(err,res,html)=>{

  if(!err && res.statusCode==200){
    
    
     
        const $  =cheerio.load(html);
        var items=[];

        main = $('.address').find('.full-address');

        function mainhead(i)

        {
            if(3>i)

                {
          var address_tmp = $('.address').find('ul').find('li').find('.full-address').find('p:nth-child(1)').eq(i).html();//find('p:nth-child(1)').text().trim();
          var location_name = $('.address').find('ul').find('li').find('.full-address').find('p:nth-child(1)').eq(i).find('.name').text();
          var phone = $('.address').find('ul').find('li').find('.full-address').find('p:nth-child(1)').eq(i).find('.phone-num').text();
          var address_tmp1 =  address_tmp.split('<br>');
          if(address_tmp1.length == 3){
            var address1 = address_tmp1[0].split('">');
            var address2 = address1[1].split('</span>');
            var address = address2[1].trim();
            var city_tmp = address_tmp1[1].trim();
            var city_tmp1 = city_tmp.split(',');
            var city = city_tmp1[0];
            var state_tmp = city_tmp1[1];
            var state_tmp1 = state_tmp.split(' ');
            var state = state_tmp1[1];
            var zip = state_tmp1[2];
            

            
            
          }
          else if (address_tmp1.length == 4){

            var address1 = address_tmp1[1];
            var address2 = address1.split('</span>');
            var address = address2[1].trim();
             var city_tmp = address_tmp1[2].trim();
             var city_tmp1 = city_tmp.split(' ');
             var city = city_tmp1[1].replace(',','');
             var zip = city_tmp1[0];
             var state = city_tmp1[2];
             
            
            
          }
          // var link =  $('.address').find('ul').find('li').find('.full-address').find('p:nth-child(2)').eq(i).find('a').attr('href');
          // // console.log(link);
          // request(link,(err,res,html)=>{

          //   if(!err && res.statusCode==200){
          //     const $  =cheerio.load(html);
          //     var latitude_tmp = $('script[type="text/javascrip]');
          //     console.log(html);
          //   }
      
          // });
          

          
                        items.push({  

                          locator_domain: 'https://www.luxehotels.com/', 

                          location_name: location_name, 

                          street_address: address,

                          city: city, 

                          state: state,

                          zip:  zip,

                          country_code: 'US',

                          store_number: '<MISSING>',

                          phone: phone,

                          location_type: 'luxehotels',

                          latitude: '<MISSING>',

                          longitude: '<MISSING>', 

                          hours_of_operation: '<MISSING>'}); 

                          
                          mainhead(i+1);
                       }


                    else{
                
                    resolve(items);
                
                    }
              } 

           mainhead(0);
           
       
          }
 
     });

  });
}

 

Apify.main(async () => {

    

    const data = await scrape();
    
    
    await Apify.pushData(data);
  
  });
