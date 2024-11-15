const socket = io();

socket.on('update_input', (data) => {
    document.getElementById('input').textContent = data.input;
});

socket.on('update_output', (data) => {
    document.getElementById('output').textContent = data.output;
});