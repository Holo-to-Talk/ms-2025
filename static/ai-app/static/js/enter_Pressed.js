const socket = io()

document.addEventListener('keydown', function(event) {
    if (event.key === 'Enter') {
        socket.emit('enter_pressed')
    }
});