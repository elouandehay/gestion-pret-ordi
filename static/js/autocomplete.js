function setupAutocomplete(inputId, resultsId, url, extraParamsFn = null) {
    const input = document.getElementById(inputId);
    const results = document.getElementById(resultsId);

    let timeout = null;

    input.addEventListener('input', () => {
        clearTimeout(timeout);

        timeout = setTimeout(async () => {
            const query = input.value;

            if (query.length < 1) {
                results.innerHTML = '';
                return;
            }

            let params = `q=${encodeURIComponent(query)}`;

            if (extraParamsFn) {
                params += extraParamsFn();
            }

            const response = await fetch(`${url}?${params}`);
            const data = await response.json();

            results.innerHTML = '';

            data.forEach(item => {
                const li = document.createElement('li');
                li.textContent = item;

                li.onclick = () => {
                    input.value = item;
                    results.innerHTML = '';
                };

                results.appendChild(li);
            });
        }, 200);
    });
}

// nom = normal
setupAutocomplete('nom', 'nom-results', '/api/noms');

// prénom dépend du nom (propre)
const prenomInput = document.getElementById('prenom');
const prenomResults = document.getElementById('prenom-results');

let timeoutPrenom = null;

document.getElementById('nom').addEventListener('input', () => {
    clearTimeout(timeoutPrenom);

    timeoutPrenom = setTimeout(async () => {
        const nom = document.getElementById('nom').value;

        // reset propre
        prenomInput.value = '';
        prenomResults.innerHTML = '';

        if (nom.length < 1) return;

        const response = await fetch(`/api/prenoms?nom=${encodeURIComponent(nom)}`);
        const data = await response.json();

        data.forEach(item => {
            const li = document.createElement('li');
            li.textContent = item;

            li.onclick = () => {
                prenomInput.value = item;
                prenomResults.innerHTML = '';
            };

            prenomResults.appendChild(li);
        });
    }, 300);
});
