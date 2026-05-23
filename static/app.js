console.log("App loaded")

async function updateStats(){
	
	console.log("Updating stats...")
	const response = await fetch("/stats")
	const data = await response.json()

	console.log(data)

	document.getElementById("cpu").innerText =
		 data.cpu + "%"
	document.getElementById("ram").innerText =
		 data.ram + "%"
	document.getElementById("temp").innerText =
		data.temp + "C"


	const motionElement = document.getElementById("motion")
	
	if(data.motion){
		motionElement.innerText = "Motion Detected"
		motionElement.classList.remove("text-success")
		motionElement.classList.add("text-danger")
	} else {
		motionElement.innerText = "No Motion Detected"
		motionElement.classList.remove("text-danger")
		motionElement.classList.add("text-success")
	}
}

setInterval(updateStats, 1000)

updateStats()
