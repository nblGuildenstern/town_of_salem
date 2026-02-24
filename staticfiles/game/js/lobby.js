const protocol = window.location.protocol === "https:" ? "wss" : "ws";

const playerId = window.LOBBY_DATA.playerId;

const socket = new WebSocket(
    `${protocol}://${window.location.host}/ws/lobby/?player_id=${playerId}`
);

const list = document.getElementById("player-list");
const myId = Number(list.dataset.myId);

socket.onmessage = function(event) {
    console.log("Raw event data:", event.data);

    const data = JSON.parse(event.data);
    const controls = document.getElementById("controls");

    
    if (data.type === "start_game") {
        window.location.href = "/game/";
        return;
    }

    const players = data.players; // get the array
    console.log("Parsed JSON:", players);

    // const list = document.getElementById("player-list");
    list.innerHTML = "";
    
    players.forEach(p => {
        const li = document.createElement("li");
        li.textContent = p.name;

        if (p.id === myId) {
            li.style.fontWeight = "bold";
            li.style.color = "black";
            if(p.role === "Narrator") {
                controls.style.display = "grid";
            }
        }

        list.appendChild(li);
    });
    console.log(list.children[0].textContent)
    console.log(players[0].role)
    list.children[0].textContent = `${players[0].name} (${players[0].role})`
};
