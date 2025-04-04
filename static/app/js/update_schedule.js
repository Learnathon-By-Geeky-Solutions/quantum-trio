document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('.add-slot').forEach(button => {
      button.addEventListener('click', function () {
        const dayDiv = this.closest('.day');
        const slotsDiv = dayDiv.querySelector('.slots');
        const slotIndex = slotsDiv.querySelectorAll('.slot').length;

        const slotDiv = document.createElement('div');
        slotDiv.className = 'slot mb-2 flex';
        slotDiv.innerHTML = `
          <input type="time" name="schedule[${dayDiv.querySelector('label').textContent}][${slotIndex}][start]"
            class="block w-1/2 p-2 border rounded mb-2 mr-2" value="">
          <input type="time" name="schedule[${dayDiv.querySelector('label').textContent}][${slotIndex}][end]"
            class="block w-1/2 p-2 border rounded mb-2" value="">
        `;
        slotsDiv.appendChild(slotDiv);
      });
    });

    document.querySelector('form').addEventListener('submit', function (e) {
      const schedule = document.querySelectorAll('.day');
      let valid = true;

      schedule.forEach(day => {
        const slots = day.querySelectorAll('.slot');
        let times = [];

        slots.forEach(slot => {
          const start = slot.querySelector('input[type="time"]').value;
          const end = slot.querySelectorAll('input[type="time"]')[1].value;
          if (start && end) {
            times.push({ start: new Date(`1970-01-01T${start}:00`), end: new Date(`1970-01-01T${end}:00`) });
          }
        });

        times.sort((a, b) => a.start - b.start);

        for (let i = 0; i < times.length - 1; i++) {
          if (times[i].end > times[i + 1].start) {
            valid = false;
            alert(`Overlapping time slots detected on ${day.querySelector('label').textContent}.`);
            e.preventDefault();
            return;
          }
        }
      });

      if (!valid) {
        e.preventDefault();
      }
    });
  });
