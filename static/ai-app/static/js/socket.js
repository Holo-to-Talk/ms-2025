const socket = io()

document.addEventListener('keydown', function(event) {
    if (event.key === 'Enter') {
        socket.emit('enter_pressed')
    }
});

socket.on('update_telop', (data) => {
    document.getElementById('telop').textContent = data.telop;
});

socket.on('update_input', (data) => {
    document.getElementById('input').textContent = data.input;
});

socket.on('update_output', (data) => {
    document.getElementById('output').textContent = data.output;
});

socket.on('update_telop_add_display_none', () => {
    document.getElementById('div_telop').classList.add('display_none');
});

socket.on('update_telop_remove_display_none', () => {
    document.getElementById('div_telop').classList.remove('display_none');
});