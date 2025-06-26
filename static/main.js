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
      console.log(strings);

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
        // console.log(elapseTime);

        
        // 残りトレーニング回数を減らす処理
        function reduceCount() {
          let remaining = parseInt(localStorage.getItem("remainingCount") || "0");

          if (remaining > 0) {
            remaining--;
            localStorage.setItem("remainingCount", remaining);
          }
        }
 
        // トレーニング終了 → DB保存後の処理
        window.addEventListener("training-finished", () => {
          reduceCount();
          const textMuted = document.querySelector(".text-muted");
          textMuted.textContent = `目標達成まであと ${localStorage.getItem("remainingCount")} 回`;
        });


      const user_id = document.querySelector("p").dataset.userId;

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

              if (result.event === "training-finished") {
                const trainingFinishedEvent = new CustomEvent("training-finished", {});
                window.dispatchEvent(trainingFinishedEvent);
              }


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