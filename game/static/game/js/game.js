function normalizeRole(roleName) {
    return roleName
        .toLowerCase()
        .replace(/\s+/g, '-')      // spaces → hyphen
}

function showNightUI(roleName) {
    console.log("Running show night (" + roleName + ")")
    document.querySelectorAll(".night-role-ui")
        .forEach(el => el.classList.add("hidden"));
        const id = normalizeRole(roleName) + "-ui";
        console.log("Night role id: " + id)
    document.getElementById(id)?.classList.remove("hidden");
    
}


const protocol = window.location.protocol === "https:" ? "wss" : "ws";

const playerId = window.LOBBY_DATA.playerId;

const socket = new WebSocket(
    `${protocol}://${window.location.host}/ws/game/?player_id=${playerId}`
);
const list = document.getElementById("player-list");
const myId = parseInt(list.dataset.myId || 0);

socket.onmessage = function(event) {
    
    const data = JSON.parse(event.data);
    console.log("Raw event data:", event.data);

    if (data.type === "players_update") {
        const players = data.players; // get the array
        const player = data.player;
        console.log("Parsed JSON:", players);
        
        // const list = document.getElementById("player-list");
        list.innerHTML = "";
        
        players.forEach(p => {
            const li = document.createElement("li");
            
            let text = p.name;
            
            if (p.id === myId) {
                li.style.fontWeight = "bold";
                li.style.color = "black";
                text = `${p.name} (${p.role})`;
            }
            else if (p.role === "Narrator" || player.role === "Narrator") {
                text = `${p.name} (${p.role})`;
            }
            
            li.textContent = text;
            list.appendChild(li);
        });
    }

    else if (data.type === "advance_night") {
        const curRole = document.getElementById("secondary-phase")
        console.log("Night advanced:", data.role);
        curRole.textContent = data.role;
        showNightUI(data.role);
    }
}

function getCookie(name) {
    let cookieValue = null;

    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');

        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();

            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }

    return cookieValue;
}



document.getElementById("advanceBtn").addEventListener("click", function() {
    fetch("/game/", {
        method: "POST",
        headers: {
            "X-CSRFToken": getCookie("csrftoken"),
            "Content-Type": "application/x-www-form-urlencoded",
        },
        body: "action=advance_phase"
    });
});
