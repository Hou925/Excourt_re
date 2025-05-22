Page({
  data: {
    application: {} // 存储申请详细信息
  },

  onLoad: function(options) {
    this.loadApplicationDetails(options.id);
  },

  // 加载申请详细信息
  loadApplicationDetails: function(applicationId) {
    // 假设从后端获取申请详细数据
    const applicationDetails = {
      studentId: '123456',
      studentName: '张三',
      creditScore: 90
      // 添加更多详细信息
    };

    this.setData({ application: applicationDetails });
  }
});
