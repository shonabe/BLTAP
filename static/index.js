"use strict";

{
  // document.querySelector(".thumbnail").
  // document.querySelectorAll(".thumbnail").
  const thumbnails = document.querySelectorAll(".thumbnail");
  const next = document.querySelector("#next");
  const prev = document.querySelector("#prev");
  let activeIndex = 0;



  thumbnails[0].addEventListener("click",() => {
    document.querySelector("#Top").src = thumbnails[0].src;
    activeIndex = 0;
    // document.querySelectorAll(".thumbnail")[1].
    thumbnails[0].classList.add("active");
    thumbnails[1].classList.remove("active");
    thumbnails[2].classList.remove("active");
  });

  thumbnails[1].addEventListener("click",() => {
    document.querySelector("#Top").src = thumbnails[1].src;
    activeIndex = 1;
    
    thumbnails[0].classList.remove("active");
    thumbnails[1].classList.add("active");
    thumbnails[2].classList.remove("active");
  });

  thumbnails[2].addEventListener("click",() => {
    document.querySelector("#Top").src = thumbnails[2].src;
    activeIndex = 2;
    
    thumbnails[0].classList.remove("active");
    thumbnails[1].classList.remove("active");
    thumbnails[2].classList.add("active");
  });

  next.addEventListener("click", () => {
    activeIndex++;
    if (activeIndex > 2) {
      activeIndex = 0;
    }
    document.querySelector("#Top").src = thumbnails[activeIndex].src;

    thumbnails[0].classList.remove("active");
    thumbnails[1].classList.remove("active");
    thumbnails[2].classList.remove("active");
    thumbnails[activeIndex].classList.add("active");
  })

  prev.addEventListener("click", () => {
    activeIndex--;
    if (activeIndex < 0) {
      activeIndex = 2;
    }
    document.querySelector("#Top").src = thumbnails[activeIndex].src;

    thumbnails[0].classList.remove("active");
    thumbnails[1].classList.remove("active");
    thumbnails[2].classList.remove("active");
    thumbnails[activeIndex].classList.add("active");
  })
}