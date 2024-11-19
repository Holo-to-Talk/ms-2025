const socket = io()

document.addEventListener('keydown', function(event) {
    if (event.key === 'Enter') {
        socket.emit('enter_pressed')
    }
});

socket.on('update_input', (data) => {
    document.getElementById('input').textContent = data.input;
});

socket.on('update_output', (data) => {
    document.getElementById('output').textContent = data.output;
});