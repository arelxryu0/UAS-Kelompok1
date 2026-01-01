let savedImage = null; // Menyimpan gambar yang sudah diupload

document.getElementById("imageInput").addEventListener("change", function(e) {
    const file = e.target.files[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = function(event) {
        savedImage = new Image();
        savedImage.src = event.target.result;

        savedImage.onload = function() {
            document.getElementById("originalImage").src = savedImage.src;
            document.getElementById("fileName").textContent = file.name;

            processImage(); // Langsung proses pertama kali
        };
    };
    reader.readAsDataURL(file);
});

document.getElementById("methodSelect").addEventListener("change", function() {
    if (savedImage) {
        processImage(); // Ganti metode tanpa menghapus gambar
    }
});

function processImage() {
    const method = document.getElementById("methodSelect").value;
    const canvas = document.getElementById("outputCanvas");
    const ctx = canvas.getContext("2d");

    // Set ukuran canvas sesuai gambar
    canvas.width = savedImage.width;
    canvas.height = savedImage.height;

    // Gambar ulang image sebagai dasar
    ctx.drawImage(savedImage, 0, 0);

    const imgData = ctx.getImageData(0, 0, canvas.width, canvas.height);
    let data = imgData.data;

    if (method === "edge") {
        // dummy simple edge (cukup buat demo)
        for (let i = 0; i < data.length; i += 4) {
            let grayscale = (data[i] + data[i+1] + data[i+2]) / 3;
            let edge = grayscale > 128 ? 255 : 0;
            data[i] = data[i+1] = data[i+2] = edge;
        }
    }

    if (method === "threshold") {
        // dummy threshold
        for (let i = 0; i < data.length; i += 4) {
            let grayscale = (data[i] + data[i+1] + data[i+2]) / 3;
            let thr = grayscale > 100 ? 255 : 0;
            data[i] = data[i+1] = data[i+2] = thr;
        }
    }

    ctx.putImageData(imgData, 0, 0);
}
