let page = 0;
let src = "";
let keyword = "";
let fetching = true;
const stations = document.querySelector(".stations");

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
    console.log("right");
    stations.scrollLeft += 200;
});

document.getElementById("left-btn").addEventListener("click", () => {
    console.log("left");
    stations.scrollLeft -= 200;
});

function getKeyword() {
    return document.querySelector(".spot-input").value;
}

document.addEventListener("click", (event) => {
    if (event.target.classList.contains("station")) {
        keyword = event.target.textContent;
        document.querySelector(".spot-input").value = keyword;
        console.log(keyword);
        page = 0;
        fetching = true;
        document.querySelector(".allcard").innerHTML = "";
        getCards();
    }
});

document.getElementById("search-btn").addEventListener("click", () => {
    keyword = getKeyword();

    page = 0;
    fetching = true;
    document.querySelector(".allcard").innerHTML = ""; //erase all cards
    getCards();

});

async function getCards() {
    if (!fetching) return; //If fetching is set to false exit.

    if (page != null && keyword === "") {
        src = `/api/attractions?page=${page}`;
    } else {
        src = `/api/attractions?page=${page}&keyword=${keyword}`; //need to deal with page varaible
    }
    try {
        const response = await fetch(src);
        const data = await response.json();
        let result = data.data;
        let allCard = document.querySelectorAll(".allcard")

        for (let i = 0; i < Math.min(12, result.length); i++) {
            let cardWrap = document.createElement('div');
            cardWrap.className = "card-wrap";

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
        if (result.length < 12 || page >= 5) {
            fetching = false;
        } else {
            page++;
        }
    } catch (error) {
        console.error('Error fetching cards:', error);
    }

}

getCards().then(() => {
    const observer = new IntersectionObserver(
        async function (entries, observer) {
            if (entries[0].isIntersecting && fetching) {
                setTimeout(async () => {
                    await getCards();
                    observer.unobserve(entries[0].target);
                    if (fetching) {
                        observer.observe(document.querySelector("footer"));
                    }
                }, 3000);

            }
        },
        {
            rootMargin: '10px',
            threshold: 0.2,
        }
    );
    observer.observe(document.querySelector("footer"));
});


