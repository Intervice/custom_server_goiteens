const songs = [
    "Imagine Dragons - Believer",
    "Ed Sheeran - Shape of You",
    "Beyoncé - Halo",
    "The Weeknd - Blinding Lights",
    "Coldplay - Viva La Vida",
    "Adele - Rolling in the Deep",
    "Maroon 5 - Sugar",
    "OneRepublic - Counting Stars",
    "Taylor Swift - Shake It Off",
    "Post Malone - Circles",
    "Shawn Mendes - Treat You Better",
    "Justin Bieber - Love Yourself",
    "Dua Lipa - Don't Start Now",
    "Lady Gaga - Shallow",
    "Billie Eilish - Bad Guy",
    "Bruno Mars - Uptown Funk",
    "Harry Styles - Watermelon Sugar",
    "Chainsmokers - Closer",
    "Linkin Park - Numb",
    "Katy Perry - Roar",
    "Sam Smith - Stay With Me"
];

const buttonElement = document.getElementById("searchButton");
const valueElement = document.getElementById("searchField1"); 
const resultElement = document.getElementById("searchResult");

buttonElement.addEventListener("click", () => {
    const songIndex = songs.findIndex(song => song.includes(valueElement.value))
    if (songIndex === -1) {
        alert("Song not found.");
    } else { 
        alert(songs[songIndex]); 
    }
});


