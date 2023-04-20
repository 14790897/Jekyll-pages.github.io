document.addEventListener('DOMContentLoaded', function () {
  var particlesContainer = document.getElementById('particles-js');
  particlesContainer.classList.add('hidden'); // 初始化时隐藏粒子效果
  var toggleParticlesButton = document.getElementById('toggleParticles');

  toggleParticlesButton.addEventListener('click', function () {
    if (particlesContainer.classList.contains('hidden')) {
      particlesContainer.classList.remove('hidden');
      toggleParticlesButton.textContent = '关闭粒子效果';
    } else {
      particlesContainer.classList.add('hidden');
      toggleParticlesButton.textContent = '开启粒子效果';
    }
  });
});
