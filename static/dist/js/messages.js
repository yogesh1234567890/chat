let input_message = $("#chat-message-input");
let message_body = $(".maa");
let send_message_form = $("#send-message-form");
const USER_ID = $("#logged-in-user").val();
// let loc = window.location;
// let wsStart = "ws://";

var remoteRTCMessage;
var iceCandidatesFromCaller = [];
var alreadyConnected = false;

var our_video = document.getElementById("local-video");
var remote_video = document.getElementById("remote-video");


// let endpoint = wsStart + loc.host + loc.pathname
let endpoint = "ws://localhost:8000/ws/chat/1/";

var socket = new WebSocket(endpoint);

var peerConn
var screenStream

function newMessage(message, sent_by_id, thread_id) {
  console.log("newMessage");
  console.log(message);
  console.log(sent_by_id);
  console.log(thread_id);
  if ($.trim(message) === "") {
    return false;
  }
  let message_element;
  let chat_id = "chat_" + thread_id;
  if (sent_by_id == USER_ID) {
    message_element = `

        <div class="message me">
        <div class="text-main">
            <div class="text-group me">
                <div class="text me">
                    <p>${message}</p>
                </div>
            </div>
        </div>
    </div>
        `;
  } else {
    message_element = `
        <div class="message">
        <div class="text-main">
            <div class="text-group">
                <div class="text">
                    <p>${message}</p>
                </div>
            </div>
        </div>
    </div>
        `;
  }

  let message_body = $('.messages-wrapper[chat-id="' + chat_id + '"] .maa');
  message_body.append($(message_element));
  message_body.animate(
    {
      scrollTop: $(document).height(),
    },
    100
  );
  input_message.val(null);
}

socket.onopen = async function (e) {
  send_message_form.on("submit", function (e) {
    e.preventDefault();
    let message = input_message.val();
    let send_to = get_active_other_user_id();
    let thread_id = get_active_thread_id();

    let data = {
      message: message,
      sent_by: USER_ID,
      send_to: send_to,
      thread_id: thread_id,
      msg_type: "text_message",
    };
    data = JSON.stringify(data);
    socket.send(data);
    $(this)[0].reset();
    let is_video = false;
    // newMessage(message, USER_ID, thread_id, is_video);
  });
};

socket.onmessage = async function (e) {
  console.log("message", e);
  let data = JSON.parse(e.data);
  console.log(data);
  // if(data.text.type =="chat_message"){
  // let parsed = JSON.parse(data.text.text);
  // let sent_by_id = parsed.sent_by;
  // let thread_id = parsed.thread_id;
  // let message = parsed.message;
  // let is_video = false;
  // newMessage(message, sent_by_id, thread_id, is_video);
  // }
  // else{
  message_fun(e);
  // }
};

socket.onerror = async function (e) {
  //console.log("error", e);
};

socket.onclose = async function (e) {
  //console.log("close", e);
};



$(".contact-li").on("click", function () {
  $(".contacts .active").removeClass("active");
  $(this).addClass("active");

  // message wrappers
  let chat_id = $(this).attr("chat-id");

  $(".messages-wrapper.is_active").removeClass("is_active");
  $('.messages-wrapper[chat-id="' + chat_id + '"]').addClass("is_active");
});

function get_active_other_user_id() {
  let other_user_id = $(".messages-wrapper.is_active").attr("other-user-id");
  other_user_id = $.trim(other_user_id);
  return other_user_id;
}

function get_active_thread_id() {
  let chat_id = $(".messages-wrapper.is_active").attr("chat-id");
  let thread_id = chat_id.replace("chat_", "");
  return thread_id;
}

var localStream = new MediaStream
var remoteStream = new MediaStream

var our_video = document.getElementById("local-video");
var remote_video = document.getElementById("remote-video");


//new codess from here
async function message_fun(e) {
  const data = JSON.parse(e.data);
  if(data.text){
  if(data.text.type =="chat_message"){
  let parsed = JSON.parse(data.text.text);
  let sent_by_id = parsed.sent_by;
  let thread_id = parsed.thread_id;
  let message = parsed.message;
  let is_video = false;
  newMessage(message, sent_by_id, thread_id, is_video);
  }
}
  else if (data.msg_type === "offer") {
    if (data.fromUser !== USER_ID) {
      //when other called you

      var calling = `${data.fromUser} is calling`;
      remoteRTCMessage = data.offer;
      isVideo = data.is_video;
      console.log('answer isVideo', isVideo)
      console.log("alreadyConnected", alreadyConnected);

      if (alreadyConnected) {
        peerConn.setRemoteDescription(
          new RTCSessionDescription(remoteRTCMessage)
        );
        //console.log("offer setRemoteDescription from alreadyConnected");

        const answer = await peerConn.createAnswer();
        // //console.log("offer created", answer);

        await peerConn.setLocalDescription(answer);
        // //console.log("offer setLocalDescription");

        //to send a answer
        socket.send(
          JSON.stringify({
            msg_type: "answer",
            // fromUser: fromUser,
            // toUser: toUser,
            fromUser:USER_ID,
            toUser: get_active_other_user_id(),
            answer: answer,
          })
        );
        // //console.log("send answer");
      } else {
        //show answer button 
      //   $(".messages-wrapper.hide.is_active").removeClass("is_active");
      //   $("#chat" + $(this).attr("name")).hide();
      // $("#call").css("display","block");
      // $(".textbox").hide();

        document.getElementById("answer_call").innerHTML = calling;
        document.getElementById("answer_call").style.display = "inline";
      }
    }
  } 
  else if (data.msg_type === "answer") {
    if (data.fromUser !== "{{request.user.username}}") {
      //when other accept our call

      remoteRTCMessage = data.answer;

      await peerConn.setRemoteDescription(
        new RTCSessionDescription(remoteRTCMessage)
      );
      // //console.log("offer setRemoteDescription");
      // //console.log("Call Started. They Answered");
    }
  } 
  else if (data.msg_type === "candidate") {
    if (data.fromUser !== "{{request.user.username}}") {
      try {
        if (peerConn) {
          // //console.log("ICE candidate Added");
          // //console.log(data.candidate)
          data.candidate && (await peerConn.addIceCandidate(data.candidate));
        } else {
          // //console.log("ICE candidate Pushed");
          iceCandidatesFromCaller.push(data.candidate);
        }
      } catch (e) {
        // console.error('Error adding received ice candidate', e);
      }
    }
  } 
  else if (data.msg_type === "stop") {
    if (data.fromUser !== "{{request.user.username}}") {
      // //console.log('stop');
      await stopCall((is_send = false));
    }
  } 
}

