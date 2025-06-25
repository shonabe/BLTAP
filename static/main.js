"use strict"

{
  const urlParams = new URLSearchParams(window.location.search);
  const problem = urlParams.get("problem") || "easy"; // デフォルトを easy に設定


// 問題の作成（Python側にファイル名を指定し、stringsに文字列のリストが返る））

let strings;

document.addEventListener("DOMContentLoaded", async function () {
  try {
      let response = await fetch(`/training_data?problem=${problem}`);
      strings = await response.json();
      // console.log(strings);

    } catch (error) {
      console.error("データ取得エラー:", error);
      document.getElementById("target").textContent = "エラーが発生しました。";
  }
});



  function setWord() {
    string = strings.splice(Math.floor(Math.random() * strings.length), 1)[0];
    target.textContent = string;
    loc = 0;
  }



  const target = document.getElementById("target");
  
  
  let string;
  let loc;
  let startTime;
  let elapseTime;
  let isPlaying = false;

  document.addEventListener("click", () => {
    if (isPlaying === true) {
      return;
    }
    isPlaying = true; 
    startTime = Date.now();
    setWord();
  });

  
// 入力文字の判定と表示の変更
  document.addEventListener("keydown", e => {
    
    if (e.key !== string[loc]) {
      return; 
    } 

    loc++;
    target.textContent = "*".repeat(loc) + string.substring(loc);
    
    if (loc === string.length) {
      if (strings.length === 0) {
        elapseTime = ((Date.now() - startTime) / 1000).toFixed(2);
        const result = document.querySelector("#result");
        result.textContent = ` ${elapseTime} seconds `;
        

        const user_id = document.querySelector("p").dataset.userId;
        
        // console.log(elapseTime);



        // // 進捗バー更新
        // function updateProgressBar(remaining, target) {
        //   const percent = 100 * (target - remaining) / target;
        //   const progress = document.querySelector(".progress-bar");
        //   if (progress) {
        //     progress.style.width = `${percent}%`;
        //     progress.setAttribute("aria-valuenow", percent);
        //     progress.textContent = `${Math.round(percent)}%`;
        //   }

        //   const progressText = document.querySelector(".text-muted");
        //   if (progressText) {
        //     progressText.textContent = `目標達成まであと ${remaining} 回`;
        //   }
        // }

        // // 残り回数を減らす処理
        // function reduceCount() {
        //   let remaining = parseInt(localStorage.getItem("remainingCount") || "0");
        //   let target = parseInt(localStorage.getItem("targetCount") || "1");

        //   if (remaining > 0) {
        //     remaining--;
        //     localStorage.setItem("remainingCount", remaining);
        //     const remainingDisplay = document.getElementById("remainingDisplay");
        //     if (remainingDisplay) remainingDisplay.textContent = remaining;
        //     updateProgressBar(remaining, target);
        //   }
        // }

        // // 最初に残り回数・進捗を表示
        // window.addEventListener("DOMContentLoaded", () => {
        //   const remaining = localStorage.getItem("remainingCount");
        //   const target = localStorage.getItem("targetCount");

        //   if (remaining !== null && target !== null) {
        //     const remainingDisplay = document.getElementById("remainingDisplay");
        //     if (remainingDisplay) remainingDisplay.textContent = remaining;
        //     updateProgressBar(remaining, target);
        //   }
        // });

        // // 目標決定ボタン処理
        // document.getElementById("saveBtn").addEventListener("click", function () {
        //   const input = document.getElementById("trainingInput");
        //   const targetCount = parseInt(input.value);

        //   if (isNaN(targetCount) || targetCount <= 0) {
        //     alert("有効な数値を入力してください。");
        //     return;
        //   }

        //   localStorage.setItem("targetCount", targetCount);
        //   localStorage.setItem("remainingCount", targetCount);

        //   const remainingDisplay = document.getElementById("remainingDisplay");
        //   if (remainingDisplay) remainingDisplay.textContent = targetCount;

        //   updateProgressBar(targetCount, targetCount);

        //   this.disabled = true; 
        // });

        // // トレーニング終了 → DB保存後の処理
        // window.addEventListener("training-finished", () => {
        //   reduceCount();
        // });



      // 経過時間をDBに送信  
        const sendData = async () => {
        const playinfo = {
              user_id: user_id,
              level: problem,
              time: parseFloat(elapseTime)
          };

          console.log(playinfo);
      
          try {
              const response = await fetch(`/${user_id}/save`, {
                  method: "POST",
                  headers: {
                      "Content-Type": "application/json"
                  },
                  body: JSON.stringify(playinfo)
              });
              
      
              if (!response.ok) {
                  throw new Error(`HTTP error! Status: ${response.status}`);
              }
      
              const result = await response.json();
              console.log("Success:", result);


              // if (result.event === "training-finished") {
              // const trainingFinishedEvent = new CustomEvent("training-finished", {});
              //   window.dispatchEvent(trainingFinishedEvent);
              // }


          } catch (error) {
              console.error("Error:", error);
          }
        
        };
      
        sendData();

      }
      setWord();  
      
    }

    
      
  });


}