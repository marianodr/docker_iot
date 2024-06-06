
const btnDelete= document.querySelectorAll('.btn-borrar');
if(btnDelete) {
  const btnArray = Array.from(btnDelete);
  btnArray.forEach((btn) => {
    btn.addEventListener('click', (e) => {
      if(!confirm('¿Está seguro de querer borrar?')){
        e.preventDefault();
      }
    });
  })
}

document.addEventListener('DOMContentLoaded', function () {
  const themeSelector = document.getElementById('themeSelector');
  const themeStylesheet = document.getElementById('themeStylesheet');

  // Verificar el tema guardado en Local Storage
  const savedTheme = localStorage.getItem('theme') || 'light';
  document.body.classList.add(savedTheme);
  themeStylesheet.href = savedTheme === 'dark' 
      ? 'https://bootswatch.com/5/darkly/bootstrap.min.css' 
      : 'https://bootswatch.com/5/cosmo/bootstrap.min.css';
  themeSelector.value = savedTheme;

  // Cambiar el tema cuando el selector cambia
  themeSelector.addEventListener('change', function () {
      const selectedTheme = themeSelector.value;
      document.body.classList.toggle('dark', selectedTheme === 'dark');
      document.body.classList.toggle('light', selectedTheme === 'light');

      themeStylesheet.href = selectedTheme === 'dark' 
          ? 'https://bootswatch.com/5/darkly/bootstrap.min.css' 
          : 'https://bootswatch.com/5/cosmo/bootstrap.min.css';

      // Guardar el tema seleccionado en Local Storage
      localStorage.setItem('theme', selectedTheme);
  });
});
