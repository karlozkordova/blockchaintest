const search = document.getElementById('glossary-search');
const entries = [...document.querySelectorAll('.glossary-item')];
const count = document.getElementById('glossary-count');
function filterGlossary() {
  const q = search.value.trim().toLocaleLowerCase('es');
  let visible = 0;
  for (const item of entries) {
    const match = item.textContent.toLocaleLowerCase('es').includes(q);
    item.hidden = !match;
    if (match) visible++;
  }
  count.textContent = `${visible} de ${entries.length} términos visibles`;
}
search.addEventListener('input', filterGlossary);
filterGlossary();
