import './css/App.css'
import InputBar from './InputBar'
import ChatWindow from './ChatWindow'
import { useEffect, useState } from 'react'
import SideBar from './SideBar'
import { v4 as uuidv4 } from 'uuid';
import Login from './Login'
import Register from './Register'
export default function App(){
  const [messages,setMessages]=useState(()=>{
    const currentMessage=localStorage.getItem('current-message');
    return currentMessage ? JSON.parse(currentMessage) : [];
  })
  const [showRegister,setShowRegister]=useState(false);
  const [user, setUser] = useState(()=>{
    const stored=localStorage.getItem('user')
    return stored?JSON.parse(stored):null;
  })
  const [typing,setTyping]=useState(false)
  const [sessionID] = useState(() => {
    const existing = localStorage.getItem('session_id')
    if (existing) return existing
    const newID = uuidv4()
    localStorage.setItem('session_id', newID)
    return newID
  });
  const onLogin=(data)=>{
    setUser(data);
  };
  const [readingHistory,setreadingHistory]=useState([])
  const onFileUpload=(data)=>{
    setreadingHistory(data)
  }
  useEffect(()=>{
    localStorage.setItem('current-message',JSON.stringify(messages))
  },[messages]);
  const onSend=(content)=>{
    const newMessage = {
        id: messages.length + 1,
        role: "user",
        content: content,
        timestamp: Date.now()
    }
  setMessages([...messages,newMessage])
  setTyping(true)
  fetch('http://localhost:8000/chat',{
    method:"POST",
    headers:{"Content-Type":"application/json","Authorization": `Bearer ${localStorage.getItem('token')}`},
    body:JSON.stringify({message:content,session_id:sessionID,reading_history: readingHistory})
  }).then(res=>res.json()).then(data=>{
    const aiMessage={
      id:messages.length+2,
      role:"assistant",
      content:data.response,
      timestamp:Date.now()
    }
    setMessages(prev=>[...prev,aiMessage])
  }).then(()=>setTyping(false)).catch(()=>setTyping(false))
  }
  const onNewChat=()=>{
    setMessages([]);
    setreadingHistory([]);
    localStorage.removeItem('session_id')
    localStorage.removeItem('current-message')
  }
  const onLogout=()=>{
    setUser(null);
    localStorage.removeItem('token');
    localStorage.removeItem('user')
    setreadingHistory([])
    setMessages([])
  }
  if (!user && !showRegister) return <Login onLogin={onLogin} onSwitch={()=>setShowRegister(true)} />
  if (!user && showRegister) return <Register onLogin={onLogin} onSwitch={()=>setShowRegister(false)}/>
  return(
    <div className='grid-container'>
    <div className='sidebar'><SideBar onNewChat={onNewChat} currentUser={user?.name} onLogout={onLogout}/></div>
    <div className='main-content'>
      <div className='chat-window'><ChatWindow messages={messages} username={user?.name} typing={typing} /></div> 
      <div className='input-bar'><InputBar onSend={onSend} onFileUpload={onFileUpload}/></div>
    </div>
    </div>
  )
}
