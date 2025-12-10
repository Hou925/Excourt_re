// app.js
App({
  onLaunch() {
    // 展示本地存储能力
    const logs = wx.getStorageSync('logs') || []
    logs.unshift(Date.now())
    wx.setStorageSync('logs', logs)

    // 登录
    wx.login({
      success: res => {
        // 发送 res.code 到后台换取 openId, sessionKey, unionId
      }
    })
  },
  globalData: {
    userInfo: null
  },
  navFromIndex(e) {
    const data = e.currentTarget.dataset
    const url = data.path
    //console.log(url);
    this.setData({
      selected: data.index
    })
    wx.navigateTo({
      url: url,
      events: {
        resetData: function(data) {
          // 重置原页面的数据
          console.log('页面返回时重置数据');
          this.setData({
            selected:0
          });
        }
      },
      success: function() {
        console.log('页面跳转成功');
      },
      fail: function(err) {
        console.error('页面跳转失败', err);
      }
    });
  },
  clearAllPageData() {
    const pages = getCurrentPages(); // 获取当前加载的页面实例
    pages.forEach((page) => {
        if (page.setData) {
            const keys = Object.keys(page.data); // 获取页面所有数据的键
            const resetData = {};
            keys.forEach((key) => {
                resetData[key] = Array.isArray(page.data[key]) ? [] : ""; // 根据数据类型设置空值
            });
            page.setData(resetData); // 清空数据
        }
    });
  }
})
