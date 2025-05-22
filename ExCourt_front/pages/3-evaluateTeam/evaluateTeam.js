Page({
    data: {
      schedules: [], // 存储最近一周的拼场信息
      selectedMembers: [] // 存储当前选中的队员列表
    },
  
    onLoad: function() {
      this.loadRecentSchedules();
    },
  
    // 加载最近一周的拼场信息
    loadRecentSchedules: function() {
      const today = new Date();
      const oneWeekAgo = new Date();
      oneWeekAgo.setDate(today.getDate() - 7);
      
      // 假设从后端获取拼场数据，这里只保留已结束的拼场
      const schedulesData = [
        { id: 1, date: '2024-10-12', time: '18:00', status: '已结束' },
        { id: 2, date: '2024-10-15', time: '19:00', status: '已结束' },
        // 添加更多数据
      ].filter(schedule => new Date(schedule.date) >= oneWeekAgo && schedule.status === '已结束');
  
      // 确保数据被设置到schedules数组中
      this.setData({ schedules: schedulesData });
    },
  
    // 查看队员信息
    viewTeamMembers: function(e) {
      const scheduleId = e.currentTarget.dataset.id;
  
      // 模拟获取该拼场的队员信息
      const membersData = [
        { studentId: '123456', studentName: '张三' },
        { studentId: '654321', studentName: '李四' }
        // 添加更多队员信息
      ];
  
      // 确保数据被设置到selectedMembers数组中
      this.setData({ selectedMembers: membersData });
    },
  
    // 跳转到评价页面
    goToEvaluation: function(e) {
      const studentId = e.currentTarget.dataset.id;
      wx.navigateTo({
        url: `/pages/3-evaluation/evaluation?studentId=${studentId}`
      });
    }
  });