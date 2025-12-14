document.getElementById('metadataForm').addEventListener('submit', async function(event) {
    // Prevent the default form submission behavior (page reload)
    event.preventDefault();

    const form = event.target;
    const baseUrl = 'http://127.0.0.1:6969'; 
    const endpoint = `${baseUrl}/api/v1/blog/register`;
    const messageElement = document.getElementById('responseMessage');
    
    messageElement.textContent = 'Submitting metadata via JSON...';
    messageElement.style.color = '#3498db';

    const title = form.elements.title.value;
    const category = form.elements.category.value;
    const keywordsRaw = form.elements.keywords.value;
    const content = form.elements.content.value;
    const referencesRaw = form.elements.references.value;
    const state = form.elements.state.value;
    
    const createdAt = form.elements.created_at.value;
    const publishedAt = form.elements.published_at.value || null;
    const lastUpdate = form.elements.last_update.value || null;

    const parseStringArray = (rawText) => {
        if (!rawText) return [];
        return rawText.split(/[\n,]/).map(item => item.trim()).filter(item => item);
    };

    const payload = {
        "title": title,
        "category": category,
        "keywords": parseStringArray(keywordsRaw),
        
        "dates": {
            "created_at": createdAt,
            "published_at": publishedAt,
            "last_update": lastUpdate,
        },
        
        "content": content,
        "references": parseStringArray(referencesRaw),
        
        "state": state
    };
    
    console.log('Sending JSON Payload:', payload);
    
    try {
        const response = await fetch(endpoint, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload),
        });

        if (!response.ok) {
            const errorBody = await response.json().catch(() => ({}));
            throw new Error(errorBody.detail || response.statusText || `HTTP error! Status: ${response.status}`);
        }
        
        const result = await response.json();

        messageElement.textContent = 'Metadata registered successfully!';
        messageElement.style.color = 'green';
        console.log('Success:', result);

    } catch (error) {
        console.error('Submission Error:', error);
        messageElement.textContent = `Submission failed: ${error.message}`;
        messageElement.style.color = 'red';
    }
});
