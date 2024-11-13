const socket = io();

socket.on('update_output', (data) => {
    document.getElementById('output').textContent = data.output;
});