async function get_media(is_video = false, is_screen = false) {
  if (!is_screen) {
    //console.log("getting media");
    isVideo = is_video;
    // document.getElementById("mute_video").innerHTML = isVideo == true ? "Stop Video" : "Video";

    await navigator.mediaDevices
      .getUserMedia({
        video: is_video,
        audio: true,
      })
      .then((stream) => {
        localStream = stream;
        our_video.srcObject = stream;
        our_video.onloadeddata = () => {
          our_video.play();
        };
        //console.log("streaming");
      }),
      (e) => {
        alert("getUserMedia() error: " + e.name);
      };
  } else if (is_screen) {
    await navigator.mediaDevices
      .getDisplayMedia({
        video: {
          cursor: "always",
        },
        audio: true,
      })
      .then((stream) => {
        screenStream = stream;
        our_video.srcObject = stream;
        our_video.onloadeddata = () => {
          our_video.play();
        };
        //console.log("screening");
      }),
      (e) => {
        alert("getUserMedia() error: " + e.name);
      };
  }
}

async function creatertcpeer() {
  peerConn = new RTCPeerConnection(iceServers);
  //console.log("RTCPeerConnection created");

  peerConn.addEventListener("track", async (event) => {
    remoteStream = event.streams[0];
    remote_video.srcObject = remoteStream;
  });

  // Listen for local ICE candidates on the local RTCPeerConnection
  peerConn.addEventListener("icecandidate", (event) => {
    if (event.candidate) {
      //to send a candidate
      // // //console.log("Send Call");
      socket.send(
        JSON.stringify({
          msg_type: "candidate",
          fromUser: USER_ID,
          toUser: get_active_other_user_id(),
          candidate: event.candidate,
        })
      );
      // //console.log("send candidate");
    }
  });
}

let iceServers = {
  iceServers: [{ urls: "stun:stun.l.google.com:19302" }],
};

async function call(isVideo, to, thread) {
  // message_fun();
  isVideo = isVideo;
  //console.log("call isVideo", isVideo);
  document.getElementById("video-call-div").style.display = "inline"
  await get_media((is_video = isVideo));
  alreadyConnected = true;

  await creatertcpeer();
  audioSender = peerConn.addTrack(localStream.getAudioTracks()[0], localStream);

  if (is_video) {
    videoSender = peerConn.addTrack(
      localStream.getVideoTracks()[0],
      localStream
    );
  }

  const offer = await peerConn.createOffer();
  //console.log("offer created");

  await peerConn.setLocalDescription(offer);
  //console.log("offer setLocalDescription");
  // //to send a call

  socket.send(
    JSON.stringify({
      msg_type: "offer",
      fromUser: USER_ID,
      toUser: to,
      thread_id: thread,
      offer: offer,
      is_video: is_video,
    })
  );

  // //console.log("send offer")
}

async function answer(video) {
  document.getElementById("video-call-div").style.display = "inline"

  await get_media(is_video=video)
  alreadyConnected = true
  //console.log('alreadyConnected', alreadyConnected)

  await creatertcpeer();
  audioSender = peerConn.addTrack(localStream.getAudioTracks()[0], localStream)

  if(isVideo){
      videoSender = peerConn.addTrack(localStream.getVideoTracks()[0], localStream)
  };

  peerConn.setRemoteDescription(new RTCSessionDescription(remoteRTCMessage));
  // //console.log("offer setRemoteDescription");

  if (iceCandidatesFromCaller.length > 0) {
      //I am having issues with call not being processed in real world (internet, not local)
      //so I will push iceCandidates I received after the call arrived, push it and, once we accept
      //add it as ice candidate
      //if the offer rtc message contains all thes ICE candidates we can ingore this.
      for (let i = 0; i < iceCandidatesFromCaller.length; i++) {
          //
          let candidate = iceCandidatesFromCaller[i];
          // //console.log("ICE candidate Added From queue");
          try {
              await peerConn.addIceCandidate(candidate)
          } catch (error) {
              // //console.log(error);
          }
      }
      iceCandidatesFromCaller = [];
      // //console.log("ICE candidate queue cleared");
  }

  const answer = await peerConn.createAnswer();
  // //console.log("offer created", answer);

  await peerConn.setLocalDescription(answer);
  // //console.log("offer setLocalDescription");

  //to send a answer
  socket.send(JSON.stringify({
      msg_type: 'answer',
      fromUser: USER_ID,
      toUser:get_active_other_user_id(),
      answer: answer
  }));
  //console.log("send answer");
}
