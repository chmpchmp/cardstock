async function getJSON(path) {
    const response = await fetch(path)
    const output = await response.json();
    return output;
}

getJSON('https://api.scryfall.com/catalog/card-names?q=game%3Apaper')
    .then(output => {
        var searchable = output.data.filter(function (item) {
            return item.indexOf('A-') !== 0;
        });

        const searchInput = document.getElementById('search');
        const searchWrapper = document.querySelector('.wrapper');
        const resultsWrapper = document.querySelector('.results');

        searchInput.addEventListener('keyup', () => {
            var results = [];
            var input = searchInput.value;

            if (input.length) {
                results = searchable.filter((item) => {
                    return item.toLowerCase().startsWith(input.toLowerCase());
                });
            }

            while (results.length > 6) {
                results.pop();
            }

            if (input.length > 0) {
                renderResults(results);
            }
        });

        function renderResults(results) {
            if (!results.length) {
                return searchWrapper.classList.remove('show');
            }

            var content = []

            for (var index = 0; index < results.length; index++) {
                content.push(`<li><a class="nav-link active link-dark" aria-current="page" href="#" onclick="select('` + results[index] + `')">` + results[index] + `</a></li>`);
            }
            
            content = content.join('');

            searchWrapper.classList.add('show');
            resultsWrapper.innerHTML = '<ul>' + content + '</ul>';
        }
    })


function select(name) {
    getJSON('https://api.scryfall.com/cards/named?fuzzy=' + encodeURIComponent(name))
        .then(output => {
            const href = output.scryfall_uri
            window.open(href.replace('https://scryfall.com/', '').replace('?utm_source=api', '') + '.html', '_self')
        });
}