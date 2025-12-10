const { BASE_URL } = require('../../utils/config.js');

Page({
  data: {
    Student_id:'',
    historyRecords: [] // 初始为空，由后端数据填充
  },

  onLoad: function() {
    wx.getStorage({key: 'student_id',success: (res) => {
      this.setData({Student_id: res.data});
      console.log(this.data.Student_id)
      this.fetchHistoryRecords();
      
    },
    fail: () => {wx.showToast({title: '未登录或学号未找到',icon: 'none'});}});
    
  },

  fetchHistoryRecords: function() {
    const that = this;
    wx.request({
      url: BASE_URL + '/student/get_my_request',
      method: 'POST',
      header: {
        'content-type': 'application/json' // 根据需要设置请求头
      },
      data: {
        my_id: this.data.Student_id // 替换为用户的实际 ID
      },
      success(res) {
        if (res.data.status === 'success') {
          console.log(res.data.data)
          const timeSlots = [
            '9:00 - 10:00', '10:00 - 11:00', '11:00 - 12:00', '12:00 - 13:00',
            '13:00 - 14:00', '14:00 - 15:00', '15:00 - 16:00', '16:00 - 17:00',
            '17:00 - 18:00', '18:00 - 19:00', '19:00 - 20:00', '20:00 - 21:00', '21:00 - 22:00'
          ];

          const records = res.data.data.map(item => {
            const courtid_split = item.court_id.split('-');
            const timeIndex = Number(courtid_split[4]);
            return {
              courtid_split,
              timeSlot: timeSlots[timeIndex] || '未知时段',
              source: item.source,
              status: item.status
            };
          });
          // const records = res.data.data.map(item => ({
          //   courtid_split: item.court_id.split('-'),
          //   source: item.source,
          //   status: item.status
          // }));
          // for(let i=0;i<records.length;i++){
          //   records[i].courtid_split[5]++
          // }
          console.log(records)
          that.setData({ historyRecords: records });
        } else {
          wx.showToast({
            title: '获取数据失败',
            icon: 'none'
          });
        }
      },
      fail() {
        wx.showToast({
          title: '请求失败',
          icon: 'none'
        });
      }
    });
  }
});
