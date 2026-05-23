async function updateStats(){

	const response = await fetch("/stats")
	const data = await response.json()

	document.getElementById("cpu").innerText =
		 data.cpu + "%"
	document.getElementById("ram").innerText =
		 data.ram + "%"
	document.getElementById("temp").innerText =
		data.temp + "C"
}

setInterval(updateStats, 1000)

updateStats()
