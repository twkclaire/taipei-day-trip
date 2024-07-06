var main=""
var submitPrice=""
var itineraryIntro=document.getElementById('itinerary-intro');
var itineraryIntroNoBooking=document.getElementById('itinerary-intro-no-booking');
const submitText=document.getElementById('submit-text');
const bookingWrap=document.getElementById('booking-wrap');
const noBookingWrap=document.getElementById('no-booking-wrap');
const contactForm=document.getElementById('contact-form');
const icardInfo=document.getElementById('card-info');
const submitWrap=document.getElementById('submit-wrap');
const noBookingText=document.getElementById('no-booking-tex');
const danger=document.getElementById('danger');
const footer=document.getElementById('footer');
let attractionId, attractionname, date, booktime, price, address, img;

danger.addEventListener('click', () => {
  let token = localStorage.getItem("token");

  fetch("/api/booking", {
    method: "DELETE",
    headers: { Authorization: `Bearer ${token}` },
  })
    .then((resp) => {
      return resp.json().then((data) => {
        if (!resp.ok) {
          throw new Error(`HTTP error! status: ${resp.status}, message: ${data.message}`);
        }
        return data;
      });
    })
    .then((data) => {
      console.log(data.data)
      location.reload();
    })
    .catch((error) => {
      console.error("Error:", error);
      
    });
});

function getBooking() {
  let token = localStorage.getItem("token");

  if (token == null){
    window.location.href="/"
  }else{
    fetch("/api/booking",{
      method:"GET",
      headers:{ Authorization: `Bearer ${token}` }, 
    })
        .then((resp) => {
        return resp.json().then((data) => {
          if (!resp.ok) { 
            window.location.href="/"
            throw new Error(
              `HTTP error! status: ${resp.status}, message: ${data.message}`
            );
          }
          return data;
        });
      })
        .then((data) => {
            // console.log(data)
            
            if (!data.data){
              noBookingWrap.classList.remove('hidden-content');
              itineraryIntroNoBooking.innerHTML=`您好，${userName}，待預訂的行程如下：`;
              footer.style.height="100%";

            }else{

              bookingWrap.classList.remove('hidden-content');
              attractionId=data.data.attraction.id
              attractionname=data.data.attraction.name;
              address=data.data.attraction.address;
              time=data.data.time; 
              date=data.data.date;
              price=data.data.price;
              img= data.data.attraction.image;
              if (time=='morning'){
                booktime='早上 9 點到中午 12 點'
              } else{
                booktime='中午 12 點到中午 4 點'
              }
            //   console.log(name,address, time, date, price);
              let itineraryText=document.getElementById("itinerary-text");
              let itineraryImg=document.getElementById("itinerary-img");
              itineraryImg.src=img;
              itineraryIntro.innerHTML=`您好，${userName}，待預訂的行程如下：`
              main += `
                        <p class="itinerary-title">台北一日遊：${attractionname}</p>
                        <p><b>日期：</b>${date}</p>
                        <p><b>時間：</b>${booktime}</p> 
                        <p><b>費用：</b>新台幣${price}元</p>
                        <p><b>地點：</b>${address}</p>
                      `;
              itineraryText.innerHTML=main;
              submitPrice +=`<p>總價：新台幣${price}元<p>`;
              submitText.innerHTML=submitPrice;
              // console.log(data)
              // return (attractionId, name, date, booktime, price, address)  


            }

        })
        .catch((error) => {
          console.error("Error:", error);
          window.location.href="/"

      });
    }
  

}
document.addEventListener('userSignedIn', getBooking);


//tappay

TPDirect.setupSDK(151766, 'app_vKyZ30uktiHZqvO7mkPQHeRbWLIEkZedy8YuoJJ3IoDOcYsL2OwibQkx6qht', 'sandbox')
// Display ccv field
let fields = {
    number: {
        // css selector
        element: '#card-number',
        placeholder: '**** **** **** ****'
    },
    expirationDate: {
        // DOM object
        element: document.getElementById('card-expiration-date'),
        placeholder: 'MM / YY'
    },
    ccv: {
        element: '#card-ccv',
        placeholder: 'ccv'
    }
}    
TPDirect.card.setup({
fields: fields,
styles: {
    // Style all elements
    'input': {
        'color': 'gray'
    },
    // Styling ccv field
    'input.ccv': {
        // 'font-size': '16px'
    },
    // Styling expiration-date field
    'input.expiration-date': {
        // 'font-size': '16px'
    },
    // Styling card-number field
    'input.card-number': {
        // 'font-size': '16px'
    },
    // style focus state
    ':focus': {
        // 'color': 'black'
    },
    // style valid state
    '.valid': {
        'color': 'green'
    },
    // style invalid state
    '.invalid': {
        'color': 'red'
    },
    // Media queries
    // Note that these apply to the iframe, not the root window.
    '@media screen and (max-width: 400px)': {
        'input': {
            'color': 'orange'
        }
    }
},
// 此設定會顯示卡號輸入正確後，會顯示前六後四碼信用卡卡號
isMaskCreditCardNumber: true,
maskCreditCardNumberRange: {
    beginIndex: 6, 
    endIndex: 11
}
})


const test=document.getElementById("test");


document.getElementById('booking-form').addEventListener('submit', function(event) {
    event.preventDefault();
    
    let token = localStorage.getItem("token");
    if (token) {
      const contactName = document.getElementById("contact-name").value;
      const contactEmail = document.getElementById("contact-email").value;
      const contactPhone = document.getElementById("contact-phone").value;
      
      if (!contactName || !contactEmail || !contactPhone) {
        alert('請填寫所有必要的聯絡資訊');
        return;
      }
      
      TPDirect.card.getPrime(function (result) {
        if (result.status !== 0) {
          console.log('getPrime 錯誤');
          alert('資料有誤，請重新確認');
          return;
        }
        
        alert('getPrime 成功');
        var prime = result.card.prime;
        var res = JSON.stringify(result, null, 4);
        // console.log(res);
        // console.log(prime);

        fetch('/api/orders', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
          },
          body: JSON.stringify({
            "prime": prime,
            "order": {
              "price": price,
              "trip": {
                "attraction": {
                  "id": attractionId,
                  "name": attractionname,
                  "address": address,
                  "image": img
                },
                "date": date,
                "time": booktime
              },
              "contact": {
                "name": contactName,
                "email": contactEmail,
                "phone": contactPhone
              }
            }
          })
        })
        .then(response => response.json())
        .then(data => {
          // console.log("this is tappay result:", data);
          // console.log("this is order number:", data.data.number);
          
          let url = `/thankyou?number=${data.data.number}`;
          // console.log(url);
          window.location.href = url;
        })
        .catch(error => {
          console.error('Error', error);
        });
      });
    } else {
      signinDialog.showModal();
    }
  })

