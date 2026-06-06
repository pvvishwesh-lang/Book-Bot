import MessageBubbles from './MessageBubbles'
import {useRef,useEffect} from 'react'
import './css/ChatWindow.css'
import TypingIndicator from './TypingIndicator'


export default function ChatWindow({messages,username,typing}){
    const containerRef=useRef()
    const bottomRef=useRef()
    
    useEffect(()=>{
        setTimeout(() => {
            const lastMessage = messages[messages.length - 1]
            const isAssistant = lastMessage?.role === 'assistant'
            const isatBottom=containerRef.current.scrollHeight-containerRef.current.scrollTop-containerRef.current.clientHeight<50
            if (isAssistant || isatBottom || typing){
                bottomRef.current?.scrollIntoView({behavior:"smooth"});
            }
             }, 100)
    },[messages,typing]);
    return(
        <div ref={containerRef} className='message-bubble-container'>
            {messages.length===0?(<div className="empty-state"><h2 className='clear-state-header'>Hi {username}. What book are you looking for?</h2><p className='clear-state-paragraph'>Ask me for recommendations or books similar to ones you love</p> </div>):(<div className='messages-inner'>{messages.map((data)=>(
                <MessageBubbles key={data.id} message={data}/> 
            ))}
            {typing&&<TypingIndicator/>}
            <div ref={bottomRef} className='bottom-container'/>
            </div>
            )}
        </div>
        
    )
}