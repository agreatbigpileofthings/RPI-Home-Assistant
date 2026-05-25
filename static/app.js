console.log("App loaded");

let lastSpeech = "";

async function updateStats() {
    console.log("Updating stats...");

    try {
        const response = await fetch("/stats");
        const data = await response.json();

        console.log(data);

        // -----------------------
        // SYSTEM STATS
        // -----------------------
        document.getElementById("cpu").innerText = data.cpu + "%";
        document.getElementById("ram").innerText = data.ram + "%";
        document.getElementById("temp").innerText = data.temp + "C";

        // -----------------------
        // MOTION
        // -----------------------
        const motionElement = document.getElementById("motion");

        if (data.motion) {
            motionElement.innerText = "Motion Detected";
            motionElement.classList.remove("text-success");
            motionElement.classList.add("text-danger");
        } else {
            motionElement.innerText = "No Motion Detected";
            motionElement.classList.remove("text-danger");
            motionElement.classList.add("text-success");
        }

        // -----------------------
        // PERSON
        // -----------------------
        const personElement = document.getElementById("person");

        if (data.person) {
            personElement.innerText = "Person Detected";
        } else {
            personElement.innerText = "No Person Detected";
        }

        // -----------------------
        // SPEECH (CURRENT)
        // -----------------------
        const speechBox = document.getElementById("currentSpeech");

        if (data.speech) {
            speechBox.innerText = data.speech;

            // flash effect when speech changes
            if (data.speech !== lastSpeech) {
                speechBox.style.background = "yellow";

                setTimeout(() => {
                    speechBox.style.background = "transparent";
                }, 300);

                lastSpeech = data.speech;
            }
        }

        // -----------------------
        // SPEECH HISTORY
        // -----------------------
        const historyDiv = document.getElementById("speechHistory");
        historyDiv.innerHTML = "";

        if (data.speech_history) {
            data.speech_history
                .slice()
                .reverse()
                .forEach(item => {
                    const p = document.createElement("div");
                    p.innerText = item.text;
                    historyDiv.appendChild(p);
                });
        }

    } catch (err) {
        console.error("Stats update failed:", err);
    }
}

// run loop
setInterval(updateStats, 1000);
updateStats();