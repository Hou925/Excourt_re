const app = getApp();
const utils = require("../../utils/util");
const {BASE_URL} = require('../../utils/config.js');

Page({
    data: {
        inputValue: "",
        time: 0,
        chatList: [], // 用于存储聊天记录
        my_avatarUrl:"",
        friend_avatarUrl: "",
        sender_id:0,
        receiver_id:0
    },

    onLoad: function (options) {
      this.data.sender_id= Number(options.sender_id),
      this.data.receiver_id= Number(options.receiver_id)
      this.setData({sender_id:options.sender_id,receiver_id:options.receiver_id})
      //console.log(this.data.sender_id)
      this.getmyUrl();
      this.getfriendUrl();
      this.getChatList();
      //console.log(this.data.chatList)
    },

    onShow: function () {
      this.getmyUrl();
      this.getfriendUrl();
      this.getChatList();
    },

    publishMessage() {
        if (this.data.inputValue == "") {
            wx.showToast({
                icon: "none",
                title: '不能发送空消息',
            });
            return;
        }

        // 模拟发送消息到聊天记录并显示
        let msg = {
            sender_id: this.data.sender_id,
            receiver_id: this.data.receiver_id,
            message_sent: this.data.inputValue,
            message_type: 'text' 
        };
        //console.log(msg)
        // 更新聊天记录
        wx.request({
          url: `${BASE_URL}/chat/send`,
          method: 'POST',
          header: {
            'Content-Type': 'application/json' // 确保有这个头部
          },
          data: {
            Sender_id: msg.sender_id,
            Receiver_id: msg.receiver_id,
            Message_sent: msg.message_sent,
            Message_type:'text',
          },
          success: (res) => {
              if (res.data.status === 'success') {
                  console.log(res.data.message)
              } else {
                  wx.showToast({
                      title: res.data.message || '发送失败',
                      icon: 'none'
                  });
              }
          },
          fail: (err) => {
              wx.showToast({
                  title: '请求失败',
                  icon: 'none'
              });
          }
      });
      let chatList = this.data.chatList;
      
      chatList.push(msg);
        this.setData({
            chatList: chatList,
            inputValue: ''
        });

        wx.showToast({
            title: '发送成功',
        });

        this.setData({
            scrollLast: "toView"
        });
    },

    //发送图片
    sendPhoto(){
      // 打开选择图片界面的逻辑
      wx.chooseMedia({
        count:1,
        mediaType:['image'],
        sourceType:['album','camera'],
        camera:'back',
        success: (res) => {
          const tempFilePath = res.tempFiles[0].tempFilePath;
          wx.showLoading({
            title: '正在上传图片',mask:true
          })
          this.uploadImage(tempFilePath);
        }
      });
    },
    uploadImage(fp){
      wx.uploadFile({
        filePath: fp,
        name: 'photo',
        url: `${BASE_URL}/chat/sendphoto`,
        formData:{
          Sender_id: this.data.sender_id,
          Receiver_id: this.data.receiver_id,
        },
        success:(res)=>{
          wx.hideLoading();
          console.log(res.data);
        },
        fail:(err)=>{console.log(err)
          wx.hideLoading();
          wx.showToast({
            title: '上传失败',
            icon: 'none'
          });
        }
      })
    },

    handleInput(e) {
        clearTimeout(this.data.time);
        var that = this;
        this.data.time = setTimeout(() => {
            that.getInputValue(e.detail.value);
        }, 200);
    },

    getInputValue(value) {
        this.setData({
            inputValue: value
        });
    },

    getChatList() {
      //console.log(this.data.sender_id)
      //console.log(this.data.receiver_id)
      wx.request({
        url: BASE_URL + '/chat/history',
        method: 'POST',
        header: {
          'Content-Type': 'application/json' // 确保有这个头部
        },
        data: {
          user_id: this.data.sender_id,
          contact_id:this.data.receiver_id
        },
        success: (res) => {
            if (res.data.status === 'success') {
                // console.log(res.data.data)
                this.getUrl(res.data.data)
                //console.log(this.data.chatList)
            } else {
                wx.showToast({
                    title: res.data.message || '获取聊天记录失败',
                    icon: 'none'
                });
            }
        },
        fail: (err) => {
            wx.showToast({
                title: '请求失败',
                icon: 'none'
            });
        }
    });
    },
    getUrl(chaL) {
      // 1. 先显示所有消息（text和image都显示，只是image没有url暂时不显示图片）
      this.setData({ chatList: chaL });
      console.log('当前chatList:', this.data.chatList);

      // 2. 再异步给每个image补url
      chaL.forEach((item, idx) => {
        if (item.message_type === 'image') {
          console.log(item.conversation_id + '.jpg')
          wx.request({
            url: BASE_URL + '/upload/find_code',
            method: 'POST',
            header: {
              'Content-Type': 'application/json' // 确保有这个头部
            },
            data: { con_id: item.conversation_id + '.jpg'},
            success: (res) => {
              if (res.statusCode == 200) {
                let chatList = this.data.chatList;
                chatList[idx].url = res.data.imageUrl;
                this.setData({ chatList });
              }
            },
            fail: (err) => { console.error("Failed to QRcode", err); }
          });
        }
      });
    },

    getmyUrl(){
            wx.request({
              url: `${BASE_URL}/upload/find_profile`,
              method:'POST',
              data:{student_id:this.data.sender_id.toString()+'.png'},
              success:(res)=>{
                if(res.statusCode==200){
                this.setData({my_avatarUrl:res.data.imageUrl})
                //console.log(this.data.my_avatarUrl)
    }
              },
              fail:(err)=>{console.error("Failed to fetch lost and found items:", err);}
            })
    },
    imae(e){console.log(e)},
    imal(l){console.log(l)},
    getfriendUrl(){
            wx.request({
              url: `${BASE_URL}/upload/find_profile`,
              method:'POST',
              data:{student_id:this.data.receiver_id.toString()+'.png'},
              success:(res)=>{
                if(res.statusCode==200){
                this.setData({friend_avatarUrl:res.data.imageUrl})
                //console.log(this.data.friend_avatarUrl)
    }
              },
              fail:(err)=>{console.error("Failed to fetch lost and found items:", err);}
            })
    }


});