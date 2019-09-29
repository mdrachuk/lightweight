fetchId().then(reloadOnChange);

function fetchId() {
    return fetch('/id').then(data => data.text());
}

function reloadOnChange(currentId) {

    setInterval(check, 500);

    function check() {
        fetchId().then(newId => {
            if (newId !== currentId) {
                location.reload()
            }
        });
    }
}