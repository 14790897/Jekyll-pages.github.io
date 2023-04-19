document.addEventListener("DOMContentLoaded", function () {
    var particlesEnabled = false;
    var particlesToggleBtn = document.getElementById("toggleParticles");
    var particlesContainer = document.getElementById("particles-js");
  
    particlesToggleBtn.addEventListener("click", function () {
      particlesEnabled = !particlesEnabled;
  
      if (particlesEnabled) {
        particlesToggleBtn.textContent = "关闭粒子效果";
        particlesContainer.style.display = "block";
      } else {
        particlesToggleBtn.textContent = "开启粒子效果";
        particlesContainer.style.display = "none";
      }
    });
  
    particlesContainer.style.display = "none";
  });
  