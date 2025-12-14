const baseUrl = 'http://127.0.0.1:6969'; // Set your FastAPI base URL
const blogEndpoint = `${baseUrl}/api/v1/blogs`; // Assuming this is your base route

// --- A. Registration (POST) Logic ---

document.getElementById('metadataForm').addEventListener('submit', async function(event) {
    event.preventDefault();

    const form = event.target;
    const messageElement = document.getElementById('responseMessage');
    
    messageElement.textContent = 'Submitting...';
    messageElement.style.color = '#3498db';

    // 1. Collect Data from Form Fields
    const keywordsRaw = form.elements.keywords.value;
    const referencesRaw = form.elements.references.value;
    
    const parseStringArray = (rawText) => {
        if (!rawText) return [];
        // Split by comma or line break, filter out empty strings, and trim whitespace
        return rawText.split(/[\n,]/).map(item => item.trim()).filter(item => item);
    };
    
    // Check for optional date field
    const publishedAtValue = form.elements.published_at.value;
    const publishedAt = publishedAtValue ? publishedAtValue : null;

    // 2. Assemble the JSON Payload (Matches RegisterBlogRequest structure)
    const payload = {
        "title": form.elements.title.value,
        "category": form.elements.category.value,
        "keywords": parseStringArray(keywordsRaw),
        "published_at": publishedAt, 
        "content_file": form.elements.content_file.value,
        "references": parseStringArray(referencesRaw),
        "state": form.elements.state.value // FastAPI expects the string value ("published" or "drafted")
    };
    
    console.log('Sending JSON Payload:', payload);
    
    // 3. Make the API request
    try {
        const response = await fetch(`${blogEndpoint}/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload),
        });

        const responseBody = await response.json();

        if (!response.ok) {
            // Handle HTTP error status codes (4xx, 5xx)
            const detail = responseBody.detail || response.statusText || 'Unknown error';
            throw new Error(`Registration failed: ${detail}`);
        }
        
        // --- FIX: Read the ID property from the successful response body ---
        const registeredId = responseBody.id; 

        if (registeredId) {
            messageElement.textContent = `✅ Registered successfully! ID: ${registeredId}`;
        } else {
            messageElement.textContent = `✅ Registered, but ID was missing from response. Status: ${responseBody.status}`;
        }
        
        messageElement.style.color = 'green';
        
        // Optionally refresh the list after a successful registration
        fetchBlogs(); 

    } catch (error) {
        console.error('Submission Error:', error);
        messageElement.textContent = `❌ Submission failed: ${error.message}`;
        messageElement.style.color = 'red';
    }
});


// --- B. Retrieval (GET) Logic ---

document.getElementById('fetchButton').addEventListener('click', fetchBlogs);

async function fetchBlogs() {
    const resultsDiv = document.getElementById('results');
    const fetchMessage = document.getElementById('fetchMessage');
    
    resultsDiv.innerHTML = '<p>Loading...</p>';
    fetchMessage.textContent = '';

    try {
        const response = await fetch(blogEndpoint, {
            method: 'GET',
            headers: { 'Accept': 'application/json' }
        });

        const responseData = await response.json(); 
        
        if (!response.ok) {
            // Handle HTTP error status codes (4xx, 5xx)
            const detail = responseData.detail || JSON.stringify(responseData);
            throw new Error(`Failed to fetch blogs. Status: ${response.status}. Detail: ${detail}`);
        }
        
        // --- FIX: Extract the array from the wrapper object (GetBlogsResponse) ---
        const blogs = responseData.blogs; 
        
        if (!Array.isArray(blogs)) {
            // This catches the original error and provides context
            console.error('API returned malformed data. Expected a list in the "blogs" key.', responseData);
            throw new Error(`API returned malformed data. Status: ${responseData.status} - ${responseData.message}`);
        }

        // Display results
        if (blogs.length === 0) {
            resultsDiv.innerHTML = '<p>No blog entries found in the database.</p>';
            return;
        }

        resultsDiv.innerHTML = '';
        blogs.forEach(blog => {
            const date = blog.dates.published_at || 'N/A';
            const item = document.createElement('div');
            item.className = 'blog-item';
            item.innerHTML = `
                <h4>${blog.title} (ID: ${blog.id})</h4>
                <p><strong>Category:</strong> ${blog.category} | <strong>State:</strong> ${blog.state}</p>
                <p><strong>Published:</strong> ${date} | <strong>Created:</strong> ${blog.dates.created_at}</p>
                <p><strong>Keywords:</strong> ${blog.keywords.join(', ')}</p>
            `;
            resultsDiv.appendChild(item);
        });

        fetchMessage.textContent = `✅ Successfully retrieved ${blogs.length} blogs.`;

    } catch (error) {
        console.error('Fetch Error:', error);
        resultsDiv.innerHTML = `<p style="color: red;">Error: ${error.message}</p>`;
        fetchMessage.textContent = `❌ Fetch failed: ${error.message}`;
    }
}
