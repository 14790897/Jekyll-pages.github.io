// 在 intro-guide.js 文件中
document.addEventListener('DOMContentLoaded', function () {
  const introjs_done = getCookie('introjs_done');
  if (introjs_done === null) {
    introJs()
      .setOptions({
        // ... 其他选项
      })
      .onexit(function() {
        setCookie('introjs_done', 'true', 365);
      })
      .start();
  }
});
