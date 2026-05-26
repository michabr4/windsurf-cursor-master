const buttons = document.querySelectorAll('.nav-btn');
const views = document.querySelectorAll('.view');

buttons.forEach((btn) => {
  btn.addEventListener('click', () => {
    const view = btn.dataset.view;

    buttons.forEach((b) => b.classList.remove('active'));
    btn.classList.add('active');

    views.forEach((v) => v.classList.remove('active'));
    document.querySelector(`#view-${view}`)?.classList.add('active');
  });
});
