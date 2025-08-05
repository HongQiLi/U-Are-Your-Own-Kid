// front/static/js/calendar.js
// 中文注释：设置 FullCalendar 拖拽事件，并将事件发送给后端保存

document.addEventListener("DOMContentLoaded", function () {
  const calendarEl = document.getElementById("calendar");

  const calendar = new FullCalendar.Calendar(calendarEl, {
    initialView: "timeGridWeek", // 以周为单位展示
    editable: true,              // 允许拖拽
    selectable: true,            // 允许选择时间段

    // 点击空白区域创建事件
    select: function (info) {
      const title = prompt("Enter your plan here");
      if (title) {
        const duration = (info.end - info.start) / 60000; // 转换为分钟
        calendar.addEvent({
          title: title,
          start: info.start,
          end: info.end,
        });

        // 发送给后端保存（假设 child_id 为 test_kid）
        fetch("/calendar/import", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            child_id: "test_kid",
            event_title: title,
            duration_minutes: duration,
          }),
        })
          .then((res) => res.json())
          .then((data) => alert(data.message))
          .catch((err) => alert("导入失败：" + err));
      }
    },
  });

  calendar.render();
});
