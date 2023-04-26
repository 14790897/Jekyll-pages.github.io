// 在 intro-guide.js 文件中
function setCookie(name, value, days) {
  const date = new Date();
  date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
  const expires = '; expires=' + date.toGMTString();
  document.cookie = name + '=' + value + expires + '; path=/';
}

function getCookie(name) {
  const nameEQ = name + '=';
  const ca = document.cookie.split(';');
  for (let i = 0; i < ca.length; i++) {
    let c = ca[i];
    while (c.charAt(0) === ' ') c = c.substring(1, c.length);
    if (c.indexOf(nameEQ) === 0) return c.substring(nameEQ.length, c.length);
  }
  return null;
}

document.addEventListener('DOMContentLoaded', function () {
  const introjs_done = getCookie('introjs_done');
  const isIntroDone = localStorage.getItem('introjs-done');
  if (introjs_done === null && isIntroDone === null) {
    introJs()
      .setOptions({
        // ... 其他选项
      })
      .onexit(function() {
        setCookie('introjs_done', 'true', 365);
        localStorage.setItem('introjs-done', 'true');
      })
      .start();
  }
});

