// Tiny homemade confetti burst -- no external dependency required.
function fireConfetti() {
    const canvas = document.getElementById('confetti-canvas');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;

    const colors = ['#e8a5a5', '#d4af37', '#1e2a4a', '#f7e6e6', '#ffffff'];
    const pieces = [];
    for (let i = 0; i < 120; i++) {
        pieces.push({
            x: Math.random() * canvas.width,
            y: -20 - Math.random() * canvas.height * 0.3,
            r: 4 + Math.random() * 6,
            color: colors[Math.floor(Math.random() * colors.length)],
            speedY: 2 + Math.random() * 3,
            speedX: -2 + Math.random() * 4,
            rotation: Math.random() * 360,
            rotSpeed: -6 + Math.random() * 12,
        });
    }

    let frame = 0;
    const maxFrames = 140;

    function draw() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        pieces.forEach(p => {
            p.x += p.speedX;
            p.y += p.speedY;
            p.rotation += p.rotSpeed;
            ctx.save();
            ctx.translate(p.x, p.y);
            ctx.rotate((p.rotation * Math.PI) / 180);
            ctx.fillStyle = p.color;
            ctx.fillRect(-p.r / 2, -p.r / 2, p.r, p.r * 0.6);
            ctx.restore();
        });
        frame++;
        if (frame < maxFrames) {
            requestAnimationFrame(draw);
        } else {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
        }
    }
    requestAnimationFrame(draw);
}
