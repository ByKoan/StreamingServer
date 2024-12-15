function toggleShuffle() {
    fetch('/shuffle', { method: 'POST' }).then(response => response.json())
        .then(data => console.log("Modo aleatorio actualizado."));
}

document.addEventListener('DOMContentLoaded', function () {
    const allowedExtensions = ['mp3', 'm4a', 'wav', 'aiff' , 'pcm', 'bwf' , 'aac', 'ogg', 'wma', 'amr', 'opus'];
    document.getElementById('file-upload-form').addEventListener('submit', function (event) {
        const fileInput = document.getElementById('file');
        const errorMessage = document.getElementById('error-message');

        errorMessage.style.display = 'none';

        if (fileInput.files.length === 0) {
            event.preventDefault();
            showErrorMessage('Por favor selecciona un archivo.');
            return;
        }

        const fileName = fileInput.files[0].name;
        const fileExtension = fileName.split('.').pop().toLowerCase();

        if (!allowedExtensions.includes(fileExtension)) {
            event.preventDefault();
            showErrorMessage('Formato no permitido. Solo se permiten archivos MP3, M4A y WAV.');
        }
    });

    function showErrorMessage(message) {
        const errorMessage = document.getElementById('error-message');
        errorMessage.textContent = message;
        errorMessage.style.display = 'block';

        setTimeout(() => {
            errorMessage.style.display = 'none';
        }, 3000);
    }
});



function nextSong() {
    fetch('/next')
        .then(response => response.json())
        .then(data => {
            // Actualiza el nombre de la canción actual
            document.getElementById('current-song').textContent = data.current_song;

            // Actualiza la lista de canciones
            const audioPlayer = document.getElementById('audio-player');
            document.getElementById('audio-source').src = "/play?" + Date.now();
            audioPlayer.load();
            audioPlayer.play(); // Forzar la reproducción

            // Actualizamos la visualización de la lista de canciones (resaltar la actual)
            const songs = document.querySelectorAll('ul li');
            songs.forEach(function (song) {
                const songText = song.textContent.trim();
                if (songText === data.current_song) {
                    {
                        song.style.backgroundColor = '#4caf50';  // Resaltamos la canción actual
                        song.style.color = '#fff';  // Aseguramos que el texto sea blanco
                    }
                } else {
                    song.style.backgroundColor = '#f9f9f9';  // Vuelve al color normal para las demás
                    song.style.color = '#333';  // Aseguramos el color para las canciones no actuales
                }
            });
        });
}

function selectSong(songNumber) {
    fetch(`/select/${songNumber}`)
        .then(response => response.json())
        .then(data => {
            // Actualiza el nombre de la canción actual
            document.getElementById('current-song').textContent = data.current_song;

            // Actualiza la lista de canciones
            const audioPlayer = document.getElementById('audio-player');
            document.getElementById('audio-source').src = "/play?" + Date.now();
            audioPlayer.load();
            audioPlayer.play(); // Forzar la reproducción

            // Actualizamos la visualización de la lista de canciones (resaltar la actual)
            const songs = document.querySelectorAll('ul li');
            songs.forEach(function (song) {
                const songText = song.textContent.trim();
                if (songText === data.current_song) {
                    song.style.backgroundColor = '#4caf50';  // Resaltamos la canción actual
                    song.style.color = '#fff';  // Aseguramos que el texto sea blanco
                } else {
                    song.style.backgroundColor = '#f9f9f9';  // Vuelve al color normal para las demás
                    song.style.color = '#333';  // Aseguramos el color para las canciones no actuales
                }
            });
        });
}