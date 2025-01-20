function uploadCSV() {
    const fileInput = document.getElementById('csvFileInput');
    const uploadStatus = document.getElementById('uploadStatus');
    const file = fileInput.files[0];

    const formData = new FormData();
    formData.append('file', file);

    fetch('/api/v1/upload-csv', {
        method: 'POST',
        body: formData
    })
        .then(response => {
            if (!response.ok) {
                console.log(response);
                return response.text().then(text => {
                    throw new Error(`HTTP ${response.status}: ${text || response.statusText}`);
                });
            }
            return response.json()
        })
        .then(data => {
            uploadStatus.classList.remove('hidden');
            uploadStatus.innerHTML = `${data.filename} was uploaded successfully!`;
            if (!data.tablename) {
                uploadStatus.innerHTML += `<br>No table was updated!`;
            } else {
                uploadStatus.innerHTML += `<br><mark>${data.tablename}</mark> Table was updated!`;
            }
    })
    .catch(error => {
        uploadStatus.classList.remove('hidden');
        uploadStatus.innerHTML = `<span class="text-red-600">${error.message}</span>`;
        console.error('Error:', error);
    });

}

const downloadReport = (url) => {
    downloadButton = document.getElementById('download-link');
    downloadButton.classList.remove('hidden');
    downloadButton.href = url;
}

function generateReport(reportType, id=0) {
    let endpoint = '';

    switch(reportType) {
        case 'student-individual':
            endpoint = `/api/v1/reports/student-profile/${id}`;
            break;
        case 'academic-performance':
            endpoint = '/api/v1/reports/academic-performance';
            break;
    }

    fetch(endpoint)
    .then(response => response.blob())
    .then(blob => {
        const url = window.URL.createObjectURL(blob);
        console.log('URL:', url);
        downloadReport(url);
    })
        .catch(error => {
        console.error('Error:', error);
    });
}

function getTableView(tableName, id) {
    // Here constructing the URL parameters
    const params = new URLSearchParams();
    params.set('table', tableName);
    if (id) {
        params.set('id', id);
    }
    
    // Update browser URL without reloading the page
    const newUrl = `${window.location.pathname}#${params.toString()}`;
    window.history.pushState({ tableName, id }, '', newUrl);
    
    // Fetch and display table data
    const api_endpoint = id ? 
        `/api/v1/table/${tableName}?id=${id}` : 
        `/api/v1/table/${tableName}`;
    
    fetchTableData(api_endpoint);
}

function fetchTableData(api_endpoint) {
    fetch(api_endpoint)
        .then(response => response.json())
        .then(data => {
            const tableContent = document.getElementById('tableContent');
            const tableContainer = document.getElementById('tableContainer');

            tableContainer.classList.remove('hidden');
            tableContent.innerHTML = '';
            
            if (!data || data.length === 0) {
                tableContent.innerHTML = '<div class="text-center text-red-500 py-4">No data available</div>';
                return;
            }

            const columns = Object.keys(data[0]);
            const table = document.createElement('table');
            table.className = 'min-w-full divide-y divide-gray-200';
            
            // Create table header
            table.innerHTML = `
                <thead class="bg-gray-50 top-0">
                    <tr>
                        ${columns.map(column => `
                            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 tracking-wider">
                                ${column}
                            </th>
                        `).join('')}
                    </tr>
                </thead>
            `;

            // Create table body with clickable IDs and image handling
            table.innerHTML += `
                <tbody class="bg-white divide-y divide-gray-200">
                    ${data.map((row, index) => `
                        <tr class="${index % 2 === 0 ? 'bg-white' : 'bg-gray-50'}">
                            ${Object.entries(row).map(([key, value]) => {
                                if (key.includes('ID')) {
                                    return `
                                        <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                            <button onclick="getTableView('${key !== 'UniversityID' ? key.replace('ID', 's') : 'Universities'}', ${value})" 
                                                    class="text-blue-500 hover:underline">
                                                ${value}
                                            </button>
                                        </td>
                                    `;
                                } else if (key.includes('URL')) {
                                    return `
                                        <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                            <img src="#" 
                                                 data-image="${value}"
                                                 class="w-12 h-12 rounded-full object-cover"
                                                 alt="avatar"
                                                 onerror="this.src='static/default_student.png'">
                                        </td>
                                    `;
                                }
                                return `
                                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                        ${value ?? ''}
                                    </td>
                                `;
                            }).join('')}
                        </tr>
                    `).join('')}
                </tbody>
            `;
            
            tableContent.appendChild(table);

            // Load images after table is created
            loadImages();
        })
        .catch(error => {
            const tableContent = document.getElementById('tableContent');
            tableContent.innerHTML = '<div class="text-center text-red-500 py-4">Error fetching table data</div>';
            console.error('Error:', error);
        });
}
// Function to load images
function loadImages() {
    const images = document.querySelectorAll('img[data-image]');
    
    images.forEach(img => {
        const imageName = img.dataset.image;
        
        // Fetch image from API
        fetch(`/api/v1/image/${imageName}`)
            .then(response => response.json())
            .then(data => {
                img.src = data.image;
            })
            .catch(error => {
                console.error('Error loading image:', error);
                img.src = 'static/default_student.png';
            });
    });
}

// Handle browser back/forward buttons
window.addEventListener('popstate', (event) => {
    if (event.state) {
        const { tableName, id } = event.state;
        const api_endpoint = id ? 
            `/api/v1/table/${tableName}?id=${id}` : 
            `/api/v1/table/${tableName}`;
        fetchTableData(api_endpoint);
    }
});

// Handle initial page load with hash
window.addEventListener('load', () => {
    console.log(window.location)
    const hash = window.location.hash.slice(1);
    if (hash) {
        const params = new URLSearchParams(hash);
        const tableName = params.get('table');
        const id = params.get('id');
        if (tableName) {
            getTableView(tableName, id);
        }
    }
});