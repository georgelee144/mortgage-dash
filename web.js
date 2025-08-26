async function  fetchDataFromPython() {
    const response =await fetch('/api/data');
    const data = await response.json();
    document.getElementById('result').innerText = data.message; 
}