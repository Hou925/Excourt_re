// pages/4-misclaim/misclaim.js
// misclaim.js
Page({
  data: {
    itemName: '',
    description: '',
    contactInfo: ''
  },

  onInputChange(e) {
    const { field } = e.currentTarget.dataset;
    this.setData({
      [field]: e.detail.value
    });
  },

  submitMisclaim() {
    const { itemName, description, contactInfo } = this.data;

    if (!itemName || !contactInfo) {
      wx.showToast({
        title: '请填写必填项',
        icon: 'none'
      });
      return;
    }

    // 保存 this 引用
    const that = this;

    wx.showModal({
      title: '提示',
      content: '申诉成功',
      showCancel: false, // 不显示取消按钮，只显示“确定”
      confirmText: '确定', // “确定”按钮文案
      success: function (res) {
        if (res.confirm) {
          that.setData({
            itemName: '',
            description: '',
            contactInfo: ''
          });

          wx.redirectTo({
            url: '/pages/4-index/indexLost'
          });
        }
      }
    });
  }
});
