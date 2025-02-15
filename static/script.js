function analyzeNews() {
    let text = document.getElementById("newsInput").value;
    let image = document.getElementById("imageUpload").files[0];
    let resultDiv = document.getElementById("result");
    let analyzeButton = document.querySelector(".analyze");

    // Clear previous result & show loading state
    resultDiv.innerHTML = "<p>✨ Analyzing... Please wait. ✨</p>";
    analyzeButton.disabled = true;
    analyzeButton.innerText = "Analyzing...";

    if (!text && !image) {
        alert("🚨 Please enter news text or upload an image!");
        analyzeButton.disabled = false;
        analyzeButton.innerText = "Analyze";
        return;
    }

    let formData = new FormData();
    if (text) formData.append("text", text);
    if (image) formData.append("image", image);

    fetch("/analyze", {
        method: "POST",
        body: formData
    })
        .then(response => response.json())
        .then(data => {
            resultDiv.innerHTML =
                `<p>🌟 <strong>Verdict ➜ </strong> ${data.verdict}</p>`;

            let downloadButton = document.getElementById("downloadReport");
            downloadButton.style.display = "inline-block";
        })
        .catch(error => {
            console.error("Error:", error);
            resultDiv.innerHTML = "<p>🚨 Error analyzing news. Please try again.</p>";
        })
        .finally(() => {
            analyzeButton.disabled = false;
            analyzeButton.innerText = "Analyze";
        });
}

function downloadReport() {
    let text = document.getElementById("newsInput").value;
    let downloadButton = document.getElementById("downloadReport");

    if (!text) {
        alert("🚨 No news text provided for the report.");
        return;
    }

    downloadButton.disabled = true;
    downloadButton.innerText = "Generating PDF...";

    fetch("/generate_report", {
        method: "POST",
        body: JSON.stringify({ text: text }),
        headers: { "Content-Type": "application/json" }
    })
        .then(response => response.blob())
        .then(blob => {
            let url = window.URL.createObjectURL(blob);
            let a = document.createElement("a");
            a.href = url;
            a.download = "News_Report.pdf";
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
        })
        .catch(error => {
            console.error("Error:", error);
            alert("🚨 Error generating report. Please try again.");
        })
        .finally(() => {
            downloadButton.disabled = false;
            downloadButton.innerText = "Download Report";
        });
}
