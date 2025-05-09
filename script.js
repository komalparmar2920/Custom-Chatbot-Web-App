document.getElementById("scrapeBtn").addEventListener("click", scrapeWebsite);
document.getElementById("sendBtn").addEventListener("click", sendMessage);
document.getElementById("website_url").addEventListener("keypress", function (event) {
    if (event.key === "Enter") {
        scrapeWebsite();
    }
});
document.getElementById("user_input").addEventListener("keypress", function (event) {
    if (event.key === "Enter") {
        sendMessage();
    }
});

function scrapeWebsite() {
    const websiteUrl = document.getElementById("website_url").value.trim();

    if (!websiteUrl) {
        alert("Please enter a website URL.");
        return;
    }

    fetch("/scrape_website", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ website_url: websiteUrl })
    })
        .then(response => response.json())
        .then(data => {
            alert(data.reply);
        })
        .catch(error => console.error("Error:", error));
}




function sendMessage() {
    const userInput = document.getElementById("user_input").value.trim();
    const chatbox = document.getElementById("chatbox");

    if (!userInput) {
        alert("Please enter a question.");
        return;
    }


    const userMessage = document.createElement("p");
    userMessage.innerHTML = `<strong>You:</strong> ${userInput}`;
    userMessage.classList.add("user-message");
    chatbox.appendChild(userMessage);

    if (userInput.startsWith("http")) {
        simulateScrapingProgress(chatbox);
        return;
    }

    fetch("/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: userInput })
    })
        .then(response => response.json())
        .then(data => {
            const botMessage = document.createElement("p");
            botMessage.innerHTML = `<strong>Bot:</strong> ${data.reply}`;
            botMessage.classList.add("bot-message");
            chatbox.appendChild(botMessage);


            chatbox.scrollTop = chatbox.scrollHeight;
        })
        .catch(error => console.error("Error:", error));

    document.getElementById("user_input").value = "";
}

function simulateScrapingProgress(chatbox) {
    const progressMessage = document.createElement("p");
    progressMessage.innerHTML = `<strong>Bot:</strong> Scraping website... 0%`;
    progressMessage.classList.add("bot-message");
    chatbox.appendChild(progressMessage);

    let progress = 0;
    const interval = setInterval(() => {
        progress += 20;
        progressMessage.innerHTML = `<strong>Bot:</strong> Scraping website... ${progress}%`;

        if (progress >= 100) {
            clearInterval(interval);
            progressMessage.innerHTML = `<strong>Bot:</strong> Website scraped successfully! Now you can ask questions just like the PDF.`;
        }
    }, 1000);
}

document.getElementById("pdf_upload").addEventListener("change", function () {
    const file = this.files[0];
    if (file) {
        uploadPDF(file);
    }
});

function uploadPDF(file) {
    const formData = new FormData();
    formData.append("file", file);

    fetch("/upload_pdf", {
        method: "POST",
        body: formData
    })
        .then(response => response.json())
        .then(data => {
            alert(data.reply);
        })
        .catch(error => console.error("Error:", error));
}
