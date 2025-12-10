Page({
    data: {
      student_id:'',
      student_name:'',
      current: 0,
      indicatorDots: true,
      autoplay: true,
      circular: true,
      interval: 3000,
      duration: 500,
      vertical: false,
      previousMargin: 0,
      nextMargin: 0,
      background: [
        '/images/ad.png',
        '/images/ad.png',
        '/images/logo.png',
        '/images/logo.png'
      ],//图片路径
  
      //底部导航栏data，在pagePath处修改要跳转到的界面路由
      selected: 0,
      color: "#7A7E83",
      selectedColor: "#3cc51f",
      currentTime: '',
      pageNameMap: {
        "首页": "/pages/index/index",
        "球场视图": "/pages/1-court-view/court-view",
        "交换区": "/pages/2-exchange/index",
        "失物招领": "/pages/4-index/indexLost",
        "发布球场": "/pages/3-publishCourt/publishCourt",
        "处理球场": "/pages/3-handleCourts/handleCourts",
        "申请球场": "/pages/3-applyCourt/applyCourt",
        "申请详情": "/pages/3-applyDetails/applyDetails",
        "评价队伍": "/pages/3-evaluateTeam/evaluateTeam",
        "评价": "/pages/3-evaluation/evaluation",
        "发布失物": "/pages/4-publishLost/publishLost",
        "我的信息": "/pages/6-Me/6-Me",
        "历史记录": "/pages/6-historyRecord/historyRecord",
        "操作记录": "/pages/6-operationRecord/6-operationRecord",
        "好友管理": "/pages/6-buddyManagement/buddyManagement",
        "聊天": "/pages/5-chating/chating",
      },
      greeting: '', // 用于存储问候语
      
      searchTerm: '',
      searchResults: []
      },
      onChange(e) {
        this.setData({
          current: e.detail.current
        });
      },
      onTransition(e) {
        //console.info('Transition Event:', e.detail);
      },
      onAnimationfinish(e) {
        //console.info('Animation Finish Event:', e.detail);
      },
      navFromIndex(e) {
        const data = e.currentTarget.dataset
        const url = data.path
        //console.log(url);
        this.setData({
          selected: data.index
        })
        wx.navigateTo({
          url: url+'?student_id='+this.data.student_id+'&student_name='+this.data.student_name,
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
    onShow(){
      this.setData(
        {selected: 0}
      );
    },
    onLoad() {
      this.updateTime();
      setInterval(this.updateTime, 1000);
      this.setData({
        greeting: this.getGreeting() // 设置问候语
      });
      //this.fetchLostAndFoundItems(); 
      this.getNameId()
    },
    getNameId(){
      wx.getStorage({key: 'student_id',success: (res) => {
          //console.log('获取到学号:', res.data);
          this.setData({student_id: res.data});},
        fail: () => {wx.showToast({title: '未登录或学号未找到',icon: 'none'});}});
      wx.getStorage({key: 'student_name',success: (res) => {
          //console.log('获取到姓名:', res.data);
          this.setData({student_name: res.data });},
        fail: () => {wx.showToast({title: '未登录或学号未找到',icon: 'none'});}});
    },
    updateTime() {
      const now = new Date();
      const hours = now.getHours().toString().padStart(2, '0');
      const minutes = now.getMinutes().toString().padStart(2, '0');
      const seconds = now.getSeconds().toString().padStart(2, '0');
      this.setData({
        currentTime: `${hours}:${minutes}:${seconds}`
      });
    },
    fetchLostAndFoundItems() {
      wx.request({
        url: 'https://example.com/api/lost-and-found', // 替换后台API地址
        method: 'GET',
        success: (res) => {
          if (res.data && res.data.items) {
            this.setData({
              lostAndFoundItems: res.data.items
            });
          }
        },
        fail: (err) => {
          console.error("Failed to fetch lost and found items:", err);
        }
      });
    },
    onInput: function(e) {
      this.setData({
        searchTerm: e.detail.value
      });
      if (e.detail.value) {
        this.executeSearch();
      }
    },
    executeSearch: function() {
      const searchTerm = this.data.searchTerm;
    const pageNameMap = this.data.pageNameMap;
    const results = Object.keys(pageNameMap).filter(name => name.includes(searchTerm));
    this.setData({
      searchResults: results
    });
  },
    onSearchResultTap: function(e) {
      const url = e.currentTarget.dataset.url;
      wx.navigateTo({
        url: url
      });
    },
    getGreeting: function() {
      const now = new Date();
      const hour = now.getHours();
      if (hour < 12) {
        return '早上好！';
      } else if (hour < 18) {
        return '下午好！';
      } else {
        return '晚上好！';
      }
    },
    navigateToExCourtTeam: function() {
      wx.navigateTo({
        url: '/pages/ExCourtTeam/ExCourtTeam'
      });
    },
  });