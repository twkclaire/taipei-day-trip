let page = 0;
let src = "";
let keyword = "";
let isFetching = false;
const stations = document.querySelector(".stations");

//scrollable bar
async function getMrt() {
    let main = "";
    try {
        const response = await fetch('/api/mrts');
        const data = await response.json();
        let mrts = data.data
        for (let i = 0; i < mrts.length; i++) {
            let mrt = data.data[i];
            main += `<a class="station">${mrt}</a>` //build a template literal to render the data
        }
        stations.innerHTML += main;
    } catch (error) {
        console.error('Error fetching MRT data:', error);
    }

}

getMrt();

document.getElementById("right-btn").addEventListener("click", () => {
    stations.scrollLeft += 200;
});

document.getElementById("left-btn").addEventListener("click", () => {
    stations.scrollLeft -= 200;
});


//search function 
function getKeyword() {
    return document.querySelector(".spot-input").value;
}
//search via entering input
document.addEventListener("click", (event) => {
    if (event.target.classList.contains("station")) {
        keyword = event.target.textContent;
        document.querySelector(".spot-input").value = keyword;
        page = 0;
        document.querySelector(".allcard").innerHTML = "";
        // console.log("Station clicked, fetching cards for keyword:", keyword);
        getCards();
    }
});

//search via clicking scrollable bar
document.getElementById("search-btn").addEventListener("click", () => {
    keyword = getKeyword();
    page = 0;
    document.querySelector(".allcard").innerHTML = ""; //erase all cards
    // console.log("Search button clicked, fetching cards for keyword:", keyword);
    getCards();

});


//dynamic rendering cards 
async function getCards() {
    // console.log("getCards() Fetching cards for page:", page, "with keyword:", keyword);

    isFetching = true;
    if (page == null) { //stop loading if nextPage is null
        console.log(page)
        return;
    } else if (page != null && keyword === "") {
        src = `/api/attractions?page=${page}`;
    } else {
        src = `/api/attractions?page=${page}&keyword=${keyword}`;
    }
    try {
        const response = await fetch(src);
        const data = await response.json();
        const nextPage = data.nextPage
        let result = data.data;
        // console.log(result);

        let allCard = document.querySelectorAll(".allcard")

        for (let i = 0; i < Math.min(12, result.length); i++) {
            let cardWrap = document.createElement('div');
            cardWrap.className = "card-wrap";
            cardWrap.addEventListener("click",function(){
                let id=result[i].id;
                spotUrl=`http://18.199.186.172:8000/attraction/${id}`;
                window.location=spotUrl;
                // console.log(spotUrl);
            })

            let imgWrap = document.createElement('div');
            imgWrap.className = "img-wrap";

            let card = document.createElement('div');
            card.className = "card";

            let spotImage = document.createElement('img');
            spotImage.className = "spot-image";
            spotImage.src = result[i].images[0];
            spotImage.loading = "lazy";
            card.appendChild(spotImage);
            let name = document.createElement('span');
            name.className = "name";
            name.innerText = result[i].name;
            card.appendChild(name);
            imgWrap.appendChild(card);

            let textWrap = document.createElement('div');
            textWrap.className = "text-wrap";
            let stationText = document.createElement('span');
            stationText.className = "station-text";
            stationText.innerText = result[i].mrt;
            textWrap.appendChild(stationText);
            let category = document.createElement('span');
            category.className = "category";
            category.innerText = result[i].category;
            textWrap.appendChild(category);
            imgWrap.appendChild(textWrap);

            cardWrap.appendChild(imgWrap);
            allCard[0].appendChild(cardWrap);


        }
        page = nextPage;

    } catch (error) {
        console.error('Error fetching cards:', error);
    } finally {
        isFetching = false; //Set to false to prevent fast scrolling
        // console.log("getCard() finally clause: Finished fetching cards.");
 
    }

}

let isLoading = false;


getCards().then(() => {
    const observer = new IntersectionObserver(
        function (entries, observer) {
        if (page==0) { //for keyword search, prevent double fetching
            // console.log(page);
            return; 
        }else if (entries[0].isIntersecting && page!=null){
            if (isLoading){
                
                // console.log("loding is still in progress")
                return;
            }else{
                isLoading= true; 
                // console.log("Now load new cards");
                getCards().then(()=>{
                isLoading= false; 
                })
            }
        }else{
            return;
        }
       
        },
        {
            threshold: 0.2,
        }
    );
    observer.observe(document.querySelector("footer"));
    // console.log("set up new observation here");
})
// .then(()=>{
//     console.log("exit getCards");
// })








