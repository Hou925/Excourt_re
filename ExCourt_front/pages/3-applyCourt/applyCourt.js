Page({
  data: {
    dates: []
  },

  onLoad: function() {
    this.loadTimeSlots();
  },

  // 加载时间段信息
  loadTimeSlots: function() {
    const today = new Date();
    const slotsData = [];
    
    for (let i = 0; i < 7; i++) {
      const date = new Date(today);
      date.setDate(today.getDate() + i);
      const dateString = `${date.getFullYear()}-${date.getMonth() + 1}-${date.getDate()}`;
      const timeSlots = this.generateTimeSlots(date);
      slotsData.push({ date: dateString, timeSlots });
    }

    this.setData({ dates: slotsData });
  },

  generateTimeSlots: function(date) {
    const slots = [];
    const day = date.getDay();
    const startHour = (day === 0 || day === 6) ? 9 : 8; // 周末9点，工作日8点
    const endHour = 21;
  
    for (let hour = startHour; hour <= endHour; hour++) {
      const time = `${date.getFullYear()}-${date.getMonth() + 1}-${date.getDate()} ${hour}:00`;
      let statusClass;
  
      if (date.toDateString() === new Date().toDateString()) {
        statusClass = 'green'; // 今天可预约
      } else if (date.toDateString() === new Date(Date.now() + 86400000).toDateString()) {
        statusClass = 'red'; // 明天人满
      } else {
        statusClass = 'gray'; // 其余时间段未发布
      }
  
      slots.push({ time, status: statusClass });
    }
  
    return slots;
  },


  // 处理点击时间段
  handleSlotClick: function(e) {
    const slot = e.currentTarget.dataset.slot;
    const status = e.currentTarget.dataset.status;

    if (status === 'green') {
      wx.showModal({
        title: '预约确认',
        content: '确认预约该时间段吗？',
        success: (res) => {
          if (res.confirm) {
            this.sendReservation(slot); // 发送预约请求
          }
        }
      });
    } else {
      wx.showToast({
        title: '不可预约',
        icon: 'none'
      });
    }
  },

  // 发送预约请求
  sendReservation: function(slot) {
    // 模拟发送请求，实际中应与后端交互
    const success = Math.random() > 0.2; // 80%成功率

    if (success) {
      wx.showToast({
        title: '预约成功',
        icon: 'success',
        duration: 2000
      });
      // 返回组队界面
      setTimeout(() => {
        wx.navigateBack();
      }, 2000);
    } else {
      wx.showToast({
        title: '预约失败',
        icon: 'none'
      });
      // 不进行跳转
    }
  },

  // 返回按钮
  goBack: function() {
    wx.navigateBack();
  }
  
});
