Page({
  data: {
    studentId: '', // 当前评价的队员学号
    score: 0, // 用户评分
    feedback: '' // 用户输入的评价内容
  },

  onLoad: function(options) {
    this.setData({
      studentId: options.studentId // 从上一个页面获取学号
    });
  },

  // 更新评分
  updateScore: function(e) {
    this.setData({
      score: e.detail.value
    });
  },

  // 更新评价内容
  updateFeedback: function(e) {
    this.setData({
      feedback: e.detail.value
    });
  },

  // 提交评价
  submitEvaluation: function() {
    const { studentId, score, feedback } = this.data;

    // 这里可以调用后端API发送评价数据
    if (score < 1 || score > 5) {
      wx.showToast({
        title: '评分必须在1到5之间',
        icon: 'none'
      });
      return;
    }

    // 模拟发送评价请求
    wx.showToast({
      title: '提交中...',
      icon: 'loading',
      duration: 1000
    });

    setTimeout(() => {
      wx.showToast({
        title: '评价提交成功',
        icon: 'success'
      });

      // 返回上一页面
      setTimeout(() => {
        wx.navigateBack();
      }, 2000);
    }, 1000);
  }
});
