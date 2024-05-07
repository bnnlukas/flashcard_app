function toggleCard(event) {
    var card = event.currentTarget.querySelector('.card');
    card.style.transform = card.style.transform === 'rotateY(180deg)' ? 'rotateY(0deg)' : 'rotateY(180deg)';
}

function handleKeyPress(event) {
    if (event.key === ' ' || event.keyCode === 32) { // Check if the pressed key is spacebar
      toggleCard(event);
    }
  }

function markGoodKnown() {
    const spanishWord = document.querySelector('.back h2').textContent;
    fetch('/good_known', {
        method: 'POST',
        body: new URLSearchParams({ spanish_word: spanishWord }),
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        }
    }).then(response => {
        if (response.ok) {
            // Reload the page to fetch a new flashcard
            window.location.reload();
        }
    });
}

function markOkKnown() {
    const spanishWord = document.querySelector('.back h2').textContent;
    fetch('/ok_known', {
        method: 'POST',
        body: new URLSearchParams({ spanish_word: spanishWord }),
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        }
    }).then(response => {
        if (response.ok) {
            // Reload the page to fetch a new flashcard
            window.location.reload();
        }
    });
}

function markBadKnown() {
    const spanishWord = document.querySelector('.back h2').textContent;
    fetch('/bad_known', {
        method: 'POST',
        body: new URLSearchParams({ spanish_word: spanishWord }),
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        }
    }).then(response => {
        if (response.ok) {
            // Reload the page to fetch a new flashcard
            window.location.reload();
        }
    });
}

function deleteData() {
    fetch('/delete_data_from_table', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
    }).then(response => {
        if (response.ok) {
            window.location.reload();
        }
    })
}

function uploadFile() {
    fetch('/upload_file', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
    }).then(response => {
        if (response.ok) {
            window.location.reload();
        }
    })
}

function exportTable() {
    fetch('/export_table', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
    }).then(response => {
        if (response.ok) {
            window.location.reload();
        }
    })
}

function createTable() {
    fetch('/create_table', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
    }).then(response => {
        if (response.ok) {
            window.location.reload();
        }
    })
}