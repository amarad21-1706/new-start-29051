<!DOCTYPE html>
<html>
<head>
    <title>User Documents</title>
    {{ figure.head }}
</head>

<body>

    <div id="document-selection">
        <select id="document-selector" aria-label="Select a document">
            </select>
    </div>

    <a href="#" id="document-workflow-link" style="display: none;">Go to Workflow</a>

    <div id="document-details">
        </div>

    <script>
        const documentSelector = document.getElementById('document-selector');
        const companyId = {{ current_user.company.id }};  // Access from template

        fetch(`/api/documents/${companyId}`)
            .then(response => response.json())
            .then(data => {
                for (const document of data) {
                    const option = document.createElement('option');
                    option.value = document.id;
                    option.textContent = document.name;
                    documentSelector.appendChild(option);
                }
            })
            .catch(error => console.error(error));  // Handle errors here

        documentSelector.addEventListener('change', () => {
            const selectedDocumentId = documentSelector.value;
            if (selectedDocumentId) {
                window.location.href = `/documents/${companyId}/${selectedDocumentId}`;
            }
        });

    </script>

</body>
</html>
