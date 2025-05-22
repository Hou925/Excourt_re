Page({
  data: {
    schoolname: '',
    courtname: '',
    date: '',
    ownername: '',
    timeslot: '',
    timeid: 0,
    uploader_id: '',
    courtid: '',
    my_id: ''
  },

  onLoad(options) {
    const startHour = Number(options.timeid) + 9;
    const endHour = startHour + 1;
    const timeslot = `${startHour}:00 - ${endHour}:00`;
    wx.getStorage({
      key: 'student_id',  // 获取存储的 student_id
      success: (res) => {
        console.log(res.data);
        this.setData({ my_id: res.data });  // 存储 student_id
        // 使用 setData 更新页面的数据状态
        this.setData({
          courtname: options.courtname || '',
          date: options.date || '',
          ownername: options.ownername,
          schoolname: options.schoolname || '',
          timeslot: timeslot || '',
          timeid: Number(options.timeid),
          courtid: options.courtid
        });

        // 获取uploader_id（假设是通过court_id从后端获取）
        this.getUploaderId();
        console.log(this.data);
        const list = this.data.courtid.split('-')
        this.setData({
          date: list[1] + '年' + list[2] + '月' + list[3] + '日',
        });
      },
      fail: () => {
        wx.showToast({
          title: '未找到用户信息，请重新登录',
          icon: 'none',
          duration: 2000
        });
      }
    });
  },

  // 获取对应 courtid 的 uploader_id
  getUploaderId() {
    // 向后端请求获取 uploader_id
    wx.request({
      url: 'http://123.60.86.239:8000/offercourt/get_uploader_id',  // 替换成实际的获取 uploader_id 的 API 地址
      method: 'POST',
      data: {
        court_id: this.data.courtid  // 传递 court_id 给后端
      },
      header: {
        'Content-Type': 'application/json'
      },
      success: (res) => {  // 使用箭头函数，确保 this 指向当前页面实例
        console.log(res)
        if (res.data.status === 'success') {
          console.log(res.data.data.uploader_id);
          // 获取上传者ID并保存
          this.setData({
            uploader_id: res.data.data.uploader_id
          });
          // 然后调用函数响应换场请求
          this.respondToExchange();
        } else {
          wx.showToast({
            title: '获取上传者ID失败',
            icon: 'none'
          });
        }
      },
      fail: () => {
        wx.showToast({
          title: '网络请求失败',
          icon: 'none'
        });
      }
    });
  },

  // 响应换场请求
  respondToExchange() {
    var my_id = this.data.my_id;
    console.log(my_id);
    console.log(this.data.courtid);
    if (!my_id) {
      wx.showToast({
        title: '缺少必要参数',
        icon: 'none'
      });
      return;
    }

    // 调用后端接口响应换场请求
    wx.request({
      url: 'http://123.60.86.239:8000/offercourt/record', // 后端 API 地址
      method: 'POST',
      data: {
        my_id: my_id,  // 响应者学号
        court_id: this.data.courtid  // 送场场地id
      },
      header: {
        'Content-Type': 'application/json'
      },
      success: (res) => {  // 使用箭头函数，确保 this 指向当前页面实例
        if (res.data.status === 'success') {
          wx.showToast({
            title: '送场接受成功',
            icon: 'success'
          });
        } else {
          wx.showToast({
            title: res.data.message || '发生错误',
            icon: 'none'
          });
        }
      },
      fail: () => {
        wx.showToast({
          title: '网络请求失败',
          icon: 'none'
        });
      }
    });
  },
  gotoChat(){
    wx.request({
      url: 'http://123.60.86.239:8000/chat/send',
      method: 'POST',
      header: {
          'Content-Type': 'application/json',
      },
      data: {
          Sender_id: this.data.my_id,
          Receiver_id: this.data.uploader_id,
          Message_sent: '球友你好！' + '我想要你的' + this.data.courtid + '谢谢！',
      },
      success: (sendRes) => {
          if (sendRes.data.status === 'success') {
              // 消息发送成功，跳转到聊天界面
              wx.showToast({
                title: sendRes.data.message || '聊天添加成功！',
                icon: 'none',
              });
              wx.navigateTo({
                  url: '/pages/5-conversation/conversation?sender_id='+ this.data.my_id + '&receiver_id=' + this.data.uploader_id,
              },
              );
          } else {
              wx.showToast({
                  title: sendRes.data.message || '消息发送失败',
                  icon: 'none',
              });
          }
      },
      fail: () => {
          wx.showToast({
              title: '发送消息请求失败',
              icon: 'none',
          });
      },
  });
  }
});