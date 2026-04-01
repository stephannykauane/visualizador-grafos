document.addEventListener("keydown", function (event) {
    if (event.target.tagName.toLowerCase() === 'input') return;

    if (event.key.toLowerCase() === "v") {
        document.getElementById("hidden-add-node").click();
    }

    if (event.key === "Backspace") {
        document.getElementById("hidden-delete").click();
    }
});