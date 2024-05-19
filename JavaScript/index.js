document.getElementById('generateBlogButton').addEventListener('click', async () => {
            

    const youtubeLink = document.getElementById('youtubeLink').value;
    const blogContent = document.getElementById('blogContent');
    
    if(youtubeLink) {
        document.getElementById('loadingCircle').style.display = 'block';
        
        blogContent.innerHTML = ''; // Clear previous content

        const endpointUrl = '/generate-blog';
        
        try {
            const response = await fetch(endpointUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ link: youtubeLink })
            });

            const data = await response.json();

            blogContent.innerHTML = data.content;

        } catch (error) {
            console.error("Error occurred:", error);
            alert("Something went wrong. Please try again later.");
            
        }
        document.getElementById('loading-circle').style.display = 'none';
    } else {
        alert("Please enter a YouTube link.");
    }
});

