document.addEventListener("DOMContentLoaded", () => {
    const socket = io.connect();
  
    socket.on("connect", () => {
      console.log("Connected to the server");
    });
  
    socket.on("new_task", (data) => {
      const taskList = document.getElementById("tasks");
      const taskElement = document.createElement("li");
      taskElement.innerHTML = data.task;
      taskList.appendChild(taskElement);
    });
  
    socket.on("update_task", (data) => {
      const taskElement = document.getElementById(task-$,{datatask_id});
      taskElement.innerHTML = data.task;
    });
  
    socket.on("delete_task", (data) => {
      const taskElement = document.getElementById(task-$,{datatask_id});
      taskElement.remove();
    });
  
    socket.on("new_comment", (data) => {
      const commentList = document.querySelector("ul");
      const commentElement = document.createElement("li");
      commentElement.innerHTML = data.comment;
      commentList.appendChild(commentElement);
    });
  });