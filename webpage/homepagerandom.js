function random() {
    getJSON('https://api.scryfall.com/cards/random?q=game%3Apaper')
        .then(output => {
            const href = output.scryfall_uri
            window.open(href.replace('https://scryfall.com/', '').replace('?utm_source=api', '') + '.html', '_self')
        });
}